#!/usr/bin/env python3
"""Unit tests for the runtime orchestration engine (engine.py).

Run from the repository root:

    python -m unittest discover -s scripts\\tests -v

Pure standard library. The module under test is loaded by absolute path via
importlib (``scripts`` is intentionally not a package). Every test runs
against a throwaway temporary workspace; the real skill tree is only read
(scripts/data/stage-graph.json), never written.
"""

import importlib.util
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
ENGINE_PATH = os.path.join(SCRIPTS_DIR, "engine.py")
SKILL_ROOT = os.path.dirname(SCRIPTS_DIR)


def _load_engine():
    spec = importlib.util.spec_from_file_location("aidlc_engine", ENGINE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


engine = _load_engine()

ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

STAGE_ORDER = [
    "workspace-detection",
    "reverse-engineering",
    "requirements-analysis",
    "user-stories",
    "workflow-planning",
    "application-design",
    "units-generation",
    "functional-design",
    "nfr-requirements",
    "nfr-design",
    "infrastructure-design",
    "code-generation",
    "build-and-test",
    "operations",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class WorkspaceCase(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.mkdtemp(prefix="aidlc-engine-test-")
        self.addCleanup(shutil.rmtree, self.workspace, True)
        self.graph = engine.load_graph()

    # -- file helpers -----------------------------------------------------

    def _path(self, *parts):
        return os.path.join(self.workspace, *parts)

    def state_text(self):
        with open(self._path("aidlc-docs", "aidlc-state.md"),
                  encoding="utf-8") as handle:
            return handle.read()

    def audit_text(self):
        with open(self._path("aidlc-docs", "audit.md"),
                  encoding="utf-8") as handle:
            return handle.read()

    def write_state(self, text):
        path = self._path("aidlc-docs", "aidlc-state.md")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)

    def set_plan_lines(self, scope=None, depth=None, execute=None, skip=None):
        """Fill the model-owned Execution Plan Summary placeholders."""
        text = self.state_text()
        if scope is not None:
            text = re.sub(
                r"- \*\*Scope\*\*: .*",
                "- **Scope**: " + scope,
                text,
            )
        if depth is not None:
            text = re.sub(
                r"- \*\*Depth\*\*: .*",
                "- **Depth**: " + depth,
                text,
            )
        if execute is not None:
            text = re.sub(
                r"- \*\*Stages to Execute\*\*: .*",
                "- **Stages to Execute**: " + execute,
                text,
            )
        if skip is not None:
            text = re.sub(
                r"- \*\*Stages to Skip\*\*: .*",
                "- **Stages to Skip**: " + skip,
                text,
            )
        self.write_state(text)

    # -- engine invocations ------------------------------------------------

    def init(self):
        return engine.cmd_init(self.workspace)

    def status(self):
        return engine.cmd_status(self.workspace)

    def next(self):
        return engine.cmd_next(self.workspace)

    def report(self, slug, result, reason=None):
        return engine.cmd_report(self.workspace, slug, result, reason)

    def jump(self, slug=None, fresh=False):
        return engine.cmd_jump(self.workspace, slug, fresh)

    def rebase(self):
        return engine.cmd_rebase(self.workspace)

    def marks(self):
        state = engine.load_state(self.graph, self.workspace)
        return dict(state.marks)

    def assert_error(self, fn, code):
        with self.assertRaises(engine.EngineError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def drive_past(self, slug):
        """Report the given stage done with the appropriate result."""
        stage = None
        for item in self.graph["stages"]:
            if item["slug"] == slug:
                stage = item
        self.assertIsNotNone(stage)
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")
        self.assertEqual(directive["stage"], slug)
        if stage["gate"] == "none":
            self.report(slug, "completed")
        else:
            self.report(slug, "approved")

    def park(self, note):
        return engine.cmd_park(self.workspace, note)

    def handoff_text(self):
        path = self._path("aidlc-docs", "handoff.md")
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def make_doc(self, rel, content="content\n"):
        """Create a file under aidlc-docs/ (rel uses / separators)."""
        path = self._path("aidlc-docs", *rel.split("/"))
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)

    def route_to(self, target):
        """Plan-skip everything except workspace-detection and target."""
        skip = [
            slug for slug in STAGE_ORDER
            if slug not in ("workspace-detection", target)
        ]
        self.set_plan_lines(skip=", ".join(skip))
        self.report("workspace-detection", "completed")
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")
        self.assertEqual(directive["stage"], target)


# ---------------------------------------------------------------------------
# init / status
# ---------------------------------------------------------------------------


class InitTests(WorkspaceCase):
    def test_status_without_state(self):
        result = self.status()
        self.assertEqual(result["engine"], "ok")
        self.assertEqual(result["state"], "none")
        self.assertIsNone(result["current_stage"])
        self.assertEqual(result["completed"], [])

    def test_fresh_init_has_no_resumed_alerts_for_engine_files(self):
        # Load-bearing: right after init the current stage is
        # workspace-detection, whose produces are exactly the engine files
        # (aidlc-state.md, audit.md) — both freshly created. If the
        # engine-file exclusion were ever removed, resumed-artifacts would
        # fire here and this assertion would fail.
        self.init()
        result = self.status()
        self.assertEqual(result["artifact_alerts"], [])
        self.assertFalse(result["alerts_unavailable"])

    def test_init_creates_state_and_audit(self):
        result = self.init()
        self.assertEqual(result["kind"], "initialized")
        self.assertTrue(os.path.isfile(
            self._path("aidlc-docs", "aidlc-state.md")))
        self.assertTrue(os.path.isfile(self._path("aidlc-docs", "audit.md")))
        text = self.state_text()
        self.assertIn("<!-- BEGIN ENGINE-STATE", text)
        self.assertIn("## Execution Plan Summary", text)
        self.assertIn("sha256: ", text)
        for slug in STAGE_ORDER:
            self.assertIn("- [ ] " + slug, text)
        self.assertIn("STATE_CREATED", self.audit_text())

    def test_init_twice_errors(self):
        self.init()
        self.assert_error(self.init, "state-exists")

    def test_status_after_init(self):
        self.init()
        result = self.status()
        self.assertEqual(result["state"], "active")
        self.assertEqual(result["current_stage"], "workspace-detection")
        self.assertEqual(result["scope"], "classic")
        self.assertEqual(result["integrity"], "ok")
        self.assertEqual(len(result["remaining"]), len(STAGE_ORDER))

    def test_legacy_state_detected(self):
        os.makedirs(self._path("aidlc-docs"))
        self.write_state("# AI-DLC State Tracking\n\n- old style file\n")
        result = self.status()
        self.assertEqual(result["state"], "legacy")
        self.assert_error(self.next, "legacy-state")

    def test_truncated_state_detected_as_corrupt(self):
        # BEGIN present, END lost (e.g. tail truncation): corruption, not
        # legacy — legacy requires NO marker at all.
        self.init()
        text = self.state_text()
        kept = [
            line for line in text.split("\n")
            if not line.startswith("<!-- END ENGINE-STATE")
        ]
        self.write_state("\n".join(kept))
        result = self.status()
        self.assertEqual(result["state"], "corrupt")
        self.assertEqual(result["integrity"], "violated")
        self.assert_error(self.next, "state-corrupt")

    def test_lone_end_marker_detected_as_corrupt(self):
        self.init()
        text = self.state_text()
        kept = [
            line for line in text.split("\n")
            if not line.startswith("<!-- BEGIN ENGINE-STATE")
        ]
        self.write_state("\n".join(kept))
        self.assertEqual(self.status()["state"], "corrupt")

    def test_fresh_still_recovers_corrupt_state(self):
        self.init()
        text = self.state_text()
        kept = [
            line for line in text.split("\n")
            if not line.startswith("<!-- END ENGINE-STATE")
        ]
        self.write_state("\n".join(kept))
        ack = self.jump(fresh=True)
        self.assertEqual(ack["kind"], "fresh")
        self.assertEqual(self.status()["state"], "none")


# ---------------------------------------------------------------------------
# Routing (next)
# ---------------------------------------------------------------------------


class RoutingTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_first_directive(self):
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")
        self.assertEqual(directive["stage"], "workspace-detection")
        self.assertEqual(directive["gate"], "none")
        self.assertEqual(directive["phase"], "inception")
        self.assertFalse(directive["conditional"])
        self.assertEqual(directive["next_stage"], "reverse-engineering")
        self.assertEqual(
            directive["stage_file"],
            "references/inception/workspace-detection.md",
        )

    def test_conditional_flag(self):
        self.drive_past("workspace-detection")
        directive = self.next()
        self.assertEqual(directive["stage"], "reverse-engineering")
        self.assertTrue(directive["conditional"])

    def test_scope_filtering(self):
        self.set_plan_lines(scope="bugfix")
        slugs = []
        while True:
            directive = self.next()
            if directive["kind"] == "done":
                break
            slug = directive["stage"]
            slugs.append(slug)
            stage = engine._stage_by_slug(self.graph, slug)
            if directive["conditional"]:
                self.report(slug, "skipped", reason="not applicable")
            elif stage["gate"] == "none":
                self.report(slug, "completed")
            else:
                self.report(slug, "approved")
        # bugfix scope prunes user-stories / application-design /
        # units-generation / most conditional construction stages.
        self.assertNotIn("user-stories", slugs)
        self.assertNotIn("application-design", slugs)
        self.assertNotIn("functional-design", slugs)
        self.assertIn("code-generation", slugs)
        self.assertIn("build-and-test", slugs)

    def test_plan_skip_overrides(self):
        self.set_plan_lines(skip="user-stories (no UX), application-design")
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        self.drive_past("requirements-analysis")
        directive = self.next()
        self.assertEqual(directive["stage"], "workflow-planning")

    def test_plan_execute_adds_back_scope_skip(self):
        self.set_plan_lines(scope="bugfix", execute="user-stories")
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        self.drive_past("requirements-analysis")
        directive = self.next()
        self.assertEqual(directive["stage"], "user-stories")

    def test_skip_line_wins_over_execute_line(self):
        # Precedence rule 1: a slug on the Skip line stays out even when
        # the Execute line also lists it — an add-back must remove the
        # Skip entry first.
        self.set_plan_lines(skip="user-stories (deferred)",
                            execute="user-stories")
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        self.drive_past("requirements-analysis")
        directive = self.next()
        self.assertEqual(directive["stage"], "workflow-planning")

    def test_report_before_skip_line_for_conditional_current(self):
        # Correct order for skipping the current CONDITIONAL stage:
        # report the formal skip while it is still current, THEN persist
        # the Skip line. Routing and integrity both stay healthy.
        self.drive_past("workspace-detection")
        ack = self.report("reverse-engineering", "skipped",
                          "greenfield, no legacy code")
        self.assertEqual(ack["current_stage"], "requirements-analysis")
        self.assertEqual(self.marks()["reverse-engineering"], "S")
        self.set_plan_lines(skip="reverse-engineering (greenfield)")
        self.assertEqual(self.status()["integrity"], "ok")
        directive = self.next()
        self.assertEqual(directive["stage"], "requirements-analysis")

    def test_skip_line_before_report_is_rejected(self):
        # The inverse order is an intentional failure: once the Skip line
        # is written, the pointer re-routes past the stage and the report
        # is no longer addressable.
        self.drive_past("workspace-detection")
        self.set_plan_lines(skip="reverse-engineering (greenfield)")
        self.assert_error(
            lambda: self.report("reverse-engineering", "skipped",
                                "greenfield"),
            "invalid-transition",
        )
        directive = self.next()
        self.assertEqual(directive["stage"], "requirements-analysis")

    def test_unknown_plan_slug_rejected(self):
        self.set_plan_lines(skip="not-a-stage")
        self.assert_error(self.next, "plan-invalid")

    def test_unknown_scope_rejected(self):
        self.set_plan_lines(scope="not-a-scope")
        self.assert_error(self.next, "plan-invalid")

    def test_done_directive(self):
        for slug in STAGE_ORDER:
            directive = self.next()
            if directive["kind"] == "done":
                break
            stage = engine._stage_by_slug(self.graph, directive["stage"])
            if directive["conditional"]:
                self.report(
                    directive["stage"], "skipped", reason="not applicable"
                )
            elif stage["gate"] == "none":
                self.report(directive["stage"], "completed")
            else:
                self.report(directive["stage"], "approved")
        self.assertEqual(self.next()["kind"], "done")
        result = self.status()
        self.assertEqual(result["state"], "completed")
        self.assertIsNone(result["current_stage"])

    def test_next_stage_is_prediction(self):
        # Skipping reverse-engineering (conditional) must not change the
        # routing of requirements-analysis; next_stage only predicts.
        self.drive_past("workspace-detection")
        self.report(
            "reverse-engineering", "skipped", reason="greenfield"
        )
        directive = self.next()
        self.assertEqual(directive["stage"], "requirements-analysis")
        self.assertEqual(directive["next_stage"], "user-stories")

    def test_plan_skip_reason_with_comma_recovers_slug(self):
        # A reason annotation containing a comma must not shear the slug in
        # two and trip unknown-slug rejection.
        self.set_plan_lines(
            skip="infrastructure-design (pure frontend, no infra), "
            "nfr-design (single unit, no distributed concerns)"
        )
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(
            plan.skip, {"infrastructure-design", "nfr-design"}
        )

    def test_plan_skip_reason_with_comma_routes(self):
        self.set_plan_lines(skip="user-stories (no UX research, none planned)")
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(plan.skip, {"user-stories"})
        self.assertEqual(self.next()["kind"], "run-stage")

    def test_plan_skip_no_comma_regression(self):
        self.set_plan_lines(skip="user-stories (no UX), application-design")
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(plan.skip, {"user-stories", "application-design"})

    def test_plan_skip_none_sentinel_regression(self):
        self.set_plan_lines(skip="none")
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(plan.skip, set())

    def test_unknown_plan_slug_with_commaed_reason_rejected(self):
        self.set_plan_lines(skip="not-a-stage (because, reasons)")
        self.assert_error(self.next, "plan-invalid")

    def _rename_plan_header(self):
        """Rename the exact section header to simulate a model reword."""
        text = self.state_text().replace(
            "## Execution Plan Summary", "## Execution Plan"
        )
        self.write_state(text)

    def test_missing_plan_header_with_filled_lines_rejected(self):
        # A filled plan line exists but the exact header is gone: routing can
        # no longer consume it, so this must surface instead of silently
        # falling back to the scope baseline.
        self.set_plan_lines(skip="user-stories (no UX)")
        self._rename_plan_header()
        error = self.assert_error(self.next, "plan-invalid")
        self.assertIn("Stages to Skip", error.message)

    def test_exact_header_with_informational_copy_routes(self):
        # The exact header is present, so a copy elsewhere is informational
        # and must not disturb routing.
        self.set_plan_lines(skip="user-stories (no UX)")
        text = self.state_text().replace(
            "## Project Information",
            "## Project Information\n"
            "- **Stages to Skip**: user-stories (informational copy)",
        )
        self.write_state(text)
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(plan.skip, {"user-stories"})
        self.assertEqual(self.next()["kind"], "run-stage")

    def test_missing_plan_header_with_placeholder_lines_ok(self):
        # Untouched placeholders (bracketed values) are not "plan lines", so
        # a renamed header must not trip the check.
        self._rename_plan_header()
        self.assertEqual(self.next()["kind"], "run-stage")

    def test_filled_plan_lines_with_exact_header_ok(self):
        self.set_plan_lines(execute="user-stories", skip="application-design")
        plan = engine.load_state(self.graph, self.workspace).plan
        self.assertEqual(plan.execute, {"user-stories"})
        self.assertEqual(plan.skip, {"application-design"})
        self.assertEqual(self.next()["kind"], "run-stage")


# ---------------------------------------------------------------------------
# Tolerant slug-list parsing (_slug_list)
# ---------------------------------------------------------------------------


class SlugListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.known = set(s["slug"] for s in engine.load_graph()["stages"])

    def parse(self, value):
        return engine._slug_list(value, self.known)

    def test_plain_list(self):
        self.assertEqual(
            self.parse("user-stories, application-design"),
            ["user-stories", "application-design"],
        )

    def test_reason_without_comma(self):
        self.assertEqual(
            self.parse("user-stories (no UX), application-design"),
            ["user-stories", "application-design"],
        )

    def test_reason_with_comma(self):
        self.assertEqual(
            self.parse("infrastructure-design (pure frontend, no infra)"),
            ["infrastructure-design"],
        )

    def test_reason_with_multiple_commas(self):
        self.assertEqual(
            self.parse("nfr-design (no perf, scale, or availability goals)"),
            ["nfr-design"],
        )

    def test_none_sentinel(self):
        self.assertEqual(self.parse("none"), [])

    def test_unknown_leftover_surfaces_for_rejection(self):
        self.assertEqual(
            self.parse("not-a-stage (because, reasons)"), ["not-a-stage"]
        )


# ---------------------------------------------------------------------------
# report transition matrix
# ---------------------------------------------------------------------------


class TransitionTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_completed_advances(self):
        self.report("workspace-detection", "completed")
        self.assertEqual(self.marks()["workspace-detection"], "x")
        self.assertEqual(self.next()["stage"], "reverse-engineering")
        self.assertIn("STAGE_COMPLETED", self.audit_text())

    def test_completed_rejected_for_gated_stage(self):
        self.drive_past("workspace-detection")
        self.assert_error(
            lambda: self.report("reverse-engineering", "completed"),
            "invalid-transition",
        )

    def test_approved_rejected_for_gateless_stage(self):
        self.assert_error(
            lambda: self.report("workspace-detection", "approved"),
            "invalid-transition",
        )

    def test_approved_advances(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "approved")
        self.assertEqual(self.marks()["reverse-engineering"], "x")
        self.assertIn("STAGE_APPROVED", self.audit_text())

    def test_rejected_stays(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "rejected")
        self.assertEqual(self.marks()["reverse-engineering"], "R")
        self.assertEqual(self.next()["stage"], "reverse-engineering")
        # Can later approve the same stage.
        self.report("reverse-engineering", "approved")
        self.assertEqual(self.marks()["reverse-engineering"], "x")

    def test_revised_stays(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "revised")
        self.assertEqual(self.marks()["reverse-engineering"], "?")
        self.assertEqual(self.next()["stage"], "reverse-engineering")

    def test_skipped_requires_reason(self):
        self.drive_past("workspace-detection")
        self.assert_error(
            lambda: self.report("reverse-engineering", "skipped"),
            "invalid-transition",
        )

    def test_skipped_conditional(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "skipped", reason="greenfield")
        self.assertEqual(self.marks()["reverse-engineering"], "S")
        self.assertIn("greenfield", self.audit_text())

    def test_skipped_rejected_for_always_stage(self):
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        self.assert_error(
            lambda: self.report(
                "requirements-analysis", "skipped", reason="trying"
            ),
            "invalid-transition",
        )

    def test_report_out_of_turn_rejected(self):
        self.assert_error(
            lambda: self.report("build-and-test", "approved"),
            "invalid-transition",
        )

    def test_unknown_stage_rejected(self):
        self.assert_error(
            lambda: self.report("not-a-stage", "completed"),
            "unknown-stage",
        )

    def test_atomic_write_no_temp_leak(self):
        self.report("workspace-detection", "completed")
        leftovers = [
            name
            for name in os.listdir(self._path("aidlc-docs"))
            if name.startswith(".aidlc-engine-")
        ]
        self.assertEqual(leftovers, [])


# ---------------------------------------------------------------------------
# Integrity
# ---------------------------------------------------------------------------


class IntegrityTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.drive_past("workspace-detection")

    def _tamper_checkbox(self):
        text = self.state_text()
        text = text.replace(
            "- [ ] requirements-analysis", "- [x] requirements-analysis"
        )
        self.write_state(text)

    def test_hand_edit_detected_by_status(self):
        self._tamper_checkbox()
        self.assertEqual(self.status()["integrity"], "violated")

    def test_hand_edit_halts_next(self):
        self._tamper_checkbox()
        self.assert_error(self.next, "integrity-violated")

    def test_hand_edit_halts_report(self):
        self._tamper_checkbox()
        self.assert_error(
            lambda: self.report("reverse-engineering", "approved"),
            "integrity-violated",
        )

    def test_rebase_restores(self):
        self._tamper_checkbox()
        self.assertEqual(self.status()["integrity"], "violated")
        self.rebase()
        self.assertEqual(self.status()["integrity"], "ok")
        self.assertIn("STATE_REBASELINED", self.audit_text())
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")

    def test_model_region_edit_does_not_halt(self):
        # Model-owned regions are deliberately outside the digest.
        text = self.state_text()
        text = text.replace(
            "- **Project Type**: [Greenfield/Brownfield]",
            "- **Project Type**: Greenfield",
        )
        text = text.replace(
            "- **Scope**: [selected at Requirements Analysis]",
            "- **Scope**: bugfix",
        )
        self.write_state(text)
        self.assertEqual(self.status()["integrity"], "ok")
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")

    def test_crlf_line_endings_keep_digest_stable(self):
        # A state file checked out / saved with CRLF must not read as drift.
        text = self.state_text().replace("\n", "\r\n")
        self.write_state(text)
        self.assertEqual(self.status()["integrity"], "ok")
        directive = self.next()
        self.assertEqual(directive["kind"], "run-stage")

    def test_audit_crosscheck(self):
        # Mark is digest-consistent but the audit entry is missing.
        self.rebase()  # baseline current state first
        text = self.state_text()
        text = text.replace(
            "- [ ] requirements-analysis", "- [x] requirements-analysis"
        )
        self.write_state(text)
        self.rebase()  # re-digest the tampered checkboxes
        # Remove all audit events so the cross-check has nothing to match
        # and the rebase exemption no longer applies.
        audit_path = self._path("aidlc-docs", "audit.md")
        with open(audit_path, "w", encoding="utf-8", newline="") as handle:
            handle.write("# AI-DLC Audit Log\n")
        self.assertEqual(self.status()["integrity"], "violated")


# ---------------------------------------------------------------------------
# jump
# ---------------------------------------------------------------------------


class JumpTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_backward_jump_resets(self):
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        self.drive_past("requirements-analysis")
        ack = self.jump(slug="reverse-engineering")
        self.assertEqual(ack["direction"], "backward")
        self.assertEqual(ack["to"], "reverse-engineering")
        marks = self.marks()
        self.assertEqual(marks["workspace-detection"], "x")
        self.assertEqual(marks["reverse-engineering"], " ")
        self.assertEqual(marks["requirements-analysis"], " ")
        self.assertEqual(self.next()["stage"], "reverse-engineering")
        self.assertIn("STAGE_JUMPED", self.audit_text())
        self.assertEqual(self.status()["integrity"], "ok")

    def test_forward_jump_marks_intermediates(self):
        self.drive_past("workspace-detection")
        ack = self.jump(slug="workflow-planning")
        self.assertEqual(ack["direction"], "forward")
        marks = self.marks()
        self.assertEqual(marks["reverse-engineering"], "S")
        self.assertEqual(marks["requirements-analysis"], "S")
        self.assertEqual(marks["user-stories"], "S")
        self.assertEqual(marks["workflow-planning"], " ")
        self.assertEqual(self.status()["integrity"], "ok")

    def test_jump_to_current_rejected(self):
        self.assert_error(
            lambda: self.jump(slug="workspace-detection"), "invalid-jump"
        )

    def test_jump_unknown_stage(self):
        self.assert_error(lambda: self.jump(slug="nope"), "unknown-stage")

    def test_jump_to_out_of_plan_stage_notes(self):
        self.set_plan_lines(scope="bugfix")
        self.drive_past("workspace-detection")
        ack = self.jump(slug="user-stories")
        self.assertIn("note", ack)

    def test_jump_to_completed_stage_is_backward_redo(self):
        # Jumping "forward" onto an already-completed stage is treated as a
        # redo of that stage (target index < current index).
        self.drive_past("workspace-detection")
        self.drive_past("reverse-engineering")
        ack = self.jump(slug="workspace-detection")
        self.assertEqual(ack["direction"], "backward")
        self.assertEqual(self.marks()["workspace-detection"], " ")
        self.assertEqual(self.next()["stage"], "workspace-detection")

    def test_jump_fresh_archives(self):
        self.drive_past("workspace-detection")
        ack = self.jump(fresh=True)
        self.assertEqual(ack["kind"], "fresh")
        self.assertTrue(ack["archived"].startswith("aidlc-docs-archive-"))
        self.assertFalse(os.path.isdir(self._path("aidlc-docs")))
        self.assertTrue(os.path.isdir(self._path(ack["archived"])))
        # The archive's audit log records why it was archived.
        archived_audit = self._path(ack["archived"], "audit.md")
        with open(archived_audit, encoding="utf-8") as handle:
            self.assertIn("WORKFLOW_FRESH", handle.read())
        # A brand-new workflow can start.
        self.init()
        self.assertEqual(self.next()["stage"], "workspace-detection")

    def test_jump_fresh_without_docs(self):
        shutil.rmtree(self._path("aidlc-docs"))
        ack = self.jump(fresh=True)
        self.assertIsNone(ack["archived"])


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


class CliTests(WorkspaceCase):
    def _run(self, argv):
        return _run_main(argv)

    def test_status_json(self):
        code, payload = self._run(["status", "--workspace", self.workspace])
        self.assertEqual(code, 0)
        self.assertEqual(payload["engine"], "ok")

    def test_report_json(self):
        self._run(["init", "--workspace", self.workspace])
        code, payload = self._run(
            ["report", "--stage", "workspace-detection",
             "--result", "completed", "--workspace", self.workspace]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["kind"], "reported")

    def test_error_json_and_exit_code(self):
        code, payload = self._run(["next", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["kind"], "error")
        self.assertEqual(payload["code"], "no-state")
        self.assertIn("message", payload)
        self.assertIn("hint", payload)

    def test_no_subcommand_is_usage_error(self):
        code, payload = self._run([])
        self.assertEqual(code, 1)
        self.assertEqual(payload["kind"], "error")
        self.assertEqual(payload["code"], "usage")

    def test_jump_requires_target(self):
        code, payload = self._run(["jump", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "usage")

    def test_status_output_has_timestamp(self):
        code, payload = self._run(["status", "--workspace", self.workspace])
        self.assertEqual(code, 0)
        self.assertRegex(payload["timestamp"], ISO_UTC_RE)

    def test_next_output_has_timestamp(self):
        self._run(["init", "--workspace", self.workspace])
        code, payload = self._run(["next", "--workspace", self.workspace])
        self.assertEqual(code, 0)
        self.assertRegex(payload["timestamp"], ISO_UTC_RE)

    def test_error_output_has_timestamp(self):
        code, payload = self._run(["next", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["kind"], "error")
        self.assertRegex(payload["timestamp"], ISO_UTC_RE)

    def test_usage_error_has_timestamp(self):
        code, payload = self._run(["jump", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "usage")
        self.assertRegex(payload["timestamp"], ISO_UTC_RE)

    def test_argparse_errors_are_json(self):
        # Missing required flags must obey the JSON output contract too.
        code, payload = self._run(["report", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["kind"], "error")
        self.assertEqual(payload["code"], "usage")
        code, payload = self._run(
            ["report", "--stage", "x", "--result", "bogus",
             "--workspace", self.workspace]
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "usage")

    def test_park_requires_note(self):
        code, payload = self._run(["park", "--workspace", self.workspace])
        self.assertEqual(code, 1)
        self.assertEqual(payload["kind"], "error")
        self.assertEqual(payload["code"], "usage")

    def test_no_subcommand_hint_and_docstring_mention_park(self):
        code, payload = self._run([])
        self.assertEqual(code, 1)
        self.assertIn("park", payload["hint"])
        self.assertIn("park", engine.__doc__)

    def test_stamp_json_shape(self):
        code, payload = self._run(["stamp"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["engine"], "ok")
        self.assertEqual(payload["kind"], "stamp")
        self.assertEqual(
            set(payload.keys()), {"engine", "kind", "timestamp"}
        )
        self.assertRegex(payload["timestamp"], ISO_UTC_RE)

    def test_stamp_zero_side_effect(self):
        code, payload = self._run(["stamp", "--workspace", self.workspace])
        self.assertEqual(code, 0)
        self.assertEqual(payload["kind"], "stamp")
        self.assertEqual(os.listdir(self.workspace), [])


# ---------------------------------------------------------------------------
# park (Phase 3.1)
# ---------------------------------------------------------------------------


class ParkTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.drive_past("workspace-detection")

    def test_park_writes_region_line_and_handoff(self):
        before = self.marks()
        ack = self.park("waiting for user input")
        self.assertEqual(ack["kind"], "parked")
        self.assertIn(
            "- **Last Parked**: reverse-engineering"
            " — waiting for user input",
            self.state_text(),
        )
        handoff = self.handoff_text()
        self.assertIsNotNone(handoff)
        self.assertIn("## Park", handoff)
        self.assertIn("**Stage**: reverse-engineering", handoff)
        self.assertIn("**Note**: waiting for user input", handoff)
        self.assertEqual(self.marks(), before)
        self.assertEqual(self.next()["stage"], "reverse-engineering")

    def test_park_never_touches_audit(self):
        before = self.audit_text().count("## Engine Transition")
        self.park("note")
        self.assertEqual(
            self.audit_text().count("## Engine Transition"), before
        )

    def test_park_keeps_digest_consistent(self):
        self.park("note")
        self.assertEqual(self.status()["integrity"], "ok")

    def test_note_hygiene(self):
        ack = self.park("a\nb")
        self.assertEqual(ack["note"], "a; b")
        self.assertIn(
            "- **Last Parked**: reverse-engineering — a; b",
            self.state_text(),
        )
        long_ack = self.park("y" * 400)
        self.assertEqual(len(long_ack["note"]), 300)
        self.assertIn(
            "- **Last Parked**: reverse-engineering — " + "y" * 300,
            self.state_text(),
        )
        self.assert_error(lambda: self.park("   \n   "), "usage")

    def test_park_without_state(self):
        fresh = tempfile.mkdtemp(prefix="aidlc-park-nostate-")
        self.addCleanup(shutil.rmtree, fresh, True)
        self.assert_error(
            lambda: engine.cmd_park(fresh, "note"), "no-state"
        )

    def test_park_after_workflow_complete(self):
        # setUp already drove workspace-detection; plan-skip everything
        # except it and operations so operations is the last stage.
        skip = [
            s for s in STAGE_ORDER
            if s not in ("workspace-detection", "operations")
        ]
        self.set_plan_lines(skip=", ".join(skip))
        self.drive_past("operations")
        self.assert_error(lambda: self.park("note"), "workflow-complete")

    def test_park_dedupe_same_tail_note(self):
        first = self.park("same note")
        self.assertTrue(first["handoff_appended"])
        second = self.park("same note")
        self.assertFalse(second["handoff_appended"])
        self.assertEqual(self.handoff_text().count("## Park"), 1)

    def test_park_write_order_state_then_handoff(self):
        calls = []
        state_path = os.path.join(
            self.workspace, "aidlc-docs", "aidlc-state.md"
        )
        handoff_path = os.path.join(
            self.workspace, "aidlc-docs", "handoff.md"
        )
        with mock.patch.object(
            engine, "_write_text_atomic",
            side_effect=lambda path, text: calls.append(path),
        ), mock.patch.object(
            engine, "_append_text",
            side_effect=lambda path, text: calls.append(path),
        ):
            self.park("ordered note")
        self.assertEqual(calls, [state_path, handoff_path])

    def test_park_second_different_note_updates(self):
        self.park("first note")
        ack = self.park("second note")
        self.assertTrue(ack["handoff_appended"])
        handoff = self.handoff_text()
        self.assertEqual(handoff.count("## Park"), 2)
        self.assertIn("**Note**: first note", handoff)
        self.assertIn("**Note**: second note", handoff)
        self.assertIn(
            "- **Last Parked**: reverse-engineering — second note",
            self.state_text(),
        )


# ---------------------------------------------------------------------------
# status recovery upgrades (Phase 3.1)
# ---------------------------------------------------------------------------


class StatusRecoveryTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_resume_note_after_park(self):
        self.drive_past("workspace-detection")
        self.park("hold on")
        self.assertEqual(
            self.status()["resume_note"],
            {"stage": "reverse-engineering", "note": "hold on"},
        )

    def test_resume_note_none_without_park(self):
        self.assertIsNone(self.status()["resume_note"])

    def test_recent_events_last_five(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "skipped", "greenfield")
        self.report("requirements-analysis", "approved")
        self.report("user-stories", "skipped", "not needed")
        self.report("workflow-planning", "approved")
        result = self.status()
        events = result["recent_events"]
        self.assertEqual(result["audit_entries"], 6)
        self.assertEqual(len(events), 5)
        for event in events:
            self.assertEqual(
                set(event.keys()),
                {"event", "stage", "reason", "timestamp"},
            )
            self.assertRegex(event["timestamp"], ISO_UTC_RE)
        self.assertEqual(
            [e["event"] for e in events],
            [
                "STAGE_COMPLETED",
                "STAGE_SKIPPED",
                "STAGE_APPROVED",
                "STAGE_SKIPPED",
                "STAGE_APPROVED",
            ],
        )
        self.assertEqual(
            [e["stage"] for e in events],
            [
                "workspace-detection",
                "reverse-engineering",
                "requirements-analysis",
                "user-stories",
                "workflow-planning",
            ],
        )
        self.assertEqual(events[1]["reason"], "greenfield")
        self.assertEqual(events[3]["reason"], "not needed")

    def test_recent_events_ignore_forged_model_section(self):
        self.drive_past("workspace-detection")
        audit = self.audit_text()
        parts = audit.split("## Engine Transition")
        self.assertEqual(len(parts), 3)  # preamble + two engine sections
        forged = (
            "## Code Generation\n"
            "**Timestamp**: 2020-01-01T00:00:00Z\n"
            "**Event**: STAGE_APPROVED\n"
            "**Stage**: operations\n"
            "**Reason**: forged by the model\n"
            "\n---\n\n"
        )
        tampered = (
            parts[0] + "## Engine Transition" + parts[1] + forged
            + "## Engine Transition" + parts[2]
        )
        with open(self._path("aidlc-docs", "audit.md"), "w",
                  encoding="utf-8", newline="") as handle:
            handle.write(tampered)
        result = self.status()
        self.assertEqual(result["integrity"], "ok")
        self.assertNotIn(
            "operations", [e["stage"] for e in result["recent_events"]]
        )

    def test_timestamp_attribution_is_last_in_section(self):
        self.drive_past("workspace-detection")
        manual = (
            "\n## Engine Transition\n"
            "**Event**: STAGE_COMPLETED\n"
            "**Stage**: workspace-detection\n"
            "**Timestamp**: 2020-05-05T05:05:05Z\n"
            "**Timestamp**: 2021-06-06T06:06:06Z\n"
            "\n---\n\n"
        )
        with open(self._path("aidlc-docs", "audit.md"), "a",
                  encoding="utf-8", newline="") as handle:
            handle.write(manual)
        events = self.status()["recent_events"]
        self.assertEqual(
            events[-1],
            {
                "event": "STAGE_COMPLETED",
                "stage": "workspace-detection",
                "reason": None,
                "timestamp": "2021-06-06T06:06:06Z",
            },
        )

    def test_no_alert_when_one_of_two_produces_exists(self):
        self.route_to("requirements-analysis")
        self.make_doc(
            "inception/requirements/"
            "requirement-verification-questions.md"
        )
        ack = self.report("requirements-analysis", "approved")
        self.assertNotIn("produces_missing", ack)
        alerts = self.status()["artifact_alerts"]
        self.assertEqual(
            [a for a in alerts if a["type"] == "missing-produces"], []
        )

    def test_no_alert_when_some_of_eight_produces_exist(self):
        self.route_to("build-and-test")
        for name in (
            "build-instructions",
            "unit-test-instructions",
            "integration-test-instructions",
            "performance-test-instructions",
        ):
            self.make_doc("construction/build-and-test/%s.md" % name)
        ack = self.report("build-and-test", "approved")
        self.assertNotIn("produces_missing", ack)
        alerts = self.status()["artifact_alerts"]
        self.assertEqual(
            [a for a in alerts if a["type"] == "missing-produces"], []
        )

    def test_no_alert_for_single_produce_stage_completed_empty(self):
        self.route_to("infrastructure-design")
        self.report("infrastructure-design", "approved")
        alerts = self.status()["artifact_alerts"]
        self.assertEqual(
            [a for a in alerts if a["type"] == "missing-produces"], []
        )

    def test_no_alert_for_zero_produce_stage_and_engine_files(self):
        self.route_to("operations")
        self.drive_past("operations")
        self.assertEqual(self.status()["artifact_alerts"], [])

    def test_missing_produces_alert_when_all_absent(self):
        self.route_to("requirements-analysis")
        self.report("requirements-analysis", "approved")
        alerts = [
            a for a in self.status()["artifact_alerts"]
            if a["type"] == "missing-produces"
        ]
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        self.assertEqual(alert["subject"], "requirements-analysis")
        self.assertEqual(alert["severity"], "warning")
        self.assertEqual(
            set(alert.keys()),
            {"type", "severity", "subject", "message",
             "action_discipline"},
        )
        self.assertIn(
            "aidlc-docs/inception/requirements/requirements.md",
            alert["message"],
        )
        self.assertIn(
            "aidlc-docs/inception/requirements/"
            "requirement-verification-questions.md",
            alert["message"],
        )
        self.assertEqual(
            alert["action_discipline"],
            "Report to the user; do not regenerate or fabricate "
            "artifacts.",
        )

    def test_missing_produces_counts_empty_file_as_missing(self):
        self.route_to("requirements-analysis")
        self.make_doc("inception/requirements/requirements.md",
                      content="")
        self.report("requirements-analysis", "approved")
        alerts = [
            a for a in self.status()["artifact_alerts"]
            if a["type"] == "missing-produces"
        ]
        self.assertEqual(len(alerts), 1)
        self.assertIn(
            "aidlc-docs/inception/requirements/requirements.md",
            alerts[0]["message"],
        )

    def test_resumed_artifacts_via_unit_glob(self):
        self.route_to("functional-design")
        self.make_doc(
            "construction/auth[1]/functional-design/"
            "business-logic-model.md"
        )
        alerts = [
            a for a in self.status()["artifact_alerts"]
            if a["type"] == "resumed-artifacts"
        ]
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["subject"], "functional-design")
        self.assertEqual(alerts[0]["severity"], "info")
        self.assertIn(
            "construction/auth[1]/functional-design/"
            "business-logic-model.md",
            alerts[0]["message"],
        )

    def test_resumed_artifacts_for_current_stage(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "skipped", "greenfield")
        self.make_doc("inception/requirements/requirements.md")
        alerts = [
            a for a in self.status()["artifact_alerts"]
            if a["type"] == "resumed-artifacts"
        ]
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["subject"], "requirements-analysis")

    def test_alert_probe_failure_fails_open(self):
        self.drive_past("workspace-detection")
        with mock.patch.object(
            engine, "_artifact_alerts",
            side_effect=RuntimeError("boom"),
        ):
            result = self.status()
        self.assertEqual(result["artifact_alerts"], [])
        self.assertTrue(result["alerts_unavailable"])
        self.assertEqual(result["integrity"], "ok")

    def test_alerts_still_computed_when_integrity_violated(self):
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "skipped", "greenfield")
        self.make_doc("inception/requirements/requirements.md")
        text = self.state_text().replace(
            "- [ ] operations", "- [x] operations"
        )
        self.write_state(text)
        result = self.status()
        self.assertEqual(result["integrity"], "violated")
        self.assertIn(
            "resumed-artifacts",
            [a["type"] for a in result["artifact_alerts"]],
        )

    # -- autonomous key + note age (Phase 3.3) ----------------------------

    def _append_model_text(self, text):
        """Append model-owned region text after the ENGINE-STATE region."""
        self.write_state(self.state_text() + text)

    def test_autonomous_key_parses_enabled_section(self):
        self._append_model_text(
            "\n## Autonomous Mode\n"
            "- **Enabled**: Yes\n"
            "- **Question Handling**: auto-recommended\n"
            "- **Review Stages**: code-generation, build-and-test\n"
            "- **Last Updated**: 2026-09-24T08:00:00Z\n"
        )
        self.assertEqual(
            self.status()["autonomous"],
            {
                "enabled": True,
                "question_handling": "auto-recommended",
                "review_stages": ["code-generation", "build-and-test"],
                "last_updated": "2026-09-24T08:00:00Z",
            },
        )

    def test_autonomous_key_disabled_has_no_review_stages(self):
        self._append_model_text(
            "\n## Autonomous Mode\n"
            "- **Enabled**: No\n"
            "- **Question Handling**: N/A\n"
            "- **Review Stages**: None\n"
            "- **Last Updated**: 2026-09-24T08:00:00Z\n"
        )
        autonomous = self.status()["autonomous"]
        self.assertEqual(autonomous["enabled"], False)
        self.assertEqual(autonomous["review_stages"], [])
        self.assertEqual(autonomous["question_handling"], "N/A")

    def test_autonomous_key_null_when_missing_or_malformed(self):
        # The section is missing entirely.
        self.assertIsNone(self.status()["autonomous"])
        # Malformed: Enabled value is neither Yes nor No.
        self._append_model_text(
            "\n## Autonomous Mode\n- **Enabled**: sometimes\n"
        )
        self.assertIsNone(self.status()["autonomous"])
        # Malformed: the section exists but carries no Enabled line.
        self.write_state(
            self.state_text().replace(
                "- **Enabled**: sometimes",
                "- **Question Handling**: manual",
            )
        )
        self.assertIsNone(self.status()["autonomous"])

    def test_note_age_seconds_after_park(self):
        self.drive_past("workspace-detection")
        self.park("waiting for user input")
        age = self.status()["note_age_seconds"]
        self.assertIsInstance(age, int)
        self.assertGreaterEqual(age, 0)

    def test_note_age_null_without_a_current_note(self):
        self.assertIsNone(self.status()["note_age_seconds"])
        self.drive_past("workspace-detection")
        self.park("in flight")
        self.report("reverse-engineering", "skipped", "greenfield")
        # A transition supersedes the park: there is no current note to
        # age, even though handoff.md still holds the historical entry.
        status = self.status()
        self.assertIsNone(status["resume_note"])
        self.assertIsNone(status["note_age_seconds"])

    def test_note_age_null_on_unparseable_handoff_timestamp(self):
        self.drive_past("workspace-detection")
        self.park("in flight")
        handoff = re.sub(
            r"\*\*Timestamp\*\*: .*",
            "**Timestamp**: garbage",
            self.handoff_text(),
            count=1,
        )
        with open(
            self._path("aidlc-docs", "handoff.md"), "w",
            encoding="utf-8", newline="",
        ) as handle:
            handle.write(handoff)
        self.assertIsNone(self.status()["note_age_seconds"])

    def test_note_age_null_when_handoff_tail_drifted(self):
        self.drive_past("workspace-detection")
        self.park("in flight")
        # Simulate a drifted handoff history (crash between the two park
        # writes, or last-writer-wins concurrency): the tail no longer
        # matches the region's parked note. resume_note stays (region is
        # authoritative) but no age of the WRONG note is reported.
        handoff = self.handoff_text().replace(
            "**Stage**: reverse-engineering", "**Stage**: user-stories"
        )
        with open(
            self._path("aidlc-docs", "handoff.md"), "w",
            encoding="utf-8", newline="",
        ) as handle:
            handle.write(handoff)
        status = self.status()
        self.assertEqual(
            status["resume_note"],
            {"stage": "reverse-engineering", "note": "in flight"},
        )
        self.assertIsNone(status["note_age_seconds"])

    # -- checkpoint-missing anchors (Phase 3.3, CTX opt-in) ----------------

    CTX_TABLE = (
        "## Extension Configuration\n"
        "| Extension | Enabled | Decided At |\n"
        "|---|---|---|\n"
        "| Context Checkpointing | Yes | Requirements Analysis |\n"
    )

    def _complete_inception(self):
        text = self.state_text()
        for slug in STAGE_ORDER[:7]:
            text = text.replace("- [ ] %s" % slug, "- [x] %s" % slug)
        self.write_state(text)
        self.rebase()

    def _checkpoint_alerts(self):
        return [
            alert
            for alert in self.status()["artifact_alerts"]
            if alert["type"] == "checkpoint-missing"
        ]

    def test_checkpoint_missing_alert_when_ctx_enabled(self):
        self._complete_inception()
        self._append_model_text("\n" + self.CTX_TABLE)
        alerts = self._checkpoint_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["subject"], "inception")
        self.assertEqual(alerts[0]["severity"], "warning")
        self.assertEqual(
            set(alerts[0].keys()),
            {"type", "severity", "subject", "message",
             "action_discipline"},
        )
        self.assertIn(
            "aidlc-docs/checkpoints/inception-checkpoint.md",
            alerts[0]["message"],
        )

    def test_no_checkpoint_alert_when_checkpoint_exists(self):
        self._complete_inception()
        self._append_model_text("\n" + self.CTX_TABLE)
        self.make_doc("checkpoints/inception-checkpoint.md")
        self.assertEqual(self._checkpoint_alerts(), [])

    def test_no_checkpoint_alert_when_ctx_not_enabled(self):
        self._complete_inception()
        # No Extension Configuration table at all: no check.
        self.assertEqual(self._checkpoint_alerts(), [])
        # A disabled row also means: no check.
        self._append_model_text(
            "\n## Extension Configuration\n"
            "| Extension | Enabled | Decided At |\n"
            "|---|---|---|\n"
            "| Context Checkpointing | No | Requirements Analysis |\n"
        )
        self.assertEqual(self._checkpoint_alerts(), [])

    def test_no_checkpoint_alert_on_malformed_table(self):
        self._complete_inception()
        self._append_model_text(
            "\n## Extension Configuration\n"
            "| Context Checkpointing | maybe |\n"  # not Yes -> not enabled
        )
        self.assertEqual(self._checkpoint_alerts(), [])

    def test_construction_checkpoint_anchor(self):
        self._complete_inception()
        text = self.state_text().replace(
            "- [ ] build-and-test", "- [x] build-and-test"
        )
        self.write_state(text)
        self.rebase()
        self._append_model_text("\n" + self.CTX_TABLE)
        subjects = {alert["subject"] for alert in self._checkpoint_alerts()}
        self.assertEqual(subjects, {"inception", "construction"})
        self.make_doc("checkpoints/inception-checkpoint.md")
        self.make_doc("checkpoints/construction-checkpoint.md")
        self.assertEqual(self._checkpoint_alerts(), [])


# ---------------------------------------------------------------------------
# report soft warning (Phase 3.1)
# ---------------------------------------------------------------------------


class ReportWarningTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.drive_past("workspace-detection")
        self.report("reverse-engineering", "skipped", "greenfield")

    def test_report_approved_flags_missing_produces(self):
        ack = self.report("requirements-analysis", "approved")
        self.assertEqual(ack["kind"], "reported")
        self.assertEqual(ack["current_stage"], "user-stories")
        self.assertEqual(
            ack["produces_missing"],
            [
                "aidlc-docs/inception/requirements/requirements.md",
                "aidlc-docs/inception/requirements/"
                "requirement-verification-questions.md",
            ],
        )

    def test_report_warning_fails_open(self):
        with mock.patch.object(
            engine, "_stage_missing_produces",
            side_effect=RuntimeError("boom"),
        ):
            ack = self.report("requirements-analysis", "approved")
        self.assertEqual(ack["kind"], "reported")
        self.assertNotIn("produces_missing", ack)

    def test_report_rejected_skips_probe(self):
        ack = self.report("requirements-analysis", "rejected")
        self.assertNotIn("produces_missing", ack)
        self.assertEqual(ack["current_stage"], "requirements-analysis")


# ---------------------------------------------------------------------------
# backward compatibility (Phase 3.1)
# ---------------------------------------------------------------------------


class BackwardCompatTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()

    def test_state_without_reader_notes_line_still_works(self):
        text = self.state_text()
        kept = [
            line for line in text.split("\n")
            if not line.startswith("Reader notes")
        ]
        self.write_state("\n".join(kept))
        result = self.status()
        self.assertEqual(result["state"], "active")
        self.drive_past("workspace-detection")
        self.assertIsNone(self.status()["resume_note"])
        self.assertNotIn("Last Parked", self.state_text())

    def test_rebase_is_byte_idempotent(self):
        self.report("workspace-detection", "completed")
        before = self.state_text()
        self.rebase()
        self.assertEqual(self.state_text(), before)


# ---------------------------------------------------------------------------
# park interaction matrix (Phase 3.1)
# ---------------------------------------------------------------------------


class InteractionMatrixTests(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.drive_past("workspace-detection")
        self.park("in flight")

    def test_report_clears_park_but_keeps_handoff(self):
        self.report("reverse-engineering", "skipped", "greenfield")
        self.assertIsNone(self.status()["resume_note"])
        self.assertNotIn("Last Parked", self.state_text())
        self.assertEqual(self.handoff_text().count("## Park"), 1)

    def test_jump_clears_park(self):
        self.jump(slug="user-stories")
        self.assertIsNone(self.status()["resume_note"])

    def test_jump_fresh_archives_handoff(self):
        ack = self.jump(fresh=True)
        archived = ack["archived"]
        self.assertIsNotNone(archived)
        self.assertTrue(
            os.path.isfile(self._path(archived, "handoff.md"))
        )
        self.init()
        parked = self.park("again")
        self.assertEqual(parked["kind"], "parked")
        self.assertIsNotNone(self.handoff_text())

    def test_rebase_preserves_park(self):
        text = self.state_text().replace(
            "- [ ] operations", "- [x] operations"
        )
        self.write_state(text)
        self.rebase()
        result = self.status()
        self.assertEqual(result["integrity"], "ok")
        self.assertEqual(
            result["resume_note"],
            {"stage": "reverse-engineering", "note": "in flight"},
        )


# ---------------------------------------------------------------------------
# golden output shapes (Phase 3.1)
# ---------------------------------------------------------------------------


def _run_main(argv):
    """Run engine.main in-process, capturing JSON stdout (CLI surface)."""
    import contextlib
    import io

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            code = engine.main(["engine.py"] + argv)
        except SystemExit as exc:  # argparse error path exits directly
            code = exc.code if isinstance(exc.code, int) else 2
    return code, json.loads(buffer.getvalue())


class GoldenOutputTests(WorkspaceCase):
    def test_status_active_key_set_exact(self):
        self.init()
        result = self.status()
        self.assertEqual(
            set(result.keys()),
            {
                "engine",
                "state_version",
                "workspace",
                "state",
                "current_stage",
                "scope",
                "depth",
                "last_completed",
                "integrity",
                "completed",
                "remaining",
                "resume_note",
                "autonomous",
                "note_age_seconds",
                "recent_events",
                "audit_entries",
                "audit_bytes",
                "artifact_alerts",
                "alerts_unavailable",
            },
        )

    def test_status_corrupt_key_set_has_no_new_keys(self):
        self.init()
        text = self.state_text()
        kept = [
            line for line in text.split("\n")
            if not line.startswith("<!-- END ENGINE-STATE")
        ]
        self.write_state("\n".join(kept))
        result = self.status()
        self.assertEqual(
            set(result.keys()),
            {
                "engine",
                "state_version",
                "workspace",
                "state",
                "current_stage",
                "scope",
                "depth",
                "last_completed",
                "integrity",
                "completed",
                "remaining",
                "hint",
            },
        )

    def test_status_none_key_set_has_no_new_keys(self):
        result = self.status()  # no state file at all
        self.assertEqual(
            set(result.keys()),
            {
                "engine",
                "state_version",
                "workspace",
                "state",
                "current_stage",
                "scope",
                "depth",
                "last_completed",
                "integrity",
                "completed",
                "remaining",
            },
        )

    def test_status_legacy_key_set_has_no_new_keys(self):
        os.makedirs(self._path("aidlc-docs"))
        self.write_state("# AI-DLC State Tracking\n\n- old style file\n")
        result = self.status()
        self.assertEqual(
            set(result.keys()),
            {
                "engine",
                "state_version",
                "workspace",
                "state",
                "current_stage",
                "scope",
                "depth",
                "last_completed",
                "integrity",
                "completed",
                "remaining",
                "hint",
            },
        )

    def test_park_ack_key_set_exact(self):
        self.init()
        self.drive_past("workspace-detection")
        ack = self.park("note")
        self.assertEqual(
            set(ack.keys()),
            {"kind", "stage", "note", "handoff_file",
             "handoff_appended"},
        )

    def test_cli_status_masked_golden(self):
        self.init()
        self.drive_past("workspace-detection")
        self.park("mid-stage note")
        code, payload = _run_main(
            ["status", "--workspace", self.workspace]
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["audit_bytes"],
            os.path.getsize(self._path("aidlc-docs", "audit.md")),
        )
        payload["timestamp"] = "<TS>"
        payload["workspace"] = "<WS>"
        payload["audit_bytes"] = "<BYTES>"
        payload["note_age_seconds"] = "<AGE>"
        for event in payload["recent_events"]:
            event["timestamp"] = "<TS>"
        golden = {
            "engine": "ok",
            "state_version": 1,
            "workspace": "<WS>",
            "state": "active",
            "current_stage": "reverse-engineering",
            "scope": "classic",
            "depth": "standard",
            "last_completed": "workspace-detection",
            "integrity": "ok",
            "completed": ["workspace-detection"],
            "remaining": STAGE_ORDER[1:],
            "resume_note": {
                "stage": "reverse-engineering",
                "note": "mid-stage note",
            },
            "autonomous": None,
            "note_age_seconds": "<AGE>",
            "recent_events": [
                {
                    "event": "STATE_CREATED",
                    "stage": "-",
                    "reason": "-",
                    "timestamp": "<TS>",
                },
                {
                    "event": "STAGE_COMPLETED",
                    "stage": "workspace-detection",
                    "reason": "-",
                    "timestamp": "<TS>",
                },
            ],
            "audit_entries": 2,
            "audit_bytes": "<BYTES>",
            "artifact_alerts": [],
            "alerts_unavailable": False,
            "timestamp": "<TS>",
        }
        self.assertEqual(payload, golden)


if __name__ == "__main__":
    unittest.main()
