#!/usr/bin/env python3
"""Unit tests for the traceability matrix tool (trace-matrix.py).

Run from the repository root:

    python -m unittest discover -s .agents\\skills\\aidlc-workflows\\scripts\\tests

Pure standard library. The module under test is loaded by absolute path
via importlib (the file name contains a hyphen, so it cannot be imported
normally). CLI-level tests run in-process against throwaway temporary
fixtures; no real dogfood files are read or written.
"""

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)


def _load_tool():
    path = os.path.join(SCRIPTS_DIR, "trace-matrix.py")
    spec = importlib.util.spec_from_file_location("trace_matrix", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = _load_tool()

ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _run_main(argv):
    """Run tool.main in-process, capturing JSON stdout (CLI surface)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            code = tool.main(["trace-matrix.py"] + argv)
        except SystemExit as exc:  # argparse usage-error path exits directly
            code = exc.code if isinstance(exc.code, int) else 2
    return code, json.loads(buffer.getvalue())


REQUIREMENTS_MD = """\
# Requirements
## A. Modes
- **FR-01 Mode enum**: state machine manages modes
- **FR-02 MENU**: mode list
- **FR-10 Type select**: choose 1-Var or regression
- **FR-11 Editor**: data editor
- **FR-14 Regression coeffs**: coefficients and statistics
- **FR-15 Estimate**: y-hat estimate
## D. TABLE —— **Deferred（moved out of this iteration）**
- **FR-30（Deferred）function input**: f(x)/g(x)
- **FR-31（Deferred）range**: Start/End/Step
"""

STORIES_MD = """\
# Stories
## One
### US2-01 Mode switching
**追溯**: FR-01、FR-02
## Four —— **Deferred**
### US2-12（Deferred）Table input
**追溯**: FR-30、FR-99
## Five
### US2-20 Slash shorthand
**追溯**: FR-10/11/14/15、BR-01
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.docs = tempfile.mkdtemp(prefix="aidlc-trace-test-")
        self.addCleanup(shutil.rmtree, self.docs, True)

    def write(self, rel, text):
        path = os.path.join(self.docs, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return path

    def run_default(self, *extra):
        self.write("inception/requirements/requirements.md", REQUIREMENTS_MD)
        self.write("inception/user-stories/stories.md", STORIES_MD)
        return _run_main(["--docs", self.docs] + list(extra))

    def matrix_entry(self, report, fr):
        for entry in report["matrix"]:
            if entry["fr"] == fr:
                return entry
        self.fail("matrix has no entry for %s" % fr)


# ---------------------------------------------------------------------------
# CLI-level behaviour (default fixture)
# ---------------------------------------------------------------------------


class MatrixTests(FixtureCase):
    def test_success_payload_shape(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        self.assertEqual(report["tool"], "trace-matrix")
        self.assertRegex(report["timestamp"], ISO_UTC_RE)
        self.assertEqual(report["requirements"]["fr_total"], 8)
        self.assertEqual(report["requirements"]["fr_active"], 6)
        self.assertEqual(
            report["requirements"]["fr_deferred"], ["FR-30", "FR-31"]
        )
        self.assertEqual(report["stories"]["story_total"], 3)
        self.assertEqual(report["stories"]["story_active"], 2)
        self.assertEqual(report["stories"]["story_deferred"], ["US2-12"])

    def test_covered_active_fr(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        entry = self.matrix_entry(report, "FR-01")
        self.assertEqual(entry["status"], "covered")
        self.assertFalse(entry["deferred"])
        self.assertEqual(entry["stories"], ["US2-01"])

    def test_uncovered_active_fr(self):
        self.write(
            "inception/requirements/requirements.md",
            "# Requirements\n- **FR-01 A**: a\n- **FR-02 B**: b\n",
        )
        self.write(
            "inception/user-stories/stories.md",
            "# Stories\n### US2-01 S\n**追溯**: FR-01\n",
        )
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 0)
        self.assertEqual(report["uncovered_active_frs"], ["FR-02"])
        self.assertEqual(
            self.matrix_entry(report, "FR-02")["status"], "uncovered"
        )

    def test_inline_deferred_fullwidth_parens(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        entry = self.matrix_entry(report, "FR-30")
        self.assertTrue(entry["deferred"])
        self.assertEqual(entry["status"], "deferred")
        # a deferred FR still lists the stories that trace it
        self.assertEqual(entry["stories"], ["US2-12"])
        self.assertNotIn("FR-30", report["uncovered_active_frs"])

    def test_heading_inherited_deferred(self):
        # The FR line itself carries NO Deferred marker; the nearest
        # preceding heading does. Same inheritance for a story heading,
        # plus the ``**Trace**：`` label variant with a full-width colon.
        self.write(
            "inception/requirements/requirements.md",
            "# Requirements\n"
            "## D. TABLE —— **Deferred（moved out）**\n"
            "- **FR-31 range**: Start/End/Step\n"
            "## E. Base\n"
            "- **FR-40 active**: keep\n",
        )
        self.write(
            "inception/user-stories/stories.md",
            "# Stories\n"
            "## Four —— **Deferred**\n"
            "### US2-31 Table\n"
            "**Trace**： FR-31\n"
            "## Five\n"
            "### US2-40 Other\n"
            "**Trace**: FR-40\n",
        )
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 0)
        self.assertEqual(report["requirements"]["fr_deferred"], ["FR-31"])
        self.assertEqual(
            self.matrix_entry(report, "FR-31")["status"], "deferred"
        )
        self.assertEqual(
            self.matrix_entry(report, "FR-31")["stories"], ["US2-31"]
        )
        self.assertEqual(
            self.matrix_entry(report, "FR-40")["status"], "covered"
        )
        self.assertEqual(report["stories"]["story_deferred"], ["US2-31"])

    def test_entry_heading_deferred_does_not_propagate_to_sibling(self):
        # Back-to-back story headings: only the first carries （Deferred）,
        # so the second must stay active. Section-level inheritance still
        # works, and an FR-ID heading propagates to neither its own FR
        # bullet nor the next one (entry-level Deferred belongs on the
        # entry line itself).
        self.write(
            "inception/requirements/requirements.md",
            "# Requirements\n"
            "## D. TABLE —— **Deferred（moved out）**\n"
            "- **FR-31 range**: Start/End/Step\n"
            "## E. Base\n"
            "- **FR-40 active**: keep\n"
            "## G. Named-entry heading\n"
            "### FR-50（Deferred）special\n"
            "- **FR-50 x**: x\n"
            "- **FR-51 y**: y\n",
        )
        self.write(
            "inception/user-stories/stories.md",
            "# Stories\n"
            "## Seven — e2e sessions\n"
            "### US2-24（Deferred）Table e2e\n"
            "**追溯**: FR-31\n"
            "### US2-25 Base e2e\n"
            "**追溯**: FR-40\n"
            "## Nine —— **Deferred** section\n"
            "### US2-31 Table input\n"
            "**追溯**: FR-31\n",
        )
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 0)
        # sibling of a Deferred story stays active; section-level
        # inheritance (## Nine —— **Deferred**) still applies to US2-31
        self.assertEqual(
            report["stories"]["story_deferred"], ["US2-24", "US2-31"]
        )
        self.assertEqual(report["stories"]["story_active"], 1)
        # section heading defers FR-31; the FR-50-ID heading defers
        # neither FR-50 nor FR-51
        self.assertEqual(report["requirements"]["fr_deferred"], ["FR-31"])
        self.assertEqual(
            self.matrix_entry(report, "FR-40")["status"], "covered"
        )

    def test_slash_shorthand_trace(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        for fr in ("FR-10", "FR-11", "FR-14", "FR-15"):
            entry = self.matrix_entry(report, fr)
            self.assertEqual(entry["stories"], ["US2-20"], fr)
            self.assertEqual(entry["status"], "covered", fr)
        # the non-FR segment (BR-01) is ignored entirely: FR-01 keeps only
        # its own story, and no matrix entry picks up US2-20 from BR-01/05
        self.assertEqual(self.matrix_entry(report, "FR-01")["stories"],
                         ["US2-01"])

    def test_dangling_trace_reference(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        self.assertEqual(
            report["dangling_trace_references"],
            [{"fr": "FR-99", "stories": ["US2-12"]}],
        )

    def test_scope_leak_active_story_traces_deferred_fr(self):
        self.write(
            "inception/requirements/requirements.md",
            "# Requirements\n- **FR-01 A**: a\n- **FR-30（Deferred）B**: b\n",
        )
        self.write(
            "inception/user-stories/stories.md",
            "# Stories\n### US2-01 Story\n**追溯**: FR-01、FR-30\n",
        )
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 0)
        self.assertEqual(
            report["scope_leaks"], [{"fr": "FR-30", "stories": ["US2-01"]}]
        )

    def test_no_scope_leak_when_deferred_story_traces_deferred_fr(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        self.assertEqual(report["scope_leaks"], [])

    def test_count_checks_mismatch_then_match(self):
        code, report = self.run_default("--expect-active-fr", "5")
        self.assertEqual(code, 0)
        self.assertEqual(
            report["count_checks"],
            [{"check": "active_fr", "declared": 5, "actual": 6,
              "match": False}],
        )
        code, report = self.run_default(
            "--expect-active-fr", "6",
            "--expect-deferred-fr", "2",
            "--expect-story", "3",
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            [c["check"] for c in report["count_checks"]],
            ["active_fr", "deferred_fr", "story"],
        )
        self.assertEqual([c["match"] for c in report["count_checks"]],
                         [True, True, True])

    def test_count_checks_omitted_when_not_requested(self):
        code, report = self.run_default()
        self.assertEqual(code, 0)
        self.assertEqual(report["count_checks"], [])

    def test_missing_requirements_file(self):
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 1)
        self.assertEqual(report["kind"], "error")
        self.assertEqual(report["code"], "missing-file")
        self.assertIn("requirements.md", report["message"])
        self.assertRegex(report["timestamp"], ISO_UTC_RE)

    def test_missing_stories_file(self):
        self.write("inception/requirements/requirements.md",
                   "# Requirements\n")
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 1)
        self.assertEqual(report["kind"], "error")
        self.assertEqual(report["code"], "missing-file")

    def test_explicit_paths_override_docs(self):
        self.write("inception/requirements/requirements.md",
                   "# Requirements\n- **FR-01 A**: a\n")
        self.write("inception/user-stories/stories.md", "# Stories\n")
        req = self.write("custom/req.md", "# R\n- **FR-09 X**: x\n")
        sto = self.write("custom/sto.md",
                         "# S\n### US-01 S\n**追溯**: FR-09\n")
        code, report = _run_main(
            ["--docs", self.docs, "--requirements", req, "--stories", sto]
        )
        self.assertEqual(code, 0)
        self.assertEqual(report["requirements"]["fr_total"], 1)
        self.assertEqual(report["stories"]["story_total"], 1)

    def test_usage_error_is_json(self):
        code, report = _run_main(["--expect-active-fr", "abc"])
        self.assertEqual(code, 1)
        self.assertEqual(report["kind"], "error")
        self.assertEqual(report["code"], "usage")
        code, report = _run_main(["--bogus"])
        self.assertEqual(code, 1)
        self.assertEqual(report["code"], "usage")


# ---------------------------------------------------------------------------
# Matrix ordering
# ---------------------------------------------------------------------------


class OrderingTests(FixtureCase):
    def test_matrix_sorted_numerically(self):
        # FR-99 vs FR-100 distinguishes numeric from lexicographic order
        # (lexicographic would place FR-100 before FR-99).
        self.write(
            "inception/requirements/requirements.md",
            "# Requirements\n"
            "- **FR-99 ninety-nine**: x\n"
            "- **FR-100 hundred**: x\n"
            "- **FR-9 nine**: x\n",
        )
        self.write(
            "inception/user-stories/stories.md",
            "# Stories\n### US-01 S\n**追溯**: FR-9\n",
        )
        code, report = _run_main(["--docs", self.docs])
        self.assertEqual(code, 0)
        self.assertEqual(
            [entry["fr"] for entry in report["matrix"]],
            ["FR-09", "FR-99", "FR-100"],
        )


# ---------------------------------------------------------------------------
# Parser unit tests
# ---------------------------------------------------------------------------


class ParserUnitTests(unittest.TestCase):
    def test_duplicate_fr_first_occurrence_wins(self):
        frs = tool.parse_requirements(
            "# R\n"
            "- **FR-01 A**: a\n"
            "- **FR-01 B**: b\n"
            "## X —— **Deferred**\n"
            "- **FR-01 C**: c\n"
        )
        self.assertEqual(frs, {1: False})

    def test_extract_fr_refs_shorthands(self):
        self.assertEqual(
            tool._extract_fr_refs("FR-10/11/14/15、BR-01"),
            [10, 11, 14, 15],
        )
        self.assertEqual(
            tool._extract_fr_refs("FR-04、FR-41（partial）"), [4, 41]
        )
        self.assertEqual(tool._extract_fr_refs("验收场景 3/4"), [])
        self.assertEqual(
            tool._extract_fr_refs("FR-01，FR-02; FR-03；FR-04, FR-05"),
            [1, 2, 3, 4, 5],
        )
        # bare pieces only inherit when the segment STARTS with FR-
        self.assertEqual(tool._extract_fr_refs("BR-01/05"), [])
        # tilde ranges expand to every FR in the span (fx991 artifact style)
        self.assertEqual(
            tool._extract_fr_refs("FR-30~34、验收场景 5"),
            [30, 31, 32, 33, 34],
        )
        self.assertEqual(
            tool._extract_fr_refs("FR-40~44、BR-01/05"),
            [40, 41, 42, 43, 44],
        )
        # spans beyond the cap (or inverted) stay untouched -> only the
        # first number registers, exactly as before
        self.assertEqual(tool._extract_fr_refs("FR-1~9999"), [1])
        self.assertEqual(tool._extract_fr_refs("FR-34~30"), [34])

    def test_trace_label_variants(self):
        stories, traces = tool.parse_stories(
            "# S\n"
            "### US-01 A\n"
            "**Trace**： FR-01\n"
            "### US2-02 B\n"
            "**追溯**: FR-01/02\n"
        )
        self.assertEqual(traces["US-01"], {1})
        self.assertEqual(traces["US2-02"], {1, 2})

    def test_story_heading_first_id_token_wins(self):
        # A placeholder heading must resolve to US2-21, not to US2-19
        # from the merge note inside the parentheses.
        stories, traces = tool.parse_stories(
            "# S\n### US2-21（已并入 US2-19/20 —— 保留编号占位说明）\n"
        )
        self.assertEqual(list(stories), ["US2-21"])
        self.assertEqual(traces, {})

    def test_trace_before_any_story_heading_is_ignored(self):
        stories, traces = tool.parse_stories(
            "# S\n**追溯**: FR-01\n### US-01 A\n"
        )
        self.assertEqual(list(stories), ["US-01"])
        self.assertEqual(traces, {})


if __name__ == "__main__":
    unittest.main()
