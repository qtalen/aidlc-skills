"""Rule-text invariants for cross-file consistency (B11 precedent).

Asserts that terms and exemptions introduced by a batch appear in EVERY
rule file that coordinates around them, so a rename or removal in one
file cannot silently orphan the others (B15 product-brainstorm: D19.36
dialogue discipline, D19.38 routing, D19.39 tool exemption).
"""

import os
import unittest

SKILL_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def _read(rel):
    with open(os.path.join(SKILL_ROOT, rel), encoding="utf-8") as handle:
        return handle.read()


class ProductBrainstormCoPresenceTests(unittest.TestCase):
    """`product-brainstorm` must appear in all four coordinating files."""

    COORDINATION_FILES = (
        "SKILL.md",                                   # stage block
        "references/common/question-format-guide.md",  # dialogue exemption
        "references/inception/requirements-analysis.md",  # load/route/consume
        "references/common/session-continuity.md",    # #12 exemption
    )

    def test_slug_in_all_coordination_files(self):
        for rel in self.COORDINATION_FILES:
            self.assertIn("product-brainstorm", _read(rel), rel)

    def test_dialogue_exemption_wording_paired(self):
        # The qfg exemption and the session-continuity #12 exemption must
        # name the same thing ("Product Brainstorm stage dialogue") — they
        # are one rule stated twice.
        for rel in (
            "references/common/question-format-guide.md",
            "references/common/session-continuity.md",
        ):
            self.assertIn(
                "Product Brainstorm stage dialogue", _read(rel), rel
            )

    def test_classic_scope_membership_count(self):
        # classic is the nothing-pre-skipped scope: its membership must
        # count every stage (15 since product-brainstorm joined, D19.35).
        self.assertIn(
            "All 15 stages", _read("references/common/scopes/classic.md")
        )


class IterationDeliveryCoPresenceTests(unittest.TestCase):
    """B15 segment 2 (delivery loop, D20 merged): the three iteration
    sections in workflow-changes and every coordinating sentence that
    points at them must stay co-present across files."""

    def test_workflow_changes_three_sections(self):
        text = _read("references/common/workflow-changes.md")
        for heading in (
            "## Roadmap Changes (Three Revision Time-Points)",
            "## Splitting an Oversized Iteration",
            "## Iteration Completion Ritual",
        ):
            self.assertIn(heading, text, heading)

    def test_shipped_immutability_and_marking_paired(self):
        # D20.14/D20.16: immutability lives in workflow-changes; the B&T
        # commit protocol carries the marking rule and the artifact name
        # (roadmap lives inside product-design.md since D20.2's override).
        # P14 (dogfood #2 paper walkthrough): the trigger is "has an
        # iteration roadmap" — N=1 products mark their only row too.
        self.assertIn(
            "never rewritten", _read("references/common/workflow-changes.md")
        )
        bt = _read("references/construction/build-and-test.md")
        self.assertIn("product-design.md", bt)
        self.assertIn("Shipped Log rollup line", bt)
        self.assertIn("Products with an iteration roadmap", bt)
        self.assertIn("single-iteration one", bt)  # N=1 clause (P14 core semantics)
        # R1 (review): Branch 3 must NOT conflate N=1-with-roadmap with
        # no-roadmap — the parenthetical names the no-roadmap condition only.
        wc = _read("references/common/workflow-changes.md")
        self.assertIn(
            "(a design delivered without an iteration roadmap", wc
        )
        self.assertIn("an N=1 roadmap's only iteration counts as the last", wc)

    def test_iteration_scope_wp_and_ug(self):
        # WP plans the subset (template section + verification); UG scopes
        # units to it and re-checks H1 at unit granularity.
        wp = _read("references/inception/workflow-planning.md")
        self.assertIn("## Iteration Scope", wp)
        self.assertIn("Iteration Scope Verification", wp)
        ug = _read("references/inception/units-generation.md")
        self.assertIn("Iteration Scope (multi-iteration products)", ug)
        self.assertIn("roadmap defect back to Workflow Planning", ug)

    def test_ritual_pointers_from_entry_files(self):
        # The two engine-directive entry points must point at the ritual.
        for rel in ("SKILL.md", "references/common/session-continuity.md"):
            self.assertIn("Iteration Completion Ritual", _read(rel), rel)

    def test_preference_never_waived_paired(self):
        # P8 ruling (dogfood #1): the same sentence lands in both the
        # brainstorm dialogue discipline and RA's completeness analysis.
        for rel in (
            "references/inception/product-brainstorm.md",
            "references/inception/requirements-analysis.md",
        ):
            self.assertIn(
                "Preference questions are never waived", _read(rel), rel
            )

    def test_no_bundled_defaults_package(self):
        # P10 ruling (dogfood #1): small finishing decisions are asked one
        # by one — no approve-all defaults bundle.
        self.assertIn(
            "never a bundled",
            _read("references/inception/product-brainstorm.md"),
        )

    def test_optin_not_orphaned_without_questions_file(self):
        # P7 ruling (dogfood #1): the file-less path still presents opt-in
        # prompts independently.
        self.assertIn(
            "never be orphaned",
            _read("references/inception/requirements-analysis.md"),
        )


class AutonomousModeTurnBoundaryTests(unittest.TestCase):
    """P13 ruling (dogfood #2, option b): AM-03 must state that turn
    boundaries are pacing, never gates — a resumption poke carries no
    approval semantics."""

    def test_turn_boundary_clause_present(self):
        am = _read(
            "references/extensions/workflow/autonomous-mode/autonomous-mode.md"
        )
        self.assertIn("Turn boundaries are not stop points", am)
        self.assertIn("resumption trigger only", am)


if __name__ == "__main__":
    unittest.main()
