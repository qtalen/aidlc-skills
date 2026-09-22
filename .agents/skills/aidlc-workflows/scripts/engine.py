#!/usr/bin/env python3
"""AI-DLC runtime orchestration engine.

Judgment belongs to the LLM, precision belongs to the tool, decisions belong
to the human. This engine owns the workflow's deterministic mechanics:

- cross-stage routing (``next`` — pure read, single directive),
- the stage state machine (``report`` — the ONLY transition entry point),
- deterministic state creation (``init``),
- changing course (``jump`` / ``jump --fresh``),
- state integrity (State Digest + audit cross-check, ``rebase``),
- the bootstrap probe / session-recovery data source (``status``),
- in-flight parking (``park`` — an annotation, never a transition; it
  keeps marks and current unchanged, writes a handoff note, and never
  touches the audit log).

The engine reads ONLY the author-time compiled artifact
``scripts/data/stage-graph.json`` (produced by ``scripts/generate.py``). It
never parses stage frontmatter and never parses ``condition`` prose.

Pure Python 3.8+ standard library. No third-party dependencies.

Usage:
    python engine.py <subcommand> [--workspace <path>]

Subcommands:
    status    bootstrap probe + recovery data (read-only)
    init      deterministically create aidlc-docs state/audit
    next      route: emit exactly one directive (read-only)
    report    record a stage transition (the only write entry)
    park      park in-flight work with a handoff note (annotation)
    jump      change course: --stage <slug> | --fresh
    rebase    re-baseline the State Digest after human confirmation

Every invocation prints exactly one JSON object to stdout. Exit code 0 on
success, 1 whenever the JSON object is ``{"kind": "error", ...}`` (including
usage errors and unexpected internal failures).
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(SKILL_ROOT, "scripts", "data", "stage-graph.json")

STATE_VERSION = 1

DOCS_DIR = "aidlc-docs"
STATE_FILE = os.path.join(DOCS_DIR, "aidlc-state.md")
AUDIT_FILE = os.path.join(DOCS_DIR, "audit.md")
HANDOFF_FILE = os.path.join(DOCS_DIR, "handoff.md")

BEGIN_MARKER = "<!-- BEGIN ENGINE-STATE"
END_MARKER = "<!-- END ENGINE-STATE -->"

MARK_PENDING = " "
MARK_DONE = "x"
MARK_SKIPPED = "S"
MARK_REJECTED = "R"
MARK_REVISED = "?"

RESULTS = ("completed", "approved", "rejected", "revised", "skipped")

# Produce entries that are the engine's own files: guaranteed to exist after
# init and carry zero signal for artifact sensors (workspace-detection is
# therefore naturally exempt from both probes).
ENGINE_OWNED_PRODUCES = ("aidlc-state.md", "audit.md")

PARK_NOTE_MAX = 300

HANDOFF_HEADER = (
    "# AI-DLC Handoff Notes\n"
    "\n"
    "Engine-owned park notes (append-only; never hand-edit). The latest\n"
    "entry surfaces via `engine.py status` -> resume_note.\n"
)

# Audit event vocabulary (appended by the engine only).
EV_CREATED = "STATE_CREATED"
EV_REBASELINED = "STATE_REBASELINED"
EV_JUMPED = "STAGE_JUMPED"
EV_FRESH = "WORKFLOW_FRESH"
EV_FOR_RESULT = {
    "completed": "STAGE_COMPLETED",
    "approved": "STAGE_APPROVED",
    "rejected": "STAGE_REJECTED",
    "revised": "STAGE_REVISED",
    "skipped": "STAGE_SKIPPED",
}

MARK_RE = re.compile(r"^- \[( |x|S|R|\?)\] ([a-z0-9][a-z0-9-]*)\s*$")
DIGEST_RE = re.compile(r"^sha256: ([0-9a-f]{64})\s*$")
PARKED_RE = re.compile(
    r"^- \*\*Last Parked\*\*: ([a-z0-9][a-z0-9-]*) — (.+)$"
)

# Audit line grammar (shared by every audit parser in this module; the
# entry format itself is written by _audit_append).
AUDIT_SECTION_RE = re.compile(r"^##\s+Engine Transition\s*$")
AUDIT_TIMESTAMP_RE = re.compile(r"^\*\*Timestamp\*\*:\s*(.+)$")
AUDIT_EVENT_RE = re.compile(r"^\*\*Event\*\*:\s*(.+)$")
AUDIT_STAGE_RE = re.compile(r"^\*\*Stage\*\*:\s*(.+)$")
AUDIT_REASON_RE = re.compile(r"^\*\*Reason\*\*:\s*(.+)$")


class EngineError(Exception):
    """An expected, reportable failure (emitted as an error JSON object)."""

    def __init__(self, code, message, hint):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


# ---------------------------------------------------------------------------
# Small IO helpers
# ---------------------------------------------------------------------------


def _read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_text_atomic(path, text):
    """Write ``text`` to ``path`` atomically (temp file + os.replace)."""
    directory = os.path.dirname(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    fd, tmp = tempfile.mkstemp(
        prefix=".aidlc-engine-", dir=directory or None, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _append_text(path, text):
    with open(path, "a", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _now_iso():
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _posix(path):
    return path.replace("\\", "/")


# ---------------------------------------------------------------------------
# Stage graph (compile artifact — the only data the engine reads)
# ---------------------------------------------------------------------------


def load_graph():
    if not os.path.isfile(GRAPH_PATH):
        raise EngineError(
            "graph-missing",
            "The compiled stage graph is missing: %s"
            % _posix(os.path.relpath(GRAPH_PATH, SKILL_ROOT)),
            "Run the author-time generator once: "
            "python <skill>/scripts/generate.py",
        )
    try:
        with open(GRAPH_PATH, "r", encoding="utf-8") as handle:
            graph = json.load(handle)
    except (ValueError, OSError) as exc:
        raise EngineError(
            "graph-invalid",
            "The compiled stage graph could not be read: %s" % exc,
            "Regenerate it: python <skill>/scripts/generate.py",
        )
    return graph


def default_scope(graph):
    for scope in graph["scopes"]:
        if scope.get("default"):
            return scope["name"]
    return graph["scopes"][0]["name"]


def scope_depth(graph, name):
    for scope in graph["scopes"]:
        if scope["name"] == name:
            return scope["depth"]
    return "standard"


# ---------------------------------------------------------------------------
# State file model
# ---------------------------------------------------------------------------


class Plan(object):
    """Model-owned, engine-read routing inputs from Execution Plan Summary."""

    def __init__(self, scope, depth, execute, skip):
        self.scope = scope
        self.depth = depth
        self.execute = execute  # set of slugs (empty = none declared)
        self.skip = skip  # set of slugs


class State(object):
    def __init__(self):
        self.exists = False
        self.legacy = False
        self.corrupt = False
        self.marks = {}  # slug -> MARK_*
        self.plan = None
        self.region_start = None  # line index of BEGIN marker
        self.region_end = None  # line index of END marker
        self.lines = []
        self.digest = None
        self.parked = None  # (slug, note) from the Last Parked line, or None


def _state_path(workspace):
    return os.path.join(workspace, STATE_FILE)


def _audit_path(workspace):
    return os.path.join(workspace, AUDIT_FILE)


def _slug_list(value, known):
    """Parse a comma-separated slug list; strips ``(reason)`` annotations.

    ``known`` is the registry of valid stage slugs (from the stage graph).
    A reason annotation may itself contain commas (e.g.
    ``infrastructure-design (pure frontend, no infra)``), so a raw comma
    split can shear one entry in two. Fragments that do not resolve to a
    known slug after stripping a trailing ``(reason)`` are greedily
    re-joined with the following fragments until they do. A leftover
    buffer at the end is emitted as-is so the caller's registry validation
    still rejects it.
    """
    result = []
    buf = ""
    for part in value.split(","):
        fragment = part.strip()
        if not fragment:
            continue
        buf = fragment if not buf else buf + ", " + fragment
        candidate = re.sub(r"\s*\([^)]*\)\s*$", "", buf).strip()
        if candidate and candidate.lower() != "none":
            if candidate in known:
                result.append(candidate)
                buf = ""
            continue
        # Candidate is empty or the "none" sentinel: this entry is complete.
        buf = ""
    if buf:
        candidate = re.sub(r"\s*\([^)]*\)\s*$", "", buf).strip()
        if candidate and candidate.lower() != "none":
            result.append(candidate)
    return result


def _is_placeholder(value):
    return "[" in value or "]" in value


def _parse_plan(graph, lines):
    """Read the model-owned Execution Plan Summary structured lines."""
    scope = None
    depth = None
    execute = set()
    skip = set()
    known = {stage["slug"] for stage in graph["stages"]}
    in_section = False
    header_present = False
    stray_plan_key = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped == "## Execution Plan Summary"
            if in_section:
                header_present = True
            continue
        m = re.match(r"^- \*\*([A-Za-z ]+)\*\*:\s*(.*)$", stripped)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if (key in ("Stages to Execute", "Stages to Skip")
                and not _is_placeholder(value) and not in_section):
            # A plan-shaped line outside the exact section header. Legal as
            # an informational copy while the exact header exists; a routing
            # hazard when it does not.
            stray_plan_key = key
        if not in_section:
            continue
        if _is_placeholder(value):
            continue
        if key == "Scope":
            scope = value.split()[0] if value.split() else None
        elif key == "Depth":
            depth = value.split()[0] if value.split() else None
        elif key == "Stages to Execute":
            execute = set(_slug_list(value, known))
        elif key == "Stages to Skip":
            skip = set(_slug_list(value, known))
    if stray_plan_key is not None and not header_present:
        raise EngineError(
            "plan-invalid",
            "Found a filled '**%s**' plan line, but the exact "
            "'## Execution Plan Summary' section header is missing (renamed "
            "or mistyped), so routing cannot consume it." % stray_plan_key,
            "Restore the exact section header '## Execution Plan Summary' in "
            "aidlc-docs/aidlc-state.md; the engine reads plan lines only from "
            "that section. Do not rename it.",
        )
    if not scope:
        scope = default_scope(graph)
    if not depth:
        depth = scope_depth(graph, scope)
    for slug in sorted(execute | skip):
        if slug not in known:
            raise EngineError(
                "plan-invalid",
                "Execution Plan Summary references unknown stage slug %r."
                % slug,
                "Fix the 'Stages to Execute' / 'Stages to Skip' lines in "
                "aidlc-docs/aidlc-state.md (slugs are kebab-case stage "
                "identifiers; see scripts/data/stage-graph.json).",
            )
    if scope not in {item["name"] for item in graph["scopes"]}:
        raise EngineError(
            "plan-invalid",
            "Execution Plan Summary names unknown scope %r." % scope,
            "Fix the '**Scope**' line in aidlc-docs/aidlc-state.md; "
            "registered scopes: %s."
            % ", ".join(item["name"] for item in graph["scopes"]),
        )
    return Plan(scope, depth, execute, skip)


def load_state(graph, workspace):
    """Load and parse the state file. Never raises for a missing file."""
    state = State()
    path = _state_path(workspace)
    if not os.path.isfile(path):
        return state
    state.exists = True
    text = _read_text(path)
    state.lines = text.split("\n")
    begin = end = None
    for index, line in enumerate(state.lines):
        if line.startswith(BEGIN_MARKER):
            begin = index
        elif line.startswith(END_MARKER):
            end = index
    if begin is None and end is None:
        state.legacy = True
        return state
    if begin is None or end is None or end <= begin:
        # A marker is present but the region is incomplete or malformed
        # (truncation, deletion, reordering). That is corruption, not a
        # pre-engine file: legacy means NO marker at all.
        state.corrupt = True
        return state
    state.region_start = begin
    state.region_end = end
    for line in state.lines[begin + 1 : end]:
        m = MARK_RE.match(line)
        if m:
            state.marks[m.group(2)] = m.group(1)
            continue
        d = DIGEST_RE.match(line)
        if d:
            state.digest = d.group(1)
            continue
        p = PARKED_RE.match(line)
        if p:
            state.parked = (p.group(1), p.group(2))
    state.plan = _parse_plan(graph, state.lines)
    return state


# ---------------------------------------------------------------------------
# Engine region rendering + State Digest
# ---------------------------------------------------------------------------

PHASE_TITLES = ("inception", "construction", "operations")


def _render_region_lines(graph, marks, current, completed_all, digest,
                         parked=None):
    lines = []
    lines.append("State Version: %d" % STATE_VERSION)
    lines.append("Engine: aidlc-workflows/scripts/engine.py")
    lines.append("")
    lines.append("## Stage Progress")
    for phase in PHASE_TITLES:
        stages = [s for s in graph["stages"] if s["phase"] == phase]
        if not stages:
            continue
        lines.append("")
        lines.append("### %s" % phase)
        for stage in stages:
            lines.append(
                "- [%s] %s" % (marks.get(stage["slug"], MARK_PENDING), stage["slug"])
            )
    lines.append("")
    lines.append("## Current Status")
    if completed_all:
        lines.append("- **Lifecycle Phase**: completed")
        lines.append("- **Current Stage**: -")
        lines.append("- **Status**: Completed")
    else:
        stage = _stage_by_slug(graph, current) if current else None
        lines.append(
            "- **Lifecycle Phase**: %s" % (stage["phase"] if stage else "inception")
        )
        lines.append("- **Current Stage**: %s" % (current or "-"))
        lines.append("- **Status**: Active")
    if parked:
        lines.append("- **Last Parked**: %s — %s" % (parked[0], parked[1]))
    lines.append("")
    lines.append("## Unit Progress")
    lines.append("(reserved — not used in state version %d)" % STATE_VERSION)
    lines.append("")
    lines.append("## State Digest")
    lines.append("sha256: %s" % digest)
    return lines


def _digest_of_region(region_lines):
    """SHA-256 over the engine-owned region, excluding the digest line."""
    payload = []
    for line in region_lines:
        if DIGEST_RE.match(line):
            continue
        payload.append(line.rstrip())
    text = "\n".join(payload).strip("\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _splice_region(state, graph, current, completed_all):
    """Replace the engine region inside the existing file; model parts intact."""
    placeholder = _render_region_lines(
        graph, state.marks, current, completed_all, "0" * 64,
        parked=state.parked,
    )
    digest = _digest_of_region(placeholder)
    region = _render_region_lines(
        graph, state.marks, current, completed_all, digest,
        parked=state.parked,
    )
    new_lines = (
        state.lines[: state.region_start + 1]
        + region
        + state.lines[state.region_end :]
    )
    return "\n".join(new_lines)


# ---------------------------------------------------------------------------
# Integrity
# ---------------------------------------------------------------------------


def _audit_events(audit_text):
    """Yield (event, stage, reason) tuples from engine transition entries.

    Deliberately whole-file (legacy behavior): the integrity cross-check
    accepts any Event-shaped line, confined or not.
    """
    events = []
    event = stage = reason = None
    for line in audit_text.split("\n"):
        stripped = line.strip()
        m = AUDIT_EVENT_RE.match(stripped)
        if m:
            if event:
                events.append((event, stage, reason))
            event, stage, reason = m.group(1).strip(), None, None
            continue
        m = AUDIT_STAGE_RE.match(stripped)
        if m:
            stage = m.group(1).strip()
            continue
        m = AUDIT_REASON_RE.match(stripped)
        if m:
            reason = m.group(1).strip()
    if event:
        events.append((event, stage, reason))
    return events


def _audit_transition_events(audit_text):
    """Engine transition entries as dicts, confined to engine sections.

    Unlike ``_audit_events`` (whole-file, legacy integrity semantics), this
    parser only reads lines inside ``## Engine Transition`` sections, so
    model-owned audit entries (which may quote raw user input containing
    Event-shaped lines) cannot forge recovery data. Timestamp attribution:
    the LAST ``**Timestamp**`` line seen in the section is the event's
    timestamp.
    """
    events = []
    in_section = False
    timestamp = event = stage = reason = None

    def flush():
        if event:
            events.append(
                {
                    "event": event,
                    "stage": stage,
                    "reason": reason,
                    "timestamp": timestamp,
                }
            )

    for line in audit_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section:
                flush()
            in_section = bool(AUDIT_SECTION_RE.match(stripped))
            timestamp = event = stage = reason = None
            continue
        if not in_section:
            continue
        m = AUDIT_TIMESTAMP_RE.match(stripped)
        if m:
            timestamp = m.group(1).strip()
            continue
        m = AUDIT_EVENT_RE.match(stripped)
        if m:
            if event:
                flush()
            event, stage, reason = m.group(1).strip(), None, None
            continue
        m = AUDIT_STAGE_RE.match(stripped)
        if m:
            stage = m.group(1).strip()
            continue
        m = AUDIT_REASON_RE.match(stripped)
        if m:
            reason = m.group(1).strip()
    if in_section:
        flush()
    return events


def _audit_append(workspace, event, stage=None, reason=None, detail=None):
    path = _audit_path(workspace)
    lines = [
        "",
        "## Engine Transition",
        "**Timestamp**: %s" % _now_iso(),
        "**Event**: %s" % event,
        "**Stage**: %s" % (stage or "-"),
        "**Reason**: %s" % (reason or "-"),
    ]
    if detail:
        lines.append("**Detail**: %s" % detail)
    lines.append("")
    lines.append("---")
    lines.append("")
    _append_text(path, "\n".join(lines))


def check_integrity(graph, state, workspace, audit_text=None):
    """Return None when intact, else an EngineError describing the drift.

    ``audit_text`` may be supplied by callers that already read the audit
    log (single-read reuse); None means read it here (historical behavior).
    """
    if not state.exists or state.legacy or state.corrupt:
        return None
    region_lines = state.lines[state.region_start + 1 : state.region_end]
    actual = _digest_of_region(region_lines)
    if state.digest is None or actual != state.digest:
        return EngineError(
            "integrity-violated",
            "The engine-owned region of aidlc-docs/aidlc-state.md does not "
            "match its State Digest (hand-edit detected).",
            "Do not continue. Show this to the user, get explicit "
            "confirmation, then run: python <skill>/scripts/engine.py rebase",
        )
    if audit_text is None:
        audit_path = _audit_path(workspace)
        audit_text = _read_text(audit_path) if os.path.isfile(audit_path) else ""
    events = _audit_events(audit_text)
    # Once a human has confirmed a re-baseline, the pre-rebase history is
    # accepted by definition; cross-checking would make rebase useless.
    rebaselined = any(event == EV_REBASELINED for event, _, _ in events)
    if not rebaselined:
        by_stage = {}
        jumped = False
        for event, stage, _reason in events:
            by_stage.setdefault(stage, set()).add(event)
            if event == EV_JUMPED:
                jumped = True
        for slug, mark in state.marks.items():
            if mark == MARK_PENDING:
                continue
            seen = by_stage.get(slug, set())
            ok = False
            if mark == MARK_DONE:
                ok = bool(seen & {"STAGE_COMPLETED", "STAGE_APPROVED"})
            elif mark == MARK_SKIPPED:
                ok = bool(seen & {"STAGE_SKIPPED"}) or jumped
            elif mark == MARK_REJECTED:
                ok = bool(seen & {"STAGE_REJECTED"})
            elif mark == MARK_REVISED:
                ok = bool(seen & {"STAGE_REVISED"})
            if not ok:
                return EngineError(
                    "integrity-violated",
                    "Stage %r is marked [%s] in aidlc-state.md but the audit "
                    "log has no matching transition entry." % (slug, mark),
                    "Do not continue. Show this to the user, get explicit "
                    "confirmation, then run: "
                    "python <skill>/scripts/engine.py rebase",
                )
    return None


def _require_intact(graph, state, workspace):
    problem = check_integrity(graph, state, workspace)
    if problem is not None:
        raise problem


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def _stage_by_slug(graph, slug):
    for stage in graph["stages"]:
        if stage["slug"] == slug:
            return stage
    return None


def effective_stages(graph, plan):
    """Stages in the routed plan: scope baseline + plan Execute − plan Skip."""
    result = []
    for stage in graph["stages"]:
        slug = stage["slug"]
        if slug in plan.skip:
            continue
        membership = stage.get("scopes", {}).get(plan.scope, "EXECUTE")
        if membership == "SKIP" and slug not in plan.execute:
            continue
        result.append(stage)
    return result


def _is_done(mark):
    return mark in (MARK_DONE, MARK_SKIPPED)


def pending_stages(graph, state):
    plan = state.plan
    return [
        stage
        for stage in effective_stages(graph, plan)
        if not _is_done(state.marks.get(stage["slug"], MARK_PENDING))
    ]


def current_stage(graph, state):
    pending = pending_stages(graph, state)
    return pending[0]["slug"] if pending else None


def _directive_for(graph, state, slug):
    stage = _stage_by_slug(graph, slug)
    plan = state.plan
    pending = pending_stages(graph, state)
    successors = [s["slug"] for s in pending if s["slug"] != slug]
    membership = stage.get("scopes", {}).get(plan.scope, "EXECUTE")
    return {
        "kind": "run-stage",
        "stage": stage["slug"],
        "name": stage["name"],
        "phase": stage["phase"],
        "gate": stage["gate"],
        "stage_file": "references/%s/%s.md" % (stage["phase"], stage["slug"]),
        "produces": stage["produces"],
        "consumes": stage["consumes"],
        "conditional": bool(
            stage["execution"] == "CONDITIONAL" or membership == "CONDITIONAL"
        ),
        "next_stage": successors[0] if successors else None,
    }


# ---------------------------------------------------------------------------
# Session recovery sensors (fail-open)
# ---------------------------------------------------------------------------


def _is_engine_owned_produce(rel):
    return os.path.basename(rel) in ENGINE_OWNED_PRODUCES


def _stage_missing_produces(workspace, stage):
    """Concrete produces of a completed stage that are all missing/empty.

    Asymmetric rule: only N>=2 concrete (non-wildcard) entries qualify, and
    an alert fires only when ALL of them are missing or empty. N=0/1 stages
    are exempt (a single conditionally-absent produce is indistinguishable
    from a genuinely missing one). Returns [] when no alert should fire.
    """
    concrete = [
        rel
        for rel in stage["produces"]
        if "{" not in rel and "*" not in rel and not _is_engine_owned_produce(rel)
    ]
    if len(concrete) < 2:
        return []
    docs = os.path.join(workspace, DOCS_DIR)
    missing = []
    for rel in concrete:
        path = os.path.join(docs, rel)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            missing.append(_posix(os.path.join(DOCS_DIR, rel)))
    return missing if len(missing) == len(concrete) else []


def _stage_resumed_artifacts(workspace, stage):
    """Produce paths of the current stage that already exist on disk.

    Existence is the signal of an interrupted session (half-done work).
    ``{unit-name}`` is translated to ``*`` and globbed; any single match
    counts. Capped at 5 paths. Engine-owned files are excluded.
    """
    docs = _posix(os.path.join(workspace, DOCS_DIR))
    hits = []
    for rel in stage["produces"]:
        if _is_engine_owned_produce(rel):
            continue
        pattern = rel.replace("{unit-name}", "*")
        if "*" in pattern or "?" in pattern or "[" in pattern:
            hits.extend(glob.glob(docs + "/" + pattern))
        else:
            full = docs + "/" + pattern
            if os.path.exists(full):
                hits.append(full)
    unique = []
    for path in sorted(set(hits)):
        rel = os.path.relpath(path, workspace)
        unique.append(_posix(rel))
    return unique[:5]


def _artifact_alerts(graph, state, workspace, current):
    """First-generation artifact findings (D14 finding shape, fail-open).

    Raises nothing: the caller wraps this in try/except and degrades to
    ``alerts_unavailable`` on any unexpected failure.
    """
    alerts = []
    for stage in graph["stages"]:
        if state.marks.get(stage["slug"]) != MARK_DONE:
            continue
        missing = _stage_missing_produces(workspace, stage)
        if missing:
            alerts.append(
                {
                    "type": "missing-produces",
                    "severity": "warning",
                    "subject": stage["slug"],
                    "message": (
                        "Completed stage %r is missing ALL of its declared "
                        "concrete produces: %s. Either the artifacts were "
                        "lost or the stage was reported without producing "
                        "them." % (stage["slug"], ", ".join(missing))
                    ),
                    "action_discipline": "Report to the user; do not "
                    "regenerate or fabricate artifacts.",
                }
            )
    if current:
        stage = _stage_by_slug(graph, current)
        resumed = _stage_resumed_artifacts(workspace, stage)
        if resumed:
            alerts.append(
                {
                    "type": "resumed-artifacts",
                    "severity": "info",
                    "subject": current,
                    "message": (
                        "Files the current stage %r will produce already "
                        "exist (possible half-done work from an interrupted "
                        "session): %s."
                        % (current, ", ".join(resumed))
                    ),
                    "action_discipline": "Read existing files before "
                    "writing; append rather than regenerate (unless in a "
                    "rejected/revised redo — see session-continuity).",
                }
            )
    return alerts


# ---------------------------------------------------------------------------
# State file template (init)
# ---------------------------------------------------------------------------


def _initial_state_text(graph):
    marks = {stage["slug"]: MARK_PENDING for stage in graph["stages"]}
    current = graph["stages"][0]["slug"] if graph["stages"] else None
    placeholder = _render_region_lines(graph, marks, current, False, "0" * 64)
    digest = _digest_of_region(placeholder)
    region = _render_region_lines(graph, marks, current, False, digest)
    lines = [
        "# AI-DLC State Tracking",
        "",
        "## Project Information",
        "- **Project Type**: [Greenfield/Brownfield]",
        "- **Start Date**: [ISO 8601 timestamp]",
        "",
        "## Workspace State",
        "- **Existing Code**: [Yes/No]",
        "- **Reverse Engineering Needed**: [Yes/No]",
        "- **Workspace Root**: [absolute path]",
        "",
        "## Code Location Rules",
        "- **Application Code**: Workspace root (NEVER in aidlc-docs/)",
        "- **Documentation**: aidlc-docs/ only",
        "- **Structure patterns**: See code-generation.md Critical Rules",
        "",
        "## Execution Plan Summary",
        "- **Scope**: [selected at Requirements Analysis]",
        "- **Depth**: [scope default]",
        "- **Stages to Execute**: [filled at Workflow Planning approval]",
        "- **Stages to Skip**: [filled at Workflow Planning approval]",
        "",
        "Reader notes: a new session MUST run `engine.py status` (recovery "
        "briefing) before touching anything; the ENGINE-STATE region below "
        "is engine-owned — never hand-edit it.",
        "",
        BEGIN_MARKER
        + " | do not hand-edit — maintained by scripts/engine.py -->",
    ]
    lines.extend(region)
    lines.append(END_MARKER)
    lines.append("")
    return "\n".join(lines)


AUDIT_HEADER = (
    "# AI-DLC Audit Log\n"
    "\n"
    "Chronological record of user inputs, AI responses, and engine "
    "transitions.\n"
    "Append-only: NEVER overwrite this file.\n"
)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_status(workspace):
    graph = load_graph()
    state = load_state(graph, workspace)
    if not state.exists:
        return {
            "engine": "ok",
            "state_version": STATE_VERSION,
            "workspace": _posix(os.path.abspath(workspace)),
            "state": "none",
            "current_stage": None,
            "scope": None,
            "depth": None,
            "last_completed": None,
            "integrity": "ok",
            "completed": [],
            "remaining": [],
        }
    if state.legacy:
        return {
            "engine": "ok",
            "state_version": STATE_VERSION,
            "workspace": _posix(os.path.abspath(workspace)),
            "state": "legacy",
            "current_stage": None,
            "scope": None,
            "depth": None,
            "last_completed": None,
            "integrity": "ok",
            "completed": [],
            "remaining": [],
            "hint": "A state file without an ENGINE-STATE region predates "
            "the engine. Do not overwrite it silently; confirm with the "
            "user, then Start Fresh (jump --fresh) or migrate manually.",
        }
    if state.corrupt:
        return {
            "engine": "ok",
            "state_version": STATE_VERSION,
            "workspace": _posix(os.path.abspath(workspace)),
            "state": "corrupt",
            "current_stage": None,
            "scope": None,
            "depth": None,
            "last_completed": None,
            "integrity": "violated",
            "completed": [],
            "remaining": [],
            "hint": "aidlc-docs/aidlc-state.md has a partial or malformed "
            "ENGINE-STATE marker region (likely truncated or hand-edited). "
            "Do not overwrite it silently. Restore the missing marker line "
            "from a backup if available; otherwise confirm with the user "
            "and Start Fresh (jump --fresh).",
        }
    audit_path = _audit_path(workspace)
    audit_text = _read_text(audit_path) if os.path.isfile(audit_path) else ""
    integrity = (
        "ok"
        if check_integrity(graph, state, workspace, audit_text=audit_text) is None
        else "violated"
    )
    effective = effective_stages(graph, state.plan)
    done = [
        s["slug"]
        for s in effective
        if _is_done(state.marks.get(s["slug"], MARK_PENDING))
    ]
    remaining = [s["slug"] for s in pending_stages(graph, state)]
    current = remaining[0] if remaining else None
    transitions = _audit_transition_events(audit_text)
    try:
        alerts = _artifact_alerts(graph, state, workspace, current)
        alerts_unavailable = False
    except Exception:  # fail-open: sensors never block the probe itself
        alerts = []
        alerts_unavailable = True
    return {
        "engine": "ok",
        "state_version": STATE_VERSION,
        "workspace": _posix(os.path.abspath(workspace)),
        "state": "completed" if not remaining else "active",
        "current_stage": current,
        "scope": state.plan.scope,
        "depth": state.plan.depth,
        "last_completed": done[-1] if done else None,
        "integrity": integrity,
        "completed": done,
        "remaining": remaining,
        "resume_note": (
            {"stage": state.parked[0], "note": state.parked[1]}
            if state.parked
            else None
        ),
        "recent_events": transitions[-5:],
        "audit_entries": len(transitions),
        "audit_bytes": len(audit_text.encode("utf-8")),
        "artifact_alerts": alerts,
        "alerts_unavailable": alerts_unavailable,
    }


def cmd_init(workspace):
    graph = load_graph()
    path = _state_path(workspace)
    if os.path.isfile(path):
        raise EngineError(
            "state-exists",
            "aidlc-docs/aidlc-state.md already exists — this is an existing "
            "workflow, not a new project.",
            "Resume it instead: run `python <skill>/scripts/engine.py "
            "status` and follow the session-continuity flow. To abandon it: "
            "`python <skill>/scripts/engine.py jump --fresh`.",
        )
    docs = os.path.join(workspace, DOCS_DIR)
    if not os.path.isdir(docs):
        os.makedirs(docs)
    _write_text_atomic(path, _initial_state_text(graph))
    audit = _audit_path(workspace)
    if not os.path.isfile(audit):
        _write_text_atomic(audit, AUDIT_HEADER)
    _audit_append(workspace, EV_CREATED)
    return {
        "kind": "initialized",
        "state_file": _posix(STATE_FILE),
        "audit_file": _posix(AUDIT_FILE),
        "stages": len(graph["stages"]),
    }


def _load_active(graph, workspace):
    state = load_state(graph, workspace)
    if not state.exists:
        raise EngineError(
            "no-state",
            "No aidlc-docs/aidlc-state.md in this workspace.",
            "For a new workflow run: python <skill>/scripts/engine.py init",
        )
    if state.legacy:
        raise EngineError(
            "legacy-state",
            "aidlc-docs/aidlc-state.md predates the engine (no ENGINE-STATE "
            "region).",
            "Confirm with the user, then Start Fresh: "
            "python <skill>/scripts/engine.py jump --fresh",
        )
    if state.corrupt:
        raise EngineError(
            "state-corrupt",
            "aidlc-docs/aidlc-state.md has a partial or malformed "
            "ENGINE-STATE marker region (BEGIN without END, END without "
            "BEGIN, or markers out of order) — likely truncated or "
            "hand-edited.",
            "Restore the missing marker line from a backup if available "
            "(exact line: '<!-- END ENGINE-STATE -->'). If no backup "
            "exists, confirm with the user and Start Fresh: "
            "python <skill>/scripts/engine.py jump --fresh",
        )
    return state


def cmd_next(workspace):
    graph = load_graph()
    state = _load_active(graph, workspace)
    _require_intact(graph, state, workspace)
    slug = current_stage(graph, state)
    if slug is None:
        return {"kind": "done"}
    return _directive_for(graph, state, slug)


def _validate_transition(graph, state, slug, result, reason):
    stage = _stage_by_slug(graph, slug)
    if stage is None:
        raise EngineError(
            "unknown-stage",
            "Unknown stage slug %r." % slug,
            "Slugs are kebab-case stage identifiers; see "
            "scripts/data/stage-graph.json.",
        )
    gated = stage["gate"] != "none"
    if result == "completed" and gated:
        raise EngineError(
            "invalid-transition",
            "Stage %r has an approval gate; 'completed' is only for "
            "gate-less stages." % slug,
            "Use --result approved after the user approves at the gate.",
        )
    if result in ("approved", "rejected", "revised") and not gated:
        raise EngineError(
            "invalid-transition",
            "Stage %r has no approval gate; '%s' does not apply."
            % (slug, result),
            "Use --result completed for gate-less stages.",
        )
    if result == "skipped":
        membership = stage.get("scopes", {}).get(state.plan.scope, "EXECUTE")
        planned_skip = slug in state.plan.skip
        if not (
            stage["execution"] == "CONDITIONAL"
            or membership == "CONDITIONAL"
            or planned_skip
        ):
            raise EngineError(
                "invalid-transition",
                "Stage %r is not skippable (it is ALWAYS-execute under "
                "scope %r)." % (slug, state.plan.scope),
                "Only CONDITIONAL stages or plan-SKIP stages may be "
                "skipped. To change course, use: "
                "python <skill>/scripts/engine.py jump --stage <slug>",
            )
        if not reason:
            raise EngineError(
                "invalid-transition",
                "A skip requires a reason.",
                "Re-run with --reason \"<why this stage does not apply>\".",
            )
    current = current_stage(graph, state)
    if slug != current:
        raise EngineError(
            "invalid-transition",
            "Stage %r is not the current stage (current: %s)."
            % (slug, current or "none — workflow complete"),
            "Only the current stage can be reported. To change course, "
            "use: python <skill>/scripts/engine.py jump --stage <slug>",
        )
    return stage


def cmd_report(workspace, slug, result, reason):
    graph = load_graph()
    state = _load_active(graph, workspace)
    _require_intact(graph, state, workspace)
    stage = _validate_transition(graph, state, slug, result, reason)
    mark = {
        "completed": MARK_DONE,
        "approved": MARK_DONE,
        "rejected": MARK_REJECTED,
        "revised": MARK_REVISED,
        "skipped": MARK_SKIPPED,
    }[result]
    state.marks[slug] = mark
    state.parked = None  # a transition supersedes any parked note
    new_current = current_stage(graph, state)
    text = _splice_region(state, graph, new_current, new_current is None)
    _write_text_atomic(_state_path(workspace), text)
    _audit_append(workspace, EV_FOR_RESULT[result], stage=slug, reason=reason)
    ack = {
        "kind": "reported",
        "stage": slug,
        "result": result,
        "current_stage": new_current,
    }
    if result in ("completed", "approved"):
        try:  # soft warning, fail-open: never block the only write entry
            missing = _stage_missing_produces(workspace, stage)
            if missing:
                ack["produces_missing"] = missing
        except Exception:
            pass
    return ack


def cmd_jump(workspace, slug, fresh):
    graph = load_graph()
    if fresh:
        docs = os.path.join(workspace, DOCS_DIR)
        archive = None
        if os.path.isdir(docs):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            archive = os.path.join(
                workspace, "aidlc-docs-archive-%s" % stamp
            )
            # Record the reset in the archive's audit log before moving it.
            audit = _audit_path(workspace)
            if os.path.isfile(audit):
                _audit_append(workspace, EV_FRESH, detail="archived to %s"
                              % _posix(os.path.basename(archive)))
            os.replace(docs, archive)
        return {
            "kind": "fresh",
            "archived": _posix(os.path.relpath(archive, workspace))
            if archive
            else None,
        }
    state = _load_active(graph, workspace)
    _require_intact(graph, state, workspace)
    target = _stage_by_slug(graph, slug)
    if target is None:
        raise EngineError(
            "unknown-stage",
            "Unknown stage slug %r." % slug,
            "Slugs are kebab-case stage identifiers; see "
            "scripts/data/stage-graph.json.",
        )
    current = current_stage(graph, state)
    if current is None:
        raise EngineError(
            "invalid-jump",
            "The workflow is complete; there is no current stage to jump "
            "from.",
            "To restart, use: python <skill>/scripts/engine.py jump --fresh",
        )
    if slug == current:
        raise EngineError(
            "invalid-jump",
            "Stage %r is already the current stage." % slug,
            "Nothing to do. To redo it, jump to itself is unnecessary — "
            "report a revision cycle instead.",
        )
    ordered = [s["slug"] for s in graph["stages"]]
    from_index = ordered.index(current)
    to_index = ordered.index(slug)
    if to_index < from_index:
        direction = "backward"
        for stage in graph["stages"]:
            if ordered.index(stage["slug"]) >= to_index:
                state.marks[stage["slug"]] = MARK_PENDING
        detail = "redo from %s; stages from %s onward reset" % (current, slug)
    else:
        direction = "forward"
        skipped = []
        for stage in graph["stages"]:
            index = ordered.index(stage["slug"])
            if from_index <= index < to_index and not _is_done(
                state.marks.get(stage["slug"], MARK_PENDING)
            ):
                state.marks[stage["slug"]] = MARK_SKIPPED
                skipped.append(stage["slug"])
        detail = "forward to %s; intermediates marked [S]: %s" % (
            slug,
            ", ".join(skipped) if skipped else "none",
        )
    state.parked = None  # a course change supersedes any parked note
    new_current = current_stage(graph, state)
    text = _splice_region(state, graph, new_current, new_current is None)
    _write_text_atomic(_state_path(workspace), text)
    _audit_append(
        workspace,
        EV_JUMPED,
        stage=slug,
        detail="from %s (%s); %s" % (current, direction, detail),
    )
    ack = {
        "kind": "jumped",
        "from": current,
        "to": slug,
        "direction": direction,
        "current_stage": new_current,
    }
    effective = {s["slug"] for s in effective_stages(graph, state.plan)}
    if slug not in effective:
        ack["note"] = (
            "Stage %r is outside the routed plan (scope %r or plan lists "
            "exclude it). Add it to the 'Stages to Execute' line in "
            "aidlc-state.md for the router to emit it." % (slug, state.plan.scope)
        )
    return ack


def cmd_rebase(workspace):
    graph = load_graph()
    state = _load_active(graph, workspace)
    new_current = current_stage(graph, state)
    text = _splice_region(state, graph, new_current, new_current is None)
    _write_text_atomic(_state_path(workspace), text)
    _audit_append(workspace, EV_REBASELINED)
    return {"kind": "rebaselined", "current_stage": new_current}


# ---------------------------------------------------------------------------
# park (annotation verb — never a transition; marks and current unchanged)
# ---------------------------------------------------------------------------


def _handoff_path(workspace):
    return os.path.join(workspace, HANDOFF_FILE)


def _sanitize_park_note(note):
    """Fold newlines to '; ' and truncate; '' when nothing is left."""
    folded = "; ".join(
        part.strip()
        for part in note.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if part.strip()
    )
    return folded[:PARK_NOTE_MAX]


def _handoff_tail(workspace):
    """(stage, note) of the LAST park entry in handoff.md, or None."""
    path = _handoff_path(workspace)
    if not os.path.isfile(path):
        return None
    stage = note = None
    for line in _read_text(path).split("\n"):
        stripped = line.strip()
        m = AUDIT_STAGE_RE.match(stripped)
        if m:
            stage = m.group(1).strip()
            continue
        m = re.match(r"^\*\*Note\*\*:\s*(.*)$", stripped)
        if m:
            note = m.group(1).strip()
    if stage is None or note is None:
        return None
    return (stage, note)


def _handoff_append(workspace, stage, note):
    entry = "\n".join(
        [
            "",
            "## Park",
            "**Timestamp**: %s" % _now_iso(),
            "**Stage**: %s" % stage,
            "**Note**: %s" % note,
            "",
            "---",
            "",
        ]
    )
    prefix = ""
    path = _handoff_path(workspace)
    if not os.path.isfile(path):
        prefix = HANDOFF_HEADER
    _append_text(path, prefix + entry)


def cmd_park(workspace, note):
    graph = load_graph()
    state = _load_active(graph, workspace)
    _require_intact(graph, state, workspace)
    note = _sanitize_park_note(note)
    if not note:
        raise EngineError(
            "usage",
            "park requires a non-empty note.",
            "Re-run with --note \"<what is in flight, the next step, and "
            "any caveats>\".",
        )
    current = current_stage(graph, state)
    if current is None:
        raise EngineError(
            "workflow-complete",
            "The workflow is complete; there is no in-flight work to park.",
            "To restart, use: python <skill>/scripts/engine.py jump --fresh",
        )
    state.parked = (current, note)
    # Write order is fixed: region first (authoritative), then handoff.
    # A crash between the two leaves handoff one entry short — resume_note
    # comes from the region, so recovery is unaffected.
    text = _splice_region(state, graph, current, False)
    _write_text_atomic(_state_path(workspace), text)
    appended = False
    if _handoff_tail(workspace) != (current, note):
        _handoff_append(workspace, current, note)
        appended = True
    return {
        "kind": "parked",
        "stage": current,
        "note": note,
        "handoff_file": _posix(HANDOFF_FILE),
        "handoff_appended": appended,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class _JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser whose usage errors obey the JSON output contract."""

    def error(self, message):
        payload = {
            "kind": "error",
            "code": "usage",
            "message": "Invalid command line: %s" % message,
            "hint": "Usage: python engine.py "
            "<status|init|next|report|park|jump|rebase> "
            "[--workspace <path>]",
            "timestamp": _now_iso(),
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        sys.exit(1)


def _build_parser():
    parser = _JsonArgumentParser(
        prog="engine.py", description="AI-DLC runtime orchestration engine"
    )
    sub = parser.add_subparsers(
        dest="command", parser_class=_JsonArgumentParser
    )

    def add(name, **kwargs):
        # --workspace is accepted after every subcommand (calling
        # convention: engine.py <subcommand> [--workspace <path>]).
        child = sub.add_parser(name, **kwargs)
        child.add_argument(
            "--workspace",
            default=None,
            help="workspace root (default: current working directory)",
        )
        return child

    add("status", help="bootstrap probe + recovery data")
    add("init", help="create state/audit deterministically")
    add("next", help="route: emit exactly one directive")

    report = add("report", help="record a stage transition")
    report.add_argument("--stage", required=True)
    report.add_argument("--result", required=True, choices=RESULTS)
    report.add_argument("--reason", default=None)

    park = add("park", help="park in-flight work with a handoff note")
    park.add_argument("--note", required=True)

    jump = add("jump", help="change course")
    jump.add_argument("--stage", default=None)
    jump.add_argument("--fresh", action="store_true")

    add("rebase", help="re-baseline the State Digest")
    return parser


def main(argv):
    parser = _build_parser()
    args = parser.parse_args(argv[1:])
    workspace = os.path.abspath(getattr(args, "workspace", None) or os.getcwd())
    try:
        if args.command == "status":
            result = cmd_status(workspace)
        elif args.command == "init":
            result = cmd_init(workspace)
        elif args.command == "next":
            result = cmd_next(workspace)
        elif args.command == "report":
            result = cmd_report(workspace, args.stage, args.result, args.reason)
        elif args.command == "park":
            result = cmd_park(workspace, args.note)
        elif args.command == "jump":
            if not args.fresh and not args.stage:
                raise EngineError(
                    "usage",
                    "jump requires --stage <slug> or --fresh.",
                    "Examples: engine.py jump --stage user-stories | "
                    "engine.py jump --fresh",
                )
            result = cmd_jump(workspace, args.stage, args.fresh)
        elif args.command == "rebase":
            result = cmd_rebase(workspace)
        else:
            raise EngineError(
                "usage",
                "No subcommand given.",
                "Usage: python engine.py "
                "<status|init|next|report|park|jump|rebase> "
                "[--workspace <path>]",
            )
    except EngineError as exc:
        error = {"kind": "error", "code": exc.code, "message": exc.message,
                 "hint": exc.hint}
        error["timestamp"] = _now_iso()
        sys.stdout.write(json.dumps(error, indent=2) + "\n")
        return 1
    except Exception as exc:  # last-resort: keep the JSON output contract
        error = {"kind": "error", "code": "internal",
                 "message": "Unexpected engine failure: %s: %s"
                 % (type(exc).__name__, exc),
                 "hint": "This is an engine bug or an environment problem "
                 "(e.g. a locked file). If it persists, report it with the "
                 "command line you ran."}
        error["timestamp"] = _now_iso()
        sys.stdout.write(json.dumps(error, indent=2) + "\n")
        return 1
    result["timestamp"] = _now_iso()
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
