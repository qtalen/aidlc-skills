#!/usr/bin/env python3
"""FR <-> story traceability matrix for AI-DLC artifacts (author-time audit).

Builds the functional-requirement coverage matrix between an iteration's
requirements.md (FR definitions) and stories.md (user stories with trace
lines), and cross-checks counts the documents claim against the parsed
actuals. Serves the mid-workflow scope-shrink audit: after a range change
defers FRs/stories, this tool answers "what is still covered, what went
dangling, and did any active story keep tracing a deferred FR?"

Usage:
    python trace-matrix.py [--docs <aidlc-docs-root>]
                           [--requirements <path>] [--stories <path>]
                           [--expect-active-fr N] [--expect-deferred-fr N]
                           [--expect-story N]

``--docs`` defaults to the current working directory; requirements
defaults to ``<docs>/inception/requirements/requirements.md`` and stories
to ``<docs>/inception/user-stories/stories.md``. Explicit
``--requirements`` / ``--stories`` override the derived paths. Each
``--expect-*`` names a count the documents claim; the tool compares it
with the parsed actual and reports the verdict under ``count_checks``
(``--expect-story`` is checked against the TOTAL story count).

Every invocation prints exactly one JSON object to stdout: exit 0 with a
report, or exit 1 with ``{"kind": "error", "code": ..., "message": ...,
"hint": ..., "timestamp": ...}`` (codes: usage, missing-file, internal).

Parsing conventions (heuristics fitted to the real dogfood artifacts):
- FR definition: any line containing ``**FR-<n>`` defines FR <n>; the
  first occurrence of a number wins. The entry is Deferred when its own
  line mentions ``Deferred`` (case-insensitive; this covers the
  full-width-paren form ``**FR-30（Deferred）...**``), otherwise when the
  nearest preceding section-level Markdown heading mentions it (the
  deferred-section inheritance form: ``### D. TABLE —— **Deferred...**``).
- Story definition: an H2-H4 heading containing a ``US<digits>-<digits>``
  token (the leading digit group is optional: ``US-01``); the FIRST such
  token in the heading is the story ID. Deferred is judged the same way
  (own heading line, else the nearest preceding section-level heading).
- Section-level heading (the ONLY Deferred inheritance source): a
  heading WITHOUT an entry-ID token. Headings carrying ``US<digits>-
  <digits>`` or ``FR-<digits>`` act on their own entry only (through the
  own-line check) and never propagate Deferred to later siblings —
  back-to-back story headings do not leak state (``### US2-24（Deferred）
  ...`` does not defer a ``### US2-25`` that follows it).
- Trace line: ``**追溯**:`` / ``**Trace**:`` (half- or full-width colon)
  belonging to the nearest story heading above it. Tilde ranges in the
  body are expanded first (``FR-30~34`` -> 30, 31, 32, 33, 34; spans
  beyond 50 are left alone and treated as prose). The body is then split
  on ``、 , ; ，`` (enumeration mark, ASCII and full-width commas,
  ASCII and full-width semicolons) into segments, each segment on ``/``
  into pieces; the
  first piece of a segment must start with ``FR-<n>`` and later
  bare-number pieces inherit the prefix (``FR-10/11/14/15`` -> 10, 11,
  14, 15). Segments whose first piece does not match (``BR-01``,
  ``验收场景 2``) are ignored entirely, bare pieces included.

Limitations:
- The heuristics make no promise about malformed Markdown; a renamed
  trace label or a new ID scheme silently yields zero matches rather
  than an error.
- Every parsed story heading counts toward ``story_total`` /
  ``story_active`` — including placeholder headings that merely keep a
  number alive after a scope reduction (e.g. ``### US2-21（已并入
  US2-19/20 ...）``). ``story_active`` can therefore legitimately exceed
  a document's own "effective stories" count by the number of
  placeholders; read the Deferred list, not just the totals.
- Deferred detection is the literal word ``Deferred`` on the entry line
  or the nearest heading; prose-only deferral notes are not understood.
- This is an author-time audit assistant, NOT a CI gate: it never writes
  files and its verdicts are advisory.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

TOOL = "trace-matrix"

REQ_REL = os.path.join("inception", "requirements", "requirements.md")
STORIES_REL = os.path.join("inception", "user-stories", "stories.md")

USAGE_HINT = (
    "Usage: python trace-matrix.py [--docs <dir>] [--requirements <path>] "
    "[--stories <path>] [--expect-active-fr N] [--expect-deferred-fr N] "
    "[--expect-story N]"
)

# FR definition: a bold ``FR-<n>`` token anywhere in the line.
FR_DEF_RE = re.compile(r"\*\*FR-(\d+)\b")
# Any Markdown ATX heading; only section-level ones (see
# ENTRY_ID_TOKEN_RE) carry Deferred inheritance downward.
HEADING_RE = re.compile(r"^#{1,6}\s")
# Entry-ID token inside a heading line. Headings carrying one act on
# their own entry only (via the own-line Deferred check) and are NEVER
# Deferred-inheritance sources for later sibling entries.
ENTRY_ID_TOKEN_RE = re.compile(r"\bUS\d*-\d+\b|\bFR-\d+\b")
# Story heading: H2-H4 whose first ``US<group>-<number>`` token is the ID.
# Non-greedy so the FIRST token wins (a placeholder heading like
# ``### US2-21（已并入 US2-19/20 ...）`` must not resolve to US2-19).
STORY_HEADING_RE = re.compile(r"^#{2,4}\s+.*?\b(US\d*-\d+)\b")
# Trace line: ``**追溯**:`` / ``**Trace**:`` with half- or full-width colon.
TRACE_RE = re.compile(r"^\*\*(?:追溯|Trace)\*\*\s*[:：]\s*(.+)$")
# Trace body grammar.
TRACE_SEGMENT_RE = re.compile(r"[、,;；，]")
FR_PIECE_RE = re.compile(r"FR-(\d+)")
BARE_NUMBER_RE = re.compile(r"\d+")
STORY_ID_RE = re.compile(r"^US(\d*)-(\d+)$")
# Tilde range shorthand (``FR-30~34``), expanded before segment parsing.
TILDE_RANGE_RE = re.compile(r"\bFR-(\d+)~(\d+)\b")
RANGE_SPAN_MAX = 50


class MatrixError(Exception):
    """An expected, reportable failure (emitted as an error JSON object)."""

    def __init__(self, code, message, hint):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _now_iso():
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _posix(path):
    return path.replace("\\", "/")


def _fr_id(number):
    return "FR-%02d" % number


def _story_sort_key(story_id):
    """Numeric sort key so US2-2 orders before US2-10 (and US2- before US-)."""
    m = STORY_ID_RE.match(story_id)
    if m:
        return (0, int(m.group(1) or "0"), int(m.group(2)), story_id)
    return (1, 0, 0, story_id)


def _read_text(path):
    if not os.path.isfile(path):
        raise MatrixError(
            "missing-file",
            "Required document not found: %s" % _posix(path),
            "Pass --docs <aidlc-docs-root>, or point --requirements / "
            "--stories at the files directly.",
        )
    # utf-8-sig: tolerates a BOM (which would otherwise break the
    # heading/trace regexes anchored at ^); plain UTF-8 decodes unchanged.
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_requirements(text):
    """FR definitions as ``{number: deferred}``; first occurrence wins.

    Deferred = the defining line mentions ``Deferred`` (case-insensitive),
    else the nearest strictly-preceding SECTION-level heading does (one
    without an entry-ID token; entry-ID headings never propagate).
    """
    frs = {}
    section_deferred = False
    for line in text.split("\n"):
        if HEADING_RE.match(line):
            if not ENTRY_ID_TOKEN_RE.search(line):
                section_deferred = "deferred" in line.lower()
        m = FR_DEF_RE.search(line)
        if m:
            number = int(m.group(1))
            if number not in frs:
                frs[number] = "deferred" in line.lower() or section_deferred
    return frs


def _expand_tilde_ranges(content):
    """Expand ``FR-30~34`` tilde ranges to explicit FR ids.

    The tilde range is an established shorthand in the dogfood artifacts
    (e.g. ``**追溯**: FR-30~34``); without expansion only the first
    number would register, silently hiding coverage of FR-31..34. Spans
    beyond ``RANGE_SPAN_MAX`` (or inverted) are left as-is — treated as
    prose, not a reference list.
    """
    def repl(match):
        lo, hi = int(match.group(1)), int(match.group(2))
        if 0 <= hi - lo <= RANGE_SPAN_MAX:
            return ", ".join("FR-%d" % number for number in range(lo, hi + 1))
        return match.group(0)

    return TILDE_RANGE_RE.sub(repl, content)


def _extract_fr_refs(content):
    """FR numbers referenced by one trace-line body (see module docstring)."""
    refs = []
    for segment in TRACE_SEGMENT_RE.split(_expand_tilde_ranges(content)):
        pieces = [piece.strip() for piece in segment.split("/")]
        m = FR_PIECE_RE.match(pieces[0])
        if not m:
            continue  # non-FR segment (BR-xx, acceptance scenarios): skipped
        refs.append(int(m.group(1)))
        for piece in pieces[1:]:
            bare = BARE_NUMBER_RE.match(piece)
            if bare:
                refs.append(int(bare.group(0)))
    return refs


def parse_stories(text):
    """Story definitions + their FR trace references.

    Returns ``(stories, traces)``: ``stories`` maps the first occurrence
    of each story ID to its Deferred flag (document order); ``traces``
    maps a story ID to the set of FR numbers referenced by the trace
    lines under its heading. A trace line before any story heading is
    ignored. Deferred = the story's own heading line, else the nearest
    strictly-preceding SECTION-level heading (one without an entry-ID
    token; a sibling story's heading never propagates its Deferred).
    """
    stories = {}
    traces = {}
    section_deferred = False
    current = None
    for line in text.split("\n"):
        if HEADING_RE.match(line):
            if not ENTRY_ID_TOKEN_RE.search(line):
                section_deferred = "deferred" in line.lower()
        m = STORY_HEADING_RE.match(line)
        if m:
            story_id = m.group(1)
            if story_id not in stories:
                stories[story_id] = (
                    "deferred" in line.lower() or section_deferred
                )
            current = story_id
            continue
        tm = TRACE_RE.match(line)
        if tm and current is not None:
            traces.setdefault(current, set()).update(
                _extract_fr_refs(tm.group(1))
            )
    return stories, traces


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def build_report(requirements_path, stories_path, expect_active_fr,
                 expect_deferred_fr, expect_story):
    frs = parse_requirements(_read_text(requirements_path))
    stories, traces = parse_stories(_read_text(stories_path))

    traced_by = {}  # fr number -> set of story IDs
    for story_id, refs in traces.items():
        for number in refs:
            traced_by.setdefault(number, set()).add(story_id)

    fr_numbers = sorted(frs)
    deferred_numbers = [n for n in fr_numbers if frs[n]]
    active_count = len(fr_numbers) - len(deferred_numbers)

    matrix = []
    uncovered_active_frs = []
    for number in fr_numbers:
        story_ids = sorted(traced_by.get(number, ()), key=_story_sort_key)
        if frs[number]:
            status = "deferred"  # deferred FRs keep their traced stories
        elif story_ids:
            status = "covered"
        else:
            status = "uncovered"
            uncovered_active_frs.append(_fr_id(number))
        matrix.append(
            {
                "fr": _fr_id(number),
                "deferred": frs[number],
                "stories": story_ids,
                "status": status,
            }
        )

    referenced = set()
    for refs in traces.values():
        referenced.update(refs)
    dangling = []
    for number in sorted(referenced - set(frs)):
        referencing = sorted(
            (s for s, refs in traces.items() if number in refs),
            key=_story_sort_key,
        )
        dangling.append({"fr": _fr_id(number), "stories": referencing})

    scope_leaks = []  # warning-grade: active stories tracing deferred FRs
    for number in deferred_numbers:
        leaking = sorted(
            (
                s
                for s, refs in traces.items()
                if number in refs and not stories.get(s, True)
            ),
            key=_story_sort_key,
        )
        if leaking:
            scope_leaks.append({"fr": _fr_id(number), "stories": leaking})

    count_checks = []
    if expect_active_fr is not None:
        count_checks.append(
            {
                "check": "active_fr",
                "declared": expect_active_fr,
                "actual": active_count,
                "match": expect_active_fr == active_count,
            }
        )
    if expect_deferred_fr is not None:
        count_checks.append(
            {
                "check": "deferred_fr",
                "declared": expect_deferred_fr,
                "actual": len(deferred_numbers),
                "match": expect_deferred_fr == len(deferred_numbers),
            }
        )
    if expect_story is not None:
        count_checks.append(
            {
                "check": "story",
                "declared": expect_story,
                "actual": len(stories),
                "match": expect_story == len(stories),
            }
        )

    return {
        "tool": TOOL,
        "requirements": {
            "file": _posix(requirements_path),
            "fr_total": len(fr_numbers),
            "fr_active": active_count,
            "fr_deferred": [_fr_id(n) for n in deferred_numbers],
        },
        "stories": {
            "file": _posix(stories_path),
            "story_total": len(stories),
            "story_active": sum(1 for d in stories.values() if not d),
            "story_deferred": [s for s, d in stories.items() if d],
        },
        "matrix": matrix,
        "uncovered_active_frs": uncovered_active_frs,
        "dangling_trace_references": dangling,
        "scope_leaks": scope_leaks,
        "count_checks": count_checks,
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
            "hint": USAGE_HINT,
            "timestamp": _now_iso(),
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        sys.exit(1)


def _build_parser():
    parser = _JsonArgumentParser(
        prog="trace-matrix.py",
        description="FR <-> story traceability matrix (author-time audit)",
    )
    parser.add_argument(
        "--docs",
        default=None,
        help="aidlc-docs root (default: current working directory)",
    )
    parser.add_argument(
        "--requirements",
        default=None,
        help="requirements.md path "
        "(default: <docs>/inception/requirements/requirements.md)",
    )
    parser.add_argument(
        "--stories",
        default=None,
        help="stories.md path "
        "(default: <docs>/inception/user-stories/stories.md)",
    )
    parser.add_argument(
        "--expect-active-fr",
        type=int,
        default=None,
        help="declared active FR count, verified against the parsed actual",
    )
    parser.add_argument(
        "--expect-deferred-fr",
        type=int,
        default=None,
        help="declared deferred FR count, verified against the parsed actual",
    )
    parser.add_argument(
        "--expect-story",
        type=int,
        default=None,
        help="declared TOTAL story count, verified against the parsed actual",
    )
    return parser


def main(argv):
    parser = _build_parser()
    args = parser.parse_args(argv[1:])
    docs = args.docs if args.docs is not None else os.getcwd()
    requirements_path = args.requirements or os.path.join(docs, REQ_REL)
    stories_path = args.stories or os.path.join(docs, STORIES_REL)
    try:
        result = build_report(
            requirements_path,
            stories_path,
            args.expect_active_fr,
            args.expect_deferred_fr,
            args.expect_story,
        )
    except MatrixError as exc:
        error = {
            "kind": "error",
            "code": exc.code,
            "message": exc.message,
            "hint": exc.hint,
            "timestamp": _now_iso(),
        }
        sys.stdout.write(json.dumps(error, indent=2) + "\n")
        return 1
    except Exception as exc:  # last-resort: keep the JSON output contract
        error = {
            "kind": "error",
            "code": "internal",
            "message": "Unexpected trace-matrix failure: %s: %s"
            % (type(exc).__name__, exc),
            "hint": "This is a tool bug or an environment problem. If it "
            "persists, report it with the command line you ran.",
            "timestamp": _now_iso(),
        }
        sys.stdout.write(json.dumps(error, indent=2) + "\n")
        return 1
    result["timestamp"] = _now_iso()
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
