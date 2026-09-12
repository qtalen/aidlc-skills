#!/usr/bin/env python3
"""AI-DLC skill author-time code generator.

Scans the YAML frontmatter of every stage rule file under
``references/<phase>/*.md`` (the single source of truth), validates it against
``references/common/stage-contract.md``, and regenerates every
``<!-- BEGIN GENERATED: <key> -->`` section across the skill.

Pure Python 3.8+ standard library. No third-party dependencies.

Usage:
    python scripts/generate.py            # validate + rewrite drifted sections
    python scripts/generate.py --check    # validate + report drift (no writes)

Exit codes:
    0  success (or, with --check, no drift)
    1  --check only: one or more generated sections are out of date
    2  a hard validation error was found
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PHASE_ORDER = ("inception", "construction", "operations")

PHASE_META = {
    "inception": {
        "emoji": "\U0001F535",  # blue circle
        "title": "INCEPTION PHASE",
        "ascii_subtitle": "Planning & Application Design",
        "desc_subtitle": "Planning and Architecture",
    },
    "construction": {
        "emoji": "\U0001F7E2",  # green circle
        "title": "CONSTRUCTION PHASE",
        "ascii_subtitle": "Design, Implementation & Test",
        "desc_subtitle": "Design, Implementation & Test",
    },
    "operations": {
        "emoji": "\U0001F7E1",  # yellow circle
        "title": "OPERATIONS PHASE",
        "ascii_subtitle": "Placeholder for Future",
        "desc_subtitle": "Placeholder",
    },
}

ALLOWED_KEYS = frozenset(
    (
        "slug",
        "phase",
        "execution",
        "condition",
        "gate",
        "produces",
        "consumes",
        "requires_stage",
        "for_each",
        "workspace_writes",
        "depth",
        "scopes",
    )
)
REQUIRED_KEYS = (
    "slug",
    "phase",
    "execution",
    "condition",
    "gate",
    "produces",
    "consumes",
    "requires_stage",
)
CONSUME_KEYS = frozenset(("artifact", "required", "conditional_on"))
EXECUTION_VALUES = ("ALWAYS", "CONDITIONAL")
GATE_VALUES = ("none", "approve-continue", "two-option")
DEPTH_VALUES = ("adaptive", "minimal", "standard", "comprehensive")
CONDITIONAL_ON_VALUES = ("brownfield", "greenfield")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Artifact entries that must never appear in the generated session-continuity
# loading list (they are workflow bookkeeping, not resumable context).
SKIP_LOADING_ARTIFACTS = ("aidlc-state.md", "audit.md")

# key -> relative path of the consumer file holding the marker pair.
# NOTE: dict ordering is significant (Python 3.7+ preserves insertion order)
# and is used for deterministic output.
MARKERS = {
    "SKILL.md": [
        "stage-list-inception",
        "stage-list-construction",
        "stage-list-operations",
    ],
    "references/common/process-overview.md": [
        "canon-lists",
        "stage-flowchart",
        "stage-descriptions",
    ],
    "references/common/welcome-message.md": [
        "ascii-diagram",
    ],
    "references/common/terminology.md": [
        "stages-inception",
        "stages-construction",
        "stages-operations",
        "stage-classification",
    ],
    "references/common/session-continuity.md": [
        "artifact-loading",
    ],
    "references/inception/workflow-planning.md": [
        "execution-plan-mermaid",
        "execution-plan-stages",
        "state-template-stages",
    ],
    "references/extensions/workflow/autonomous-mode/autonomous-mode.md": [
        "stage-names",
    ],
}


class HardError(Exception):
    """A hard validation failure (non-zero exit)."""


# ---------------------------------------------------------------------------
# Mini YAML frontmatter parser (hand-written, deliberately tiny subset)
# ---------------------------------------------------------------------------


def _strip_inline_comment(value):
    """Drop a trailing ``# ...`` comment when preceded by whitespace."""
    m = re.search(r"(?:^|\s)#", value)
    if m:
        return value[: m.start()].rstrip()
    return value


def _parse_scalar(raw):
    value = _strip_inline_comment(raw.strip())
    if value == "":
        return ""
    if value in ("true", "false"):
        return value == "true"
    if value in ("null", "Null", "NULL", "~"):
        return None
    if re.match(r"^-?[0-9]+$", value):
        return int(value)
    return value


def _parse_block(block, path):
    """Parse an indented list block (string list or object list)."""
    items = []
    j = 0
    while j < len(block):
        stripped = block[j].strip()
        if not (stripped == "-" or stripped.startswith("- ")):
            raise HardError(
                "%s: expected a list item, got %r" % (path, block[j])
            )
        body = stripped[1:].strip()
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", body):
            # Object list item, e.g. `- artifact: foo/bar.md`.
            obj = {}
            key, value = body.split(":", 1)
            obj[key.strip()] = _parse_scalar(value)
            j += 1
            while j < len(block):
                continuation = block[j].strip()
                if continuation.startswith("- ") or continuation == "-":
                    break
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:(.*)$", continuation)
                if not m:
                    raise HardError(
                        "%s: cannot parse list item field %r" % (path, block[j])
                    )
                obj[m.group(1)] = _parse_scalar(m.group(2))
                j += 1
            items.append(obj)
        else:
            items.append(_parse_scalar(body))
            j += 1
    return items


def _parse_frontmatter(text, path):
    """Return ``(mapping, body)`` or raise :class:`HardError`."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r").strip() != "---":
        raise HardError("%s: missing YAML frontmatter opener ('---')" % path)
    close = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r").strip() == "---":
            close = i
            break
    if close is None:
        raise HardError("%s: missing YAML frontmatter closer ('---')" % path)

    fm_lines = [line.rstrip("\r") for line in lines[1:close]]
    body = "\n".join(lines[close + 1:])

    mapping = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if line.strip() == "" or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise HardError(
                "%s: unexpected indentation at frontmatter line %r" % (path, line)
            )
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
        if not m:
            raise HardError(
                "%s: cannot parse frontmatter line %r" % (path, line)
            )
        key = m.group(1)
        rest = m.group(2).strip()
        if key in mapping:
            raise HardError("%s: duplicate frontmatter key %r" % (path, key))
        if rest == "":
            i += 1
            block = []
            while (
                i < len(fm_lines)
                and fm_lines[i].strip() != ""
                and fm_lines[i][0] in " \t"
            ):
                block.append(fm_lines[i])
                i += 1
            mapping[key] = _parse_block(block, path) if block else []
        elif rest == "[]":
            mapping[key] = []
            i += 1
        else:
            mapping[key] = _parse_scalar(rest)
            i += 1
    return mapping, body


# ---------------------------------------------------------------------------
# Stage model, validation and ordering
# ---------------------------------------------------------------------------


class Stage(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def _rel(path):
    return os.path.relpath(path, SKILL_ROOT).replace("\\", "/")


def _as_str_list(value, path, key):
    if not isinstance(value, list):
        raise HardError("%s: %s must be a list" % (path, key))
    for item in value:
        if not isinstance(item, str):
            raise HardError(
                "%s: %s entries must be strings (got %r)" % (path, key, item)
            )
    return list(value)


def _as_consumes(value, path):
    if not isinstance(value, list):
        raise HardError("%s: consumes must be a list" % path)
    result = []
    for item in value:
        if not isinstance(item, dict):
            raise HardError("%s: consumes entries must be objects" % path)
        unknown = [k for k in item if k not in CONSUME_KEYS]
        if unknown:
            raise HardError(
                "%s: unknown consumes key(s): %s" % (path, ", ".join(sorted(unknown)))
            )
        if "artifact" not in item or "required" not in item:
            raise HardError(
                "%s: consumes entry requires 'artifact' and 'required'" % path
            )
        artifact = item["artifact"]
        if not isinstance(artifact, str) or artifact.strip() == "":
            raise HardError("%s: consumes.artifact must be a non-empty string" % path)
        required = item["required"]
        if not isinstance(required, bool):
            raise HardError("%s: consumes.required must be a boolean" % path)
        conditional_on = item.get("conditional_on")
        if conditional_on is not None:
            if (
                not isinstance(conditional_on, str)
                or conditional_on not in CONDITIONAL_ON_VALUES
            ):
                raise HardError(
                    "%s: consumes.conditional_on must be one of %s"
                    % (path, " | ".join(CONDITIONAL_ON_VALUES))
                )
        result.append(
            {
                "artifact": artifact,
                "required": required,
                "conditional_on": conditional_on,
            }
        )
    return result


def _derive_name(body, path):
    title = None
    for line in body.split("\n"):
        line = line.rstrip("\r")
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        raise HardError("%s: no H1 heading ('# ...') found in body" % path)
    if " - " in title:
        title = title.split(" - ", 1)[0]
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
    return title


def build_stage(path, stem, dir_phase, text):
    display_path = _rel(path)
    mapping, body = _parse_frontmatter(text, display_path)

    unknown = [key for key in mapping if key not in ALLOWED_KEYS]
    if unknown:
        raise HardError(
            "%s: unknown frontmatter key(s): %s"
            % (display_path, ", ".join(sorted(unknown)))
        )
    for key in REQUIRED_KEYS:
        if key not in mapping:
            raise HardError("%s: missing required key %r" % (display_path, key))

    slug = mapping["slug"]
    if not isinstance(slug, str):
        raise HardError("%s: slug must be a string" % display_path)
    if not KEBAB_RE.match(slug):
        raise HardError("%s: slug %r is not kebab-case" % (display_path, slug))
    if slug != stem:
        raise HardError(
            "%s: slug %r must equal filename stem %r" % (display_path, slug, stem)
        )

    phase = mapping["phase"]
    if not isinstance(phase, str) or phase not in PHASE_ORDER:
        raise HardError(
            "%s: phase must be one of %s" % (display_path, " | ".join(PHASE_ORDER))
        )
    if phase != dir_phase:
        raise HardError(
            "%s: phase %r must match containing directory %r"
            % (display_path, phase, dir_phase)
        )

    execution = mapping["execution"]
    if execution not in EXECUTION_VALUES:
        raise HardError(
            "%s: execution must be one of %s"
            % (display_path, " | ".join(EXECUTION_VALUES))
        )

    condition = mapping["condition"]
    if not isinstance(condition, str) or condition.strip() == "":
        raise HardError("%s: condition must be a non-empty string" % display_path)

    gate = mapping["gate"]
    if gate not in GATE_VALUES:
        raise HardError(
            "%s: gate must be one of %s" % (display_path, " | ".join(GATE_VALUES))
        )

    produces = _as_str_list(mapping["produces"], display_path, "produces")
    requires_stage = _as_str_list(
        mapping["requires_stage"], display_path, "requires_stage"
    )
    consumes = _as_consumes(mapping["consumes"], display_path)

    for_each = mapping.get("for_each")
    if for_each is not None and for_each != "unit-of-work":
        raise HardError(
            "%s: for_each must be 'unit-of-work' when present" % display_path
        )

    workspace_writes = mapping.get("workspace_writes", False)
    if not isinstance(workspace_writes, bool):
        raise HardError("%s: workspace_writes must be a boolean" % display_path)

    depth = mapping.get("depth")
    if depth is not None and depth not in DEPTH_VALUES:
        raise HardError(
            "%s: depth must be one of %s"
            % (display_path, " | ".join(DEPTH_VALUES))
        )

    scopes = _as_str_list(mapping.get("scopes", []), display_path, "scopes")
    if scopes:
        raise HardError(
            "%s: scopes is reserved and must be absent or empty" % display_path
        )

    return Stage(
        path=path,
        slug=slug,
        phase=phase,
        execution=execution,
        condition=condition,
        gate=gate,
        produces=produces,
        consumes=consumes,
        requires_stage=requires_stage,
        for_each=for_each,
        workspace_writes=workspace_writes,
        depth=depth,
        scopes=scopes,
        name=_derive_name(body, display_path),
    )


def load_stages():
    stages = []
    for phase in PHASE_ORDER:
        directory = os.path.join(SKILL_ROOT, "references", phase)
        if not os.path.isdir(directory):
            continue
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".md"):
                continue
            path = os.path.join(directory, filename)
            if not os.path.isfile(path):
                continue
            text = _read_text(path)
            stages.append(build_stage(path, filename[:-3], phase, text))
    if not stages:
        raise HardError("no stage files found under references/<phase>/")
    return stages


def _validate_references(stages):
    by_slug = {}
    for stage in stages:
        by_slug[stage.slug] = stage
    for stage in stages:
        for ref in stage.requires_stage:
            if ref not in by_slug:
                raise HardError(
                    "%s: requires_stage references unknown slug %r"
                    % (_rel(stage.path), ref)
                )


def _detect_cycles(stages, by_slug):
    white, gray, black = 0, 1, 2
    color = {stage.slug: white for stage in stages}

    def visit(stage):
        color[stage.slug] = gray
        for ref in stage.requires_stage:
            target = by_slug[ref]
            if color[target.slug] == gray:
                raise HardError(
                    "cycle detected in requires_stage graph involving %r"
                    % target.slug
                )
            if color[target.slug] == white:
                visit(target)
        color[stage.slug] = black

    for stage in stages:
        if color[stage.slug] == white:
            visit(stage)


def compute_display_order(stages):
    """Phase order first, then layered topological order within each phase."""
    by_slug = {stage.slug: stage for stage in stages}
    ordered = []
    for phase in PHASE_ORDER:
        in_phase = [stage for stage in stages if stage.phase == phase]
        in_slugs = set(stage.slug for stage in in_phase)
        memo = {}

        def layer(stage):
            if stage.slug in memo:
                return memo[stage.slug]
            deps = [ref for ref in stage.requires_stage if ref in in_slugs]
            value = 0 if not deps else 1 + max(layer(by_slug[ref]) for ref in deps)
            memo[stage.slug] = value
            return value

        for stage in in_phase:
            layer(stage)
        in_phase.sort(key=lambda s: (memo[s.slug], s.slug))
        ordered.extend(in_phase)
    return ordered


# ---------------------------------------------------------------------------
# Advisory warnings
# ---------------------------------------------------------------------------


def _artifact_matches(consume, produce):
    c = consume[:-2] if consume.endswith("/*") else consume
    p = produce[:-2] if produce.endswith("/*") else produce
    if c == p:
        return True
    if p.startswith(c + "/"):
        return True
    if c.startswith(p + "/"):
        return True
    return False


def compute_warnings(stages):
    warnings = []
    for stage in stages:
        for consume in stage.consumes:
            producers = [
                other
                for other in stages
                if any(
                    _artifact_matches(consume["artifact"], produced)
                    for produced in other.produces
                )
            ]
            if not producers:
                warnings.append(
                    "consume artifact %r of stage %r matches no stage's produces"
                    % (consume["artifact"], stage.slug)
                )
                continue
            if consume["required"]:
                others = [p for p in producers if p.slug != stage.slug]
                if others and not any(
                    p.slug in stage.requires_stage for p in others
                ):
                    warnings.append(
                        "required consume %r of stage %r has producer(s) %s not in requires_stage"
                        % (
                            consume["artifact"],
                            stage.slug,
                            ", ".join(sorted(p.slug for p in others)),
                        )
                    )

    seen = {}
    for stage in stages:
        for produced in stage.produces:
            if produced in seen and seen[produced] != stage.slug:
                warnings.append(
                    "produces collision: %r written by both %r and %r"
                    % (produced, seen[produced], stage.slug)
                )
            else:
                seen[produced] = stage.slug
    return warnings


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _node_id(slug):
    return "".join(part.capitalize() for part in slug.split("-"))


def build_render_map(ordered):
    def ps(phase):
        return [stage for stage in ordered if stage.phase == phase]

    def tag(stage):
        if stage.phase == "operations":
            return "PLACEHOLDER"
        return stage.execution

    def short_label(stage):
        if stage.phase == "operations":
            return "PLACEHOLDER"
        return "ALWAYS" if stage.execution == "ALWAYS" else "COND"

    def render_stage_list(phase):
        lines = []
        for stage in ps(phase):
            adaptive = " - Adaptive depth" if stage.depth == "adaptive" else ""
            lines.append("- %s (%s%s)" % (stage.name, tag(stage), adaptive))
        return "\n".join(lines)

    def render_stage_list_construction():
        construction = ps("construction")
        for_each = [s for s in construction if s.for_each]
        others = [s for s in construction if not s.for_each]
        lines = []
        if for_each:
            lines.append("- Per-Unit Loop (executes for each unit):")
            for stage in for_each:
                lines.append("  - %s (%s, per-unit)" % (stage.name, tag(stage)))
        for stage in others:
            lines.append("- %s (%s)" % (stage.name, tag(stage)))
        return "\n".join(lines)

    def render_stages_construction_flat():
        lines = []
        for stage in ps("construction"):
            per_unit = ", per-unit" if stage.for_each else ""
            lines.append("- %s (%s%s)" % (stage.name, tag(stage), per_unit))
        return "\n".join(lines)

    def render_canon_lists():
        always = [s.name for s in ordered if s.execution == "ALWAYS"]
        conditional = [
            s.name
            for s in ordered
            if s.execution == "CONDITIONAL" and s.phase != "operations"
        ]
        return (
            "\u2022 **These stages always execute**: %s\n"
            "\u2022 **All other stages are conditional**: %s"
            % (", ".join(always), ", ".join(conditional))
        )

    def render_stage_names():
        return ", ".join(s.name for s in ordered if s.phase != "operations")

    def render_stage_descriptions():
        blocks = []
        for phase in PHASE_ORDER:
            meta = PHASE_META[phase]
            lines = [
                "**%s %s** - %s"
                % (meta["emoji"], meta["title"], meta["desc_subtitle"])
            ]
            for stage in ps(phase):
                per_unit = ", per-unit" if stage.for_each else ""
                lines.append(
                    "- %s: %s (%s%s)"
                    % (stage.name, stage.condition, tag(stage), per_unit)
                )
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    def render_stage_classification():
        always = [s for s in ordered if s.execution == "ALWAYS"]
        conditional = [
            s
            for s in ordered
            if s.execution == "CONDITIONAL" and s.phase != "operations"
        ]
        lines = ["- **%s**: %s" % (s.name, s.condition) for s in always]
        lines.append("")
        lines.append("### Conditional Stages")
        lines.extend("- **%s**: %s" % (s.name, s.condition) for s in conditional)
        return "\n".join(lines)

    def render_artifact_loading():
        lines = []
        for stage in ordered:
            if not stage.produces:
                continue
            entries = [
                p for p in stage.produces if p not in SKIP_LOADING_ARTIFACTS
            ]
            if not entries:
                continue
            text = ", ".join(entries)
            if stage.workspace_writes:
                text += ", plus all generated application code"
            lines.append("   - **%s**: Read %s" % (stage.name, text))
        return "\n".join(lines)

    def render_mermaid(status_mode):
        blank = "    "
        lines = ["```mermaid", "flowchart TD", '    Start(["User Request"])', blank]
        for phase in PHASE_ORDER:
            meta = PHASE_META[phase]
            lines.append(
                '    subgraph %s["%s %s"]'
                % (phase.upper(), meta["emoji"], meta["title"])
            )
            for stage in ps(phase):
                if stage.phase == "operations":
                    label = "PLACEHOLDER"
                elif status_mode:
                    label = "STATUS"
                else:
                    label = tag(stage)
                lines.append(
                    '        %s["%s<br/><b>%s</b>"]'
                    % (_node_id(stage.slug), stage.name, label)
                )
            lines.append("    end")
            lines.append(blank)

        # Start edges for root stages.
        for stage in ordered:
            if not stage.requires_stage:
                lines.append("    Start --> %s" % _node_id(stage.slug))

        # Dependency edges (arrow style follows the target's execution).
        for stage in ordered:
            for ref in stage.requires_stage:
                arrow = "-.->" if stage.execution == "CONDITIONAL" else "-->"
                lines.append(
                    "    %s %s %s"
                    % (_node_id(ref), arrow, _node_id(stage.slug))
                )

        # Per-unit loop back-edge.
        for_each = [s for s in ordered if s.for_each]
        if for_each:
            lines.append(
                "    %s -.->|Next Unit| %s"
                % (_node_id(for_each[-1].slug), _node_id(for_each[0].slug))
            )

        # Sink stages terminate the flow.
        depended = set()
        for stage in ordered:
            depended.update(stage.requires_stage)
        for stage in ordered:
            if stage.slug not in depended:
                arrow = "-.->" if stage.execution == "CONDITIONAL" else "-->"
                lines.append(
                    '    %s %s End(["Complete"])'
                    % (_node_id(stage.slug), arrow)
                )

        lines.append(blank)
        if status_mode:
            lines.append(
                "    %% Replace STATUS with COMPLETED, SKIP, EXECUTE as appropriate"
            )
            lines.append("    %% Apply styling based on status")
        else:
            for stage in ordered:
                if stage.execution == "ALWAYS":
                    lines.append(
                        "    style %s fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff"
                        % _node_id(stage.slug)
                    )
            for stage in ordered:
                if stage.execution == "CONDITIONAL" and stage.phase != "operations":
                    lines.append(
                        "    style %s fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000"
                        % _node_id(stage.slug)
                    )
            lines.append(
                "    style Operations fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000"
            )
            lines.append(
                "    style INCEPTION fill:#BBDEFB,stroke:#1565C0,stroke-width:3px, color:#000"
            )
            lines.append(
                "    style CONSTRUCTION fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px, color:#000"
            )
            lines.append(
                "    style OPERATIONS fill:#FFF59D,stroke:#F57F17,stroke-width:3px, color:#000"
            )
            lines.append(
                "    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000"
            )
            lines.append(
                "    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000"
            )
            lines.append(blank)
            lines.append("    linkStyle default stroke:#333,stroke-width:2px")
        lines.append("```")
        return "\n".join(lines)

    def render_ascii():
        width = 39
        indent = " " * 8

        def border():
            return indent + "+" + "-" * width + "+"

        def row(content):
            return indent + "|" + content.ljust(width) + "|"

        lines = ["```"]
        lines.append(" " * 25 + "User Request")
        lines.append(" " * 30 + "|")
        lines.append(" " * 30 + "v")
        for phase in PHASE_ORDER:
            meta = PHASE_META[phase]
            stages = ps(phase)
            lines.append(border())
            lines.append(row("     " + meta["title"]))
            lines.append(row("     " + meta["ascii_subtitle"]))
            lines.append(border())
            for_each = [s for s in stages if s.for_each]
            others = [s for s in stages if not s.for_each]
            if for_each:
                lines.append(row(" * Per-Unit Loop (for each unit):"))
                for stage in for_each:
                    lines.append(
                        row("   - %s (%s)" % (stage.name, short_label(stage)))
                    )
            for stage in others:
                lines.append(row(" * %s (%s)" % (stage.name, short_label(stage))))
            lines.append(border())
            lines.append(" " * 30 + "|")
            lines.append(" " * 30 + "v")
        lines.append(" " * 27 + "Complete")
        lines.append("```")
        return "\n".join(lines)

    def render_execution_plan_stages():
        lines = []
        for index, phase in enumerate(PHASE_ORDER):
            if index > 0:
                lines.append("")
            meta = PHASE_META[phase]
            lines.append("### %s %s" % (meta["emoji"], meta["title"]))
            for stage in ps(phase):
                if stage.phase == "operations":
                    lines.append("- [ ] %s - PLACEHOLDER" % stage.name)
                    lines.append(
                        "  - **Rationale**: Future deployment and monitoring workflows"
                    )
                elif stage.execution == "ALWAYS":
                    lines.append("- [ ] %s - EXECUTE (ALWAYS)" % stage.name)
                    lines.append(
                        "  - **Rationale**: [Why this stage is needed]"
                    )
                else:
                    per_unit = " (per-unit)" if stage.for_each else ""
                    lines.append(
                        "- [ ] %s - [EXECUTE/SKIP]%s" % (stage.name, per_unit)
                    )
                    lines.append(
                        "  - **Rationale**: [Why executing or skipping]"
                    )
        return "\n".join(lines)

    def render_state_template_stages():
        lines = []
        for index, phase in enumerate(PHASE_ORDER):
            if index > 0:
                lines.append("")
            meta = PHASE_META[phase]
            lines.append("### %s %s" % (meta["emoji"], meta["title"]))
            for stage in ps(phase):
                if stage.phase == "operations":
                    lines.append("- [ ] %s - PLACEHOLDER" % stage.name)
                    continue
                if stage.for_each and stage.execution == "CONDITIONAL":
                    suffix = " (per-unit, if applicable)"
                elif stage.for_each:
                    suffix = " (per-unit)"
                elif stage.execution == "CONDITIONAL":
                    suffix = " (if applicable)"
                else:
                    suffix = ""
                lines.append("- [ ] %s%s" % (stage.name, suffix))
        return "\n".join(lines)

    render_map = {
        "stage-list-inception": lambda: render_stage_list("inception"),
        "stage-list-construction": render_stage_list_construction,
        "stage-list-operations": lambda: render_stage_list("operations"),
        "canon-lists": render_canon_lists,
        "stage-flowchart": lambda: render_mermaid(False),
        "stage-descriptions": render_stage_descriptions,
        "ascii-diagram": render_ascii,
        "stages-inception": lambda: render_stage_list("inception"),
        "stages-construction": render_stages_construction_flat,
        "stages-operations": lambda: render_stage_list("operations"),
        "stage-classification": render_stage_classification,
        "artifact-loading": render_artifact_loading,
        "execution-plan-mermaid": lambda: render_mermaid(True),
        "execution-plan-stages": render_execution_plan_stages,
        "state-template-stages": render_state_template_stages,
        "stage-names": render_stage_names,
    }
    return render_map


# ---------------------------------------------------------------------------
# Marker replacement and file IO
# ---------------------------------------------------------------------------


def _read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _replace_section(text, key, rendered):
    begin_re = re.compile(
        r"<!-- BEGIN GENERATED: " + re.escape(key) + r"[^\r\n]*?-->"
    )
    end_re = re.compile(r"<!-- END GENERATED: " + re.escape(key) + r" -->")
    match_begin = begin_re.search(text)
    if not match_begin:
        raise HardError("missing BEGIN marker for key %r" % key)
    match_end = end_re.search(text, match_begin.end())
    if not match_end:
        raise HardError("missing END marker for key %r" % key)

    between = text[match_begin.end():match_end.start()]
    if between.startswith("\r\n"):
        newline = "\r\n"
    elif between.startswith("\n"):
        newline = "\n"
    else:
        newline = None

    if newline:
        body = rendered.replace("\n", newline)
        new_between = newline + body + newline
    else:
        new_between = rendered
    return text[: match_begin.end()] + new_between + text[match_end.start():]


def regenerate(check):
    stages = load_stages()
    _validate_references(stages)
    by_slug = {stage.slug: stage for stage in stages}
    _detect_cycles(stages, by_slug)

    ordered = compute_display_order(stages)
    warnings = compute_warnings(stages)
    render_map = build_render_map(ordered)

    drifted = []
    changed_files = {}
    for relpath, keys in MARKERS.items():
        path = os.path.join(SKILL_ROOT, relpath)
        if not os.path.isfile(path):
            raise HardError("marker target file not found: %s" % relpath)
        text = _read_text(path)
        found = re.findall(r"<!-- BEGIN GENERATED:\s*([A-Za-z0-9_-]+)", text)
        for key in found:
            if key not in keys:
                raise HardError(
                    "%s: unknown GENERATED marker key %r" % (relpath, key)
                )
        new_text = text
        for key in keys:
            if key not in found:
                raise HardError(
                    "%s: missing GENERATED marker for key %r" % (relpath, key)
                )
            if key not in render_map:
                raise HardError("no renderer registered for key %r" % key)
            replaced = _replace_section(new_text, key, render_map[key]())
            if replaced != new_text:
                drifted.append(key)
            new_text = replaced
        if new_text != text:
            changed_files[relpath] = new_text
    return warnings, drifted, changed_files


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv):
    check = "--check" in argv[1:]
    try:
        warnings, drifted, changed_files = regenerate(check)
    except HardError as exc:
        sys.stderr.write("ERROR: %s\n" % exc)
        return 2

    for warning in warnings:
        sys.stdout.write("WARNING: %s\n" % warning)

    if check:
        if drifted:
            for key in drifted:
                sys.stdout.write("DRIFT: %s\n" % key)
            sys.stdout.write(
                "%d generated section(s) out of date.\n" % len(drifted)
            )
            return 1
        sys.stdout.write("All generated sections up to date.\n")
        return 0

    for relpath, text in changed_files.items():
        _write_text(os.path.join(SKILL_ROOT, relpath), text)
    for key in drifted:
        sys.stdout.write("Regenerated: %s\n" % key)
    sys.stdout.write(
        "%d section(s) regenerated, %d file(s) written.\n"
        % (len(drifted), len(changed_files))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
