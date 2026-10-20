# Review rubric index

Resolve a stage's `review_class` to its rubric file. The main session reads
only this index (~zero context cost); the rubric itself is read by the
reviewer in its own session (lazy + pull — see `../review-delegation.md`).

| Class | Rubric | Scope (one line) |
|---|---|---|
| `requirements-consistency` | `rubrics/requirements-consistency.md` | Internal consistency, observable boundaries, falsifiable non-goals, testable acceptance criteria, no silent narrowing or scope creep |
| `design-soundness` | `rubrics/design-soundness.md` | Decision risk in design artifacts, drift vs requirements, missing failure paths, integration risk (run on the strongest available model tier) |
| `code-quality` | `rubrics/code-quality.md` | Bugs / performance / architecture in the produced code, and its match against design & requirements artifacts |

Deferred to Phase 5B (do not invent rubrics for them): `evidence-credibility`
(test-evidence trustworthiness) and `security-threat` (security threat
reasoning). Classes may be composed in future phases (e.g., a
security-patch code review appends the security rubric); today each wired
stage uses exactly one.
