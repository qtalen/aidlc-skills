"""Extension-layout invariants for the opt-in discovery protocol (D21).

SKILL.md's extension loading prescribes a filesystem protocol:
  * workflow start loads ONLY ``*.opt-in.md`` stubs under
    ``references/extensions/``;
  * a stub's full rules file is derived by naming convention (strip
    ``.opt-in.md``, append ``.md``) and loads ONLY after the user opts in;
  * every rule ``.md`` WITHOUT an opt-in companion is MANDATORY — its
    rules file loads immediately at every workflow start.

Two failure modes can therefore arise from plain file edits, with no
code involved: a stub whose derived rules file does not exist (broken
convention), and a rule .md left without a companion (silently becomes
a mandatory always-on extension). D21 deleted the Context Checkpointing
extension in one move — both files together — precisely to avoid the
second trap; these tests pin both invariants permanently.

Deliberately NOT asserted: which opt-in extensions exist. Adding a
legitimate opt-in extension must not require a test edit, and restoring
CTX from git history (documented in D21) must not either. The mandatory
allowlist is the one conscious-registration point, because mandatory
rules load at every workflow start.
"""

import os
import tempfile
import unittest

SKILL_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
EXT_ROOT = os.path.join(SKILL_ROOT, "references", "extensions")

# Rule files intentionally loaded at every workflow start (SKILL.md
# mandatory discovery). Deliberate additions go through this line.
MANDATORY_ALLOWLIST = {
    os.path.join("workflow", "workflow-conventions", "workflow-conventions.md"),
}


def _scan(ext_root):
    """Replicate SKILL.md's discovery protocol over ``ext_root``.

    Returns ``(stubs, broken_convention, mandatory)``:
      stubs              rel paths of every ``*.opt-in.md`` found;
      broken_convention  rel stub paths whose derived rules file is absent;
      mandatory          rel rule ``.md`` paths with no opt-in companion.
    """
    stubs, rule_files = [], []
    for dirpath, _dirs, files in os.walk(ext_root):
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, name), ext_root)
            if name.endswith(".opt-in.md"):
                stubs.append(rel)
            elif name.endswith(".md"):
                rule_files.append(rel)
    broken = [
        s for s in stubs
        if not os.path.exists(
            os.path.join(ext_root, s[: -len(".opt-in.md")] + ".md")
        )
    ]
    mandatory = [
        r for r in rule_files
        if not os.path.exists(
            os.path.join(ext_root, r[: -len(".md")] + ".opt-in.md")
        )
    ]
    return stubs, broken, mandatory


class LiveTreeTests(unittest.TestCase):
    """Invariants over the real extensions tree."""

    def test_every_stub_resolves_to_a_rules_file(self):
        _stubs, broken, _mandatory = _scan(EXT_ROOT)
        self.assertEqual(broken, [])

    def test_orphans_equal_mandatory_allowlist(self):
        _stubs, _broken, mandatory = _scan(EXT_ROOT)
        self.assertEqual(set(mandatory), MANDATORY_ALLOWLIST)


class DetectorTests(unittest.TestCase):
    """The detector itself must flag exactly the two failure modes
    (mutation coverage on synthetic trees; the live tree is never
    touched)."""

    def _build(self, rel_files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = os.path.join(tmp.name, "extensions")
        for rel in rel_files:
            path = os.path.join(root, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("x")
        return root

    def test_clean_tree_passes(self):
        root = self._build([
            "a/a.opt-in.md", "a/a.md",
            "b/b.md",  # the one intentional mandatory orphan
        ])
        stubs, broken, mandatory = _scan(root)
        self.assertEqual(stubs, [os.path.join("a", "a.opt-in.md")])
        self.assertEqual(broken, [])
        self.assertEqual(mandatory, [os.path.join("b", "b.md")])

    def test_stub_without_rules_file_flagged(self):
        root = self._build(["c/c.opt-in.md"])
        _stubs, broken, _mandatory = _scan(root)
        self.assertEqual(broken, [os.path.join("c", "c.opt-in.md")])

    def test_accidental_orphan_flagged(self):
        # D21's trap: deleting a stub while keeping its rules file turns
        # an opt-in extension into a mandatory one.
        root = self._build(["a/a.md"])
        _stubs, _broken, mandatory = _scan(root)
        self.assertEqual(mandatory, [os.path.join("a", "a.md")])


if __name__ == "__main__":
    unittest.main()
