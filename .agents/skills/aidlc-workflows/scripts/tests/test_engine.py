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
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                code = engine.main(["engine.py"] + argv)
            except SystemExit as exc:  # argparse error path exits directly
                code = exc.code if isinstance(exc.code, int) else 2
        return code, json.loads(buffer.getvalue())

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


if __name__ == "__main__":
    unittest.main()
