#!/usr/bin/env python3
"""Unit + integration tests for the author-time generator (generate.py).

Run from the repository root:

    python -m unittest discover -s scripts\\tests -v

Pure standard library. The ``scripts`` directory is intentionally *not* made a
package: the module under test is loaded by absolute path via importlib, and
integration tests exercise it as a subprocess against a throwaway copy of the
skill tree (the real skill files are never written to).

Contract §7 rule -> fixture -> tests map (rules 1-12 hard-fail, 13-16
advisory; rules 9, 11 and 16 were already covered before this table existed):

| Rule | Summary | Fixture | Tests |
|------|---------|---------|-------|
| 1 | unknown frontmatter keys rejected (incl. reserved `reviewer:`/`sensors:`) | build_stage() in memory | Rule1Tests |
| 2 | slug is kebab-case and equals filename stem | build_stage() in memory | Rule2Tests |
| 3 | phase matches containing directory | build_stage() in memory | Rule3Tests |
| 4 | required keys present, list-typed, enum-valid | build_stage() in memory | Rule4Tests |
| 5 | condition is a non-empty string | build_stage() in memory | Rule5Tests |
| 6 | for_each only accepts 'unit-of-work' | build_stage() in memory | Rule6Tests |
| 7 | requires_stage references known slugs | _warn_stage() + _validate_references() | Rule7Tests |
| 8 | requires_stage graph is acyclic | _warn_stage() + _detect_cycles() | Rule8Tests |
| 9 | scopes key set equals registered scopes | build_stage() in memory | covered by test_incomplete_scopes_keyset_errors (StageValidationTests) |
| 10 | scope values in EXECUTE/SKIP/CONDITIONAL | build_stage() in memory | Rule10Tests |
| 11 | ALWAYS stage is EXECUTE in every scope | build_stage() in memory | covered by test_always_stage_must_execute_everywhere (StageValidationTests) |
| 12 | scope registry files valid (name/depth/keys/default) | load_scopes() with generate.SKILL_ROOT patched to a temp dir (module global read at call time; generate.py:31, :534-535) — no tree copy needed | Rule12Tests |
| 13 | every consume artifact matches some producer | _warn_stage() + compute_warnings() | Rule13Tests |
| 14 | required consume's producer listed in requires_stage | _warn_stage() + compute_warnings() | Rule14Tests |
| 15 | an artifact is not written by two stages | _warn_stage() + compute_warnings() | Rule15Tests |
| 16 | required consume not left without executing producer | _warn_stage() + compute_warnings() | covered by Rule16AdvisoryTests |
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
# 2b. Contract hard-rule tests (stage-contract.md §7, rules 1-15)
# ---------------------------------------------------------------------------


def _scope_fm(name, depth="standard", default=None, omit=()):
    """Build a minimal scope registry frontmatter + H1 body."""
    lines = ["---", "name: " + name]
    if "depth" not in omit:
        lines.append("depth: " + depth)
    lines.append("keywords: []")
    if "description" not in omit:
        lines.append('description: "Test scope"')
    if default is not None:
        lines.append("default: " + default)
    lines.append("---")
    lines.append("")
    lines.append("# " + name)
    return "\n".join(lines)


class Rule1Tests(unittest.TestCase):
    def test_unknown_key_rejected(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
        ).replace("---\nslug:", "---\nbogus_key: 1\nslug:", 1)
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("unknown frontmatter key(s)", str(ctx.exception))
        self.assertIn("bogus_key", str(ctx.exception))

    def test_reserved_key_reviewer_rejected(self):
        # Rule 1: 'reviewer' is reserved (contract §5), not an allowed key.
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
        ).replace("---\nslug:", "---\nreviewer: none\nslug:", 1)
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("unknown frontmatter key(s)", str(ctx.exception))
        self.assertIn("reviewer", str(ctx.exception))

    def test_reserved_key_sensors_rejected(self):
        # Rule 1: 'sensors' is reserved (contract §5), not an allowed key.
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
        ).replace("---\nslug:", "---\nsensors: []\nslug:", 1)
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("unknown frontmatter key(s)", str(ctx.exception))
        self.assertIn("sensors", str(ctx.exception))


class Rule2Tests(unittest.TestCase):
    def test_slug_must_equal_filename_stem(self):
        text = _stage_fm(
            "my-stage", "inception", "CONDITIONAL", {"classic": "EXECUTE"}
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "other-name.md", "other-name", "inception", text, ["classic"]
            )
        self.assertIn("must equal filename stem", str(ctx.exception))

    def test_slug_must_be_kebab_case(self):
        text = _stage_fm(
            "My_Stage", "inception", "CONDITIONAL", {"classic": "EXECUTE"}
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "My_Stage.md", "My_Stage", "inception", text, ["classic"]
            )
        self.assertIn("is not kebab-case", str(ctx.exception))


class Rule3Tests(unittest.TestCase):
    def test_phase_must_match_directory(self):
        text = _stage_fm(
            "my-stage", "construction", "CONDITIONAL", {"classic": "EXECUTE"}
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("must match containing directory", str(ctx.exception))


class Rule4Tests(unittest.TestCase):
    def test_missing_required_key_gate(self):
        # Rule 4: drop the gate line from an otherwise valid frontmatter.
        text = _stage_fm(
            "my-stage", "inception", "CONDITIONAL", {"classic": "EXECUTE"}
        ).replace("gate: none\n", "")
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("missing required key", str(ctx.exception))
        self.assertIn("'gate'", str(ctx.exception))

    def test_produces_must_be_list(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
            produces="not-a-list",
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("produces must be a list", str(ctx.exception))

    def test_execution_enum_violation(self):
        text = _stage_fm(
            "my-stage", "inception", "SOMETIMES", {"classic": "EXECUTE"}
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("execution must be one of", str(ctx.exception))


class Rule5Tests(unittest.TestCase):
    def test_empty_condition_rejected(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "EXECUTE"},
            condition="",
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("condition must be a non-empty string", str(ctx.exception))


class Rule6Tests(unittest.TestCase):
    def test_for_each_must_be_unit_of_work(self):
        text = _stage_fm(
            "my-stage", "inception", "CONDITIONAL", {"classic": "EXECUTE"}
        ).replace("---\nslug:", "---\nfor_each: per-module\nslug:", 1)
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic"]
            )
        self.assertIn("for_each must be 'unit-of-work'", str(ctx.exception))


class Rule7Tests(unittest.TestCase):
    def test_unknown_requires_stage_slug(self):
        stages = [_warn_stage("a", requires_stage=["nonexistent-stage"])]
        with self.assertRaises(generate.HardError) as ctx:
            generate._validate_references(stages)
        self.assertIn("requires_stage references unknown slug", str(ctx.exception))
        self.assertIn("nonexistent-stage", str(ctx.exception))


class Rule8Tests(unittest.TestCase):
    def test_requires_stage_cycle_detected(self):
        a = _warn_stage("a", requires_stage=["b"])
        b = _warn_stage("b", requires_stage=["a"])
        by_slug = {"a": a, "b": b}
        with self.assertRaises(generate.HardError) as ctx:
            generate._detect_cycles([a, b], by_slug)
        self.assertIn("cycle detected", str(ctx.exception))


class Rule10Tests(unittest.TestCase):
    def test_invalid_scope_value_rejected(self):
        text = _stage_fm(
            "my-stage",
            "inception",
            "CONDITIONAL",
            {"classic": "MAYBE", "bugfix": "EXECUTE"},
        )
        with self.assertRaises(generate.HardError) as ctx:
            generate.build_stage(
                "my-stage.md", "my-stage", "inception", text, ["classic", "bugfix"]
            )
        self.assertIn("scopes.classic must be one of", str(ctx.exception))


class Rule12Tests(unittest.TestCase):
    def setUp(self):
        self._orig_root = generate.SKILL_ROOT
        self._root = tempfile.mkdtemp()
        generate.SKILL_ROOT = self._root
        self._scopes_dir = os.path.join(
            self._root, "references", "common", "scopes"
        )
        os.makedirs(self._scopes_dir)
        self.addCleanup(self._restore)

    def _restore(self):
        generate.SKILL_ROOT = self._orig_root
        shutil.rmtree(self._root, ignore_errors=True)

    def _write_scope(self, filename, text):
        with open(
            os.path.join(self._scopes_dir, filename),
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            handle.write(text)

    def test_name_must_equal_stem(self):
        # Rule 12: one valid registry file plus an offender.
        self._write_scope("alpha.md", _scope_fm("alpha", default="true"))
        self._write_scope("beta.md", _scope_fm("alpha"))
        with self.assertRaises(generate.HardError) as ctx:
            generate.load_scopes()
        self.assertIn("must equal filename stem", str(ctx.exception))

    def test_missing_required_scope_key(self):
        # Rule 12: description omitted.
        self._write_scope("alpha.md", _scope_fm("alpha", default="true"))
        self._write_scope("beta.md", _scope_fm("beta", omit=("description",)))
        with self.assertRaises(generate.HardError) as ctx:
            generate.load_scopes()
        self.assertIn("missing required scope key", str(ctx.exception))
        self.assertIn("'description'", str(ctx.exception))

    def test_depth_enum_violation(self):
        # Rule 12: 'deep' is not a valid scope depth.
        self._write_scope("alpha.md", _scope_fm("alpha", default="true"))
        self._write_scope("beta.md", _scope_fm("beta", depth="deep"))
        with self.assertRaises(generate.HardError) as ctx:
            generate.load_scopes()
        self.assertIn("depth must be one of", str(ctx.exception))

    def test_zero_defaults_rejected(self):
        # Rule 12: a legal file that does not opt in as default still needs
        # exactly one default somewhere.
        self._write_scope("alpha.md", _scope_fm("alpha"))
        with self.assertRaises(generate.HardError) as ctx:
            generate.load_scopes()
        self.assertIn("no scope declares default: true", str(ctx.exception))

    def test_two_defaults_rejected(self):
        # Rule 12: two defaults must fail.
        self._write_scope("alpha.md", _scope_fm("alpha", default="true"))
        self._write_scope("beta.md", _scope_fm("beta", default="true"))
        with self.assertRaises(generate.HardError) as ctx:
            generate.load_scopes()
        self.assertIn(
            "more than one scope declares default: true", str(ctx.exception)
        )


class Rule13Tests(unittest.TestCase):
    def test_unmatched_consume_warns(self):
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE"},
        )
        warnings = generate.compute_warnings([consumer], ["classic"])
        self.assertTrue(
            [w for w in warnings if "matches no stage's produces" in w]
        )

    def test_matched_producer_does_not_warn(self):
        producer = _warn_stage(
            "producer", produces=["artifact.md"], scopes={"classic": "EXECUTE"}
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE"},
        )
        warnings = generate.compute_warnings([producer, consumer], ["classic"])
        self.assertFalse(
            [w for w in warnings if "matches no stage's produces" in w]
        )


class Rule14Tests(unittest.TestCase):
    def test_required_producer_missing_from_requires_stage(self):
        producer = _warn_stage(
            "producer", produces=["artifact.md"], scopes={"classic": "EXECUTE"}
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            scopes={"classic": "EXECUTE"},
        )
        warnings = generate.compute_warnings([producer, consumer], ["classic"])
        self.assertTrue([w for w in warnings if "not in requires_stage" in w])

    def test_required_producer_listed_in_requires_stage(self):
        producer = _warn_stage(
            "producer", produces=["artifact.md"], scopes={"classic": "EXECUTE"}
        )
        consumer = _warn_stage(
            "consumer",
            consumes=[_consume("artifact.md")],
            requires_stage=["producer"],
            scopes={"classic": "EXECUTE"},
        )
        warnings = generate.compute_warnings([producer, consumer], ["classic"])
        self.assertFalse([w for w in warnings if "not in requires_stage" in w])


class Rule15Tests(unittest.TestCase):
    def test_duplicate_producer_warns(self):
        first = _warn_stage(
            "p1", produces=["artifact.md"], scopes={"classic": "EXECUTE"}
        )
        second = _warn_stage(
            "p2", produces=["artifact.md"], scopes={"classic": "EXECUTE"}
        )
        warnings = generate.compute_warnings([first, second], ["classic"])
        self.assertTrue([w for w in warnings if "produces collision" in w])

    def test_distinct_producers_do_not_warn(self):
        first = _warn_stage(
            "p1", produces=["a.md"], scopes={"classic": "EXECUTE"}
        )
        second = _warn_stage(
            "p2", produces=["b.md"], scopes={"classic": "EXECUTE"}
        )
        warnings = generate.compute_warnings([first, second], ["classic"])
        self.assertFalse([w for w in warnings if "produces collision" in w])


# ---------------------------------------------------------------------------
# 3. Compile-to-JSON artifact (stage-graph.json)
# ---------------------------------------------------------------------------


class StageGraphTests(unittest.TestCase):
    """The compiled graph must be deterministic and faithful to frontmatter."""

    @classmethod
    def setUpClass(cls):
        scopes = generate.load_scopes()
        scope_order = generate.compute_scope_order(scopes)
        scope_names = [scope.name for scope in scope_order]
        stages = generate.load_stages(scope_names)
        ordered = generate.compute_display_order(stages)
        cls.graph = generate.build_stage_graph(ordered, scope_order)
        cls.ordered = ordered
        cls.scope_names = scope_names

    def test_state_version(self):
        self.assertEqual(self.graph["state_version"], 1)

    def test_stage_order_matches_display_order(self):
        self.assertEqual(
            [stage["slug"] for stage in self.graph["stages"]],
            [stage.slug for stage in self.ordered],
        )

    def test_scope_order_default_first_then_alpha(self):
        names = [scope["name"] for scope in self.graph["scopes"]]
        self.assertEqual(names[0], "classic")
        self.assertEqual(names, sorted(names, key=lambda n: (n != "classic", n)))

    def test_stage_fields_match_frontmatter(self):
        by_slug = {stage["slug"]: stage for stage in self.graph["stages"]}
        stage = by_slug["requirements-analysis"]
        self.assertEqual(stage["name"], "Requirements Analysis")
        self.assertEqual(stage["phase"], "inception")
        self.assertEqual(stage["execution"], "ALWAYS")
        self.assertEqual(stage["gate"], "approve-continue")
        self.assertIs(stage["for_each"], False)
        self.assertIs(stage["workspace_writes"], False)
        self.assertEqual(
            stage["consumes"],
            [
                {
                    "artifact": "inception/reverse-engineering/*",
                    "required": True,
                    "conditional_on": "brownfield",
                }
            ],
        )
        self.assertEqual(
            sorted(stage["scopes"].keys()), sorted(self.scope_names)
        )
        self.assertEqual(stage["scopes"]["classic"], "EXECUTE")

    def test_boolean_flags_are_real_booleans(self):
        by_slug = {stage["slug"]: stage for stage in self.graph["stages"]}
        self.assertIs(by_slug["code-generation"]["for_each"], True)
        self.assertIs(by_slug["code-generation"]["workspace_writes"], True)
        for stage in self.graph["stages"]:
            self.assertIsInstance(stage["for_each"], bool)
            self.assertIsInstance(stage["workspace_writes"], bool)

    def test_consumes_shape_is_complete(self):
        for stage in self.graph["stages"]:
            for consume in stage["consumes"]:
                self.assertEqual(
                    set(consume.keys()),
                    {"artifact", "required", "conditional_on"},
                )

    def test_scopes_registry_matches_scope_files(self):
        scopes = generate.load_scopes()
        by_name = {scope["name"]: scope for scope in self.graph["scopes"]}
        for scope in scopes:
            entry = by_name[scope.name]
            self.assertEqual(entry["depth"], scope.depth)
            self.assertEqual(entry["keywords"], list(scope.keywords))
            self.assertEqual(entry["description"], scope.description)
            self.assertEqual(entry["default"], bool(scope.default))

    def test_serialization_is_deterministic(self):
        scopes = generate.compute_scope_order(generate.load_scopes())
        first = generate.render_stage_graph(self.ordered, scopes)
        second = generate.render_stage_graph(self.ordered, scopes)
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))


# ---------------------------------------------------------------------------
# 4. Integration tests (temp copies only; never touch the real skill files)
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

    def test_stage_graph_bytes_stable_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = self._copy_skill(tmp)
            graph_path = os.path.join(
                dest, "scripts", "data", "stage-graph.json"
            )
            self.assertEqual(_run_generate(dest).returncode, 0)
            with open(graph_path, "rb") as handle:
                first = handle.read()
            self.assertEqual(_run_generate(dest).returncode, 0)
            with open(graph_path, "rb") as handle:
                second = handle.read()
            self.assertEqual(first, second)

    def test_stage_graph_drift_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = self._copy_skill(tmp)
            self.assertEqual(_run_generate(dest).returncode, 0)
            graph_path = os.path.join(
                dest, "scripts", "data", "stage-graph.json"
            )
            with open(graph_path, "r", encoding="utf-8", newline="") as handle:
                text = handle.read()
            self.assertIn('"state_version": 1', text)
            with open(graph_path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text.replace('"state_version": 1', '"state_version": 99'))
            result = _run_generate(dest, check=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("DRIFT: stage-graph.json", result.stdout)

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
