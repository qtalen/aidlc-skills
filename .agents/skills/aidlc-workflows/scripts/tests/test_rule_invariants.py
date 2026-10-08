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


if __name__ == "__main__":
    unittest.main()
