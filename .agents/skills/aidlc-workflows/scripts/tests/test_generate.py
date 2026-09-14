#!/usr/bin/env python3
"""Unit + integration tests for the author-time generator (generate.py).

Run from the repository root:

    python -m unittest discover -s scripts\\tests -v

Pure standard library. The ``scripts`` directory is intentionally *not* made a
package: the module under test is loaded by absolute path via importlib, and
integration tests exercise it as a subprocess against a throwaway copy of the
skill tree (the real skill files are never written to).
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
GENERATE_PATH = os.path.join(SCRIPTS_DIR, "generate.py")
SKILL_ROOT = os.path.dirname(SCRIPTS_DIR)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SKILL_ROOT)))


def _load_generate():
    spec = importlib.util.spec_from_file_location("aidlc_generate", GENERATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate = _load_generate()


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _stage_fm(
    slug,
    phase,
    execution,
    scopes,
    consumes="[]",
    produces="[]",
    requires_stage="[]",
    condition="Runs when needed",
    gate="none",
):
    """Build a minimal valid stage frontmatter + H1 body."""
    lines = [
        "---",
        "slug: " + slug,
        "phase: " + phase,
        "execution: " + execution,
        "condition: " + condition,
        "gate: " + gate,
        "produces: " + produces,
        "consumes: " + consumes,
        "requires_stage: " + requires_stage,
        "scopes:",
    ]
    for name, value in scopes.items():
        lines.append("  %s: %s" % (name, value))
    lines.append("---")
    lines.append("")
    lines.append("# Test Stage")
    return "\n".join(lines)


def _warn_stage(
    slug, produces=(), consumes=(), requires_stage=(), scopes=None, for_each=None
):
    """Build a synthetic Stage object for compute_warnings()."""
    return generate.Stage(
        slug=slug,
        path=slug + ".md",
        produces=list(produces),
        consumes=list(consumes),
        requires_stage=list(requires_stage),
        scopes=dict(scopes or {}),
        for_each=for_each,
    )


def _consume(artifact, required=True, conditional_on=None):
    return {
        "artifact": artifact,
        "required": required,
        "conditional_on": conditional_on,
    }


def _run_generate(cwd, check=False):
    cmd = [sys.executable, GENERATE_PATH, "--check"] if check else [
        sys.executable,
        GENERATE_PATH,
    ]
    if os.path.realpath(cwd) != os.path.realpath(REPO_ROOT):
        # Operate on the generator copy that lives inside the temp tree.
        cmd[1] = os.path.join(cwd, "scripts", "generate.py")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _snapshot(root):
    snapshot = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            with open(full, "rb") as handle:
                snapshot[rel] = handle.read()
    return snapshot


# ---------------------------------------------------------------------------
# 1. Parser unit tests
# ---------------------------------------------------------------------------


class ScalarParsingTests(unittest.TestCase):
    def test_double_quoted_scalar_keeps_hash(self):
        # Y4 regression: '#' inside quotes is data, not a comment.
        self.assertEqual(generate._parse_scalar('"issue #123"'), "issue #123")

    def test_single_quoted_scalar_keeps_hash(self):
        self.assertEqual(generate._parse_scalar("'a # b'"), "a # b")

    def test_quoted_scalar_keeps_hash_with_trailing_comment(self):
        self.assertEqual(generate._parse_scalar('"issue #123" # note'), "issue #123")

    def test_unquoted_scalar_still_truncates_inline_comment(self):
        self.assertEqual(generate._parse_scalar("foo # comment"), "foo")

    def test_plain_scalar_unchanged(self):
        self.assertEqual(generate._parse_scalar("plain-value"), "plain-value")

    def test_booleans_and_ints(self):
        self.assertIs(generate._parse_scalar("true"), True)
        self.assertIs(generate._parse_scalar("false"), False)
        self.assertEqual(generate._parse_scalar("42"), 42)


class FrontmatterParsingTests(unittest.TestCase):
    def test_quoted_value_hash_survives_frontmatter(self):
        text = '---\ndescription: "issue #123"\n---\n# Scope\n'
        mapping, _body = generate._parse_frontmatter(text, "scope.md")
        self.assertEqual(mapping["description"], "issue #123")

    def test_consumes_list_of_maps(self):
        text = (
            "---\n"
            "slug: demo\n"
            "consumes:\n"
            "  - artifact: docs/a.md\n"
            "    required: true\n"
            "  - artifact: docs/b.md\n"
            "    required: false\n"
            "    conditional_on: brownfield\n"
            "---\n"
            "# Demo\n"
        )
        mapping, _body = generate._parse_frontmatter(text, "demo.md")
        self.assertEqual(
            mapping["consumes"],
            [
                {"artifact": "docs/a.md", "required": True},
                {
                    "artifact": "docs/b.md",
                    "required": False,
                    "conditional_on": "brownfield",
                },
            ],
        )
        normalized = generate._as_consumes(mapping["consumes"], "demo.md")
        self.assertEqual(normalized[0]["conditional_on"], None)
        self.assertIs(normalized[0]["required"], True)
        self.assertEqual(normalized[1]["conditional_on"], "brownfield")

    def test_scopes_nested_map(self):
        text = (
            "---\n"
            "scopes:\n"
            "  classic: EXECUTE\n"
            "  bugfix: SKIP\n"
            "  refactor: CONDITIONAL\n"
            "---\n"
            "# X\n"
        )
        mapping, _body = generate._parse_frontmatter(text, "x.md")
        self.assertEqual(
            mapping["scopes"],
            {"classic": "EXECUTE", "bugfix": "SKIP", "refactor": "CONDITIONAL"},
        )

    def test_empty_lists(self):
        text = (
            "---\n"
            "consumes: []\n"
            "produces: []\n"
            "keywords: []\n"
            "---\n"
            "# X\n"
        )
        mapping, _body = generate._parse_frontmatter(text, "x.md")
        self.assertEqual(mapping["consumes"], [])
        self.assertEqual(mapping["produces"], [])
        self.assertEqual(mapping["keywords"], [])

    def test_scope_default_boolean(self):
        text = (
            "---\n"
            "name: classic\n"
            "depth: standard\n"
            "keywords: []\n"
            'description: "Full lifecycle"\n'
            "default: true\n"
            "---\n"
            "# classic\n"
        )
        mapping, _body = generate._parse_frontmatter(text, "classic.md")
        self.assertIs(mapping["default"], True)


# ---------------------------------------------------------------------------
# 2. Validator unit tests
# ---------------------------------------------------------------------------


class StageValidationTests(unittest.TestCase):
    def test_valid_stage_builds(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE", "bugfix": "CONDITIONAL"},
        )
        stage = generate.build_stage(
            "my-stage.md", "my-stage", "inception", text, ["classic", "bugfix"]
        )
        self.assertEqual(stage.slug, "my-stage")
        self.assertEqual(stage.execution, "CONDITIONAL")
        self.assertEqual(stage.scopes["bugfix"], "CONDITIONAL")

    def test_incomplete_scopes_keyset_errors(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic", "bugfix"]
            )
        self.assertIn("scopes key set", str(ctx.exception))

    def test_always_stage_must_execute_everywhere(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "ALWAYS",
            {"classic": "EXECUTE", "bugfix": "SKIP"},
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic", "bugfix"]
            )
        self.assertIn("ALWAYS stage must be EXECUTE", str(ctx.exception))


class Rule16AdvisoryTests(unittest.TestCase):
    def test_all_producers_skipped_warns(self):
        producer = _warn_stage(
            "producer",
            produces=["artifact.md"],
            scopes={"classic": "SKIP", "bugfix": "EXECUTE"},
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE", "bugfix": "EXECUTE"},
        )
        warnings = generate.compute_warnings(
            [producer, consumer], ["classic", "bugfix"]
        )
        rule16 = [w for w in warnings if "all producer stages are SKIP" in w]
        self.assertEqual(len(rule16), 1)
        self.assertIn("'classic'", rule16[0])
        self.assertIn("'consumer'", rule16[0])

    def test_executing_producer_does_not_warn(self):
        producer = _warn_stage(
            "producer",
            produces=["artifact.md"],
            scopes={"classic": "SKIP", "bugfix": "EXECUTE"},
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE", "bugfix": "EXECUTE"},
        )
        warnings = generate.compute_warnings(
            [producer, consumer], ["bugfix"]
        )
        self.assertFalse(
            [w for w in warnings if "all producer stages are SKIP" in w]
        )

    def test_for_each_consumer_is_exempt(self):
        producer = _warn_stage(
            "producer",
            produces=["artifact.md"],
            scopes={"classic": "SKIP"},
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE"},
            for_each="unit-of-work",
        )
        warnings = generate.compute_warnings([producer, consumer], ["classic"])
        self.assertFalse(
            [w for w in warnings if "all producer stages are SKIP" in w]
        )


# ---------------------------------------------------------------------------
# 3. Integration tests (temp copies only; never touch the real skill files)
# ---------------------------------------------------------------------------


class IntegrationTests(unittest.TestCase):
    def _copy_skill(self, tmp):
        dest = os.path.join(tmp, "aidlc-workflows")
        shutil.copytree(SKILL_ROOT, dest)
        return dest

    def test_idempotent_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = self._copy_skill(tmp)
            first = _run_generate(dest)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = _snapshot(dest)
            second = _run_generate(dest)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("0 section(s) regenerated", second.stdout)
            self.assertEqual(_snapshot(dest), before)

    def test_drift_detected_in_temp_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = self._copy_skill(tmp)
            self.assertEqual(_run_generate(dest).returncode, 0)

            target = os.path.join(dest, "SKILL.md")
            with open(target, "r", encoding="utf-8", newline="") as handle:
                text = handle.read()

            def inject(match):
                return match.group(0) + "\nDRIFTED CONTENT\n"

            new_text, count = re.subn(
                r"<!-- BEGIN GENERATED: [A-Za-z0-9_-]+[^\r\n]*?-->",
                inject,
                text,
                count=1,
            )
            self.assertEqual(count, 1)
            self.assertNotEqual(new_text, text)
            with open(target, "w", encoding="utf-8", newline="") as handle:
                handle.write(new_text)

            result = _run_generate(dest, check=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("DRIFT", result.stdout)

    def test_real_repo_check_is_clean(self):
        result = subprocess.run(
            [sys.executable, GENERATE_PATH, "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All generated sections up to date.", result.stdout)


if __name__ == "__main__":
    unittest.main()
