# Stage Contract — Frontmatter Specification

> **Authority**: This document is the authoritative contract for the YAML frontmatter
> of every stage rule file under `references/<phase>/`. The generator script
> (`scripts/generate.py`) validates against this document and regenerates all
> derived stage-inventory sections from it.
>
> **Purpose**: Stage frontmatter is the **single source of truth** for the stage
> inventory. Human-readable lists elsewhere (SKILL.md, process-overview,
> welcome-message, terminology, session-continuity, workflow-planning templates,
> autonomous-mode) are **generated artifacts** between
> `<!-- BEGIN GENERATED: <key> -->` / `<!-- END GENERATED -->` markers — never
> hand-edit them.
>
> **Runtime neutrality**: Frontmatter is inert metadata at runtime. The skill
> remains pure Markdown; any harness loads it unchanged. The contract is designed
> *engine-ready*: a future orchestration engine (see `docs/integration-plan.md`
> Phase 3) consumes these same files with zero modification.

---

## 1. File layout

```yaml
---
# YAML frontmatter — authored contract (this document)
---

# [Stage Title]

# ... existing rule body, unchanged ...
```

- Frontmatter starts at line 1 (`---` opener) and ends at the closing `---`.
- The rule body below the frontmatter is **not** restructured by this contract
  (unlike v2.0's `## Steps` compartment rule). Bodies stay as authored.
- One stage per file; filename stem must equal `slug`.

---

## 2. Authored fields

All fields are required unless marked optional.
The generator **rejects unknown keys** — see §5 for the reserved namespace.

| Field | Type | Required | Enum / Constraint |
|-------|------|----------|-------------------|
| `slug` | string | yes | kebab-case; **must match the filename stem** |
| `phase` | string | yes | `inception` \| `construction` \| `operations`; **must match the containing directory** |
| `execution` | string | yes | `ALWAYS` \| `CONDITIONAL` |
| `condition` | string | yes | Free-form, 1–3 sentences. For `ALWAYS`: why it always runs. For `CONDITIONAL`: a compact summary of the Execute-IF / Skip-IF branches (the full prose stays in the body / SKILL.md stage block) |
| `gate` | string | yes | `none` \| `approve-continue` \| `two-option` — see §3 |
| `produces` | string[] | yes | May be empty. Artifact paths **relative to `aidlc-docs/`** (e.g. `inception/requirements/requirements.md`). Glob `*` allowed for per-unit trees (e.g. `construction/{unit-name}/code/`) — see §4 |
| `consumes` | object[] | yes | May be empty. Each entry: `{artifact, required, conditional_on?}` — see below |
| `consumes[].artifact` | string | yes per entry | `aidlc-docs/`-relative path or glob, same shape as `produces` entries |
| `consumes[].required` | boolean | yes per entry | `true` = if the producing stage executes, this input must exist. Scoped to the active plan: scopes/plans that skip the producer make the consume moot |
| `consumes[].conditional_on` | string | optional | `brownfield` \| `greenfield`. Omit for unconditional consumes |
| `requires_stage` | string[] | yes | May be empty. Stage slugs. Two roles: (1) semantic data dependency; (2) presentation-order edge. Must form an acyclic graph within the whole workflow |
| `for_each` | string | optional | `unit-of-work` is the only legal value today. Marks a per-unit stage (runs once per unit in the per-unit loop). Omit for once-per-workflow stages |
| `workspace_writes` | boolean | optional | Default `false`. `true` marks a stage that writes application code to the workspace root (not only docs under `aidlc-docs/`). Today only `code-generation` |
| `depth` | string | optional | `adaptive` \| `minimal` \| `standard` \| `comprehensive`; default `adaptive`. Per `depth-levels.md`, all stages scale detail — this field only records a fixed override when one exists |
| `scopes` | string[] | **reserved** | Phase 2 fills this (see `docs/integration-plan.md`). Must be **absent or empty** in Phase 0/1; the generator rejects non-empty values until Phase 2 lands |

---

## 3. Gate types

| `gate` value | Meaning | Current stages |
|---|---|---|
| `none` | No approval gate; presents completion message and proceeds automatically | workspace-detection |
| `approve-continue` | Inception style: `✅ Approve & Continue` / `🔧 Request Changes`, optionally a conditional third option (e.g. "Add User Stories") defined in the stage body | all gated inception stages, build-and-test |
| `two-option` | Construction style: exactly `🔧 Request Changes` / `✅ Continue to Next Stage` (NO EMERGENT BEHAVIOR per SKILL.md) | per-unit construction stages |

The `operations` placeholder stage uses `gate: none` (it produces nothing and
ends the workflow after Build and Test).

---

## 4. Artifact path conventions

- Paths are relative to the workspace's `aidlc-docs/` directory, POSIX-style
  (`/` separators), no leading slash, no `aidlc-docs/` prefix.
- `{unit-name}` is the per-unit placeholder for construction unit trees
  (e.g. `construction/{unit-name}/functional-design/business-logic-model.md`).
- A trailing `/*` glob means "every file in this directory"
  (e.g. `inception/reverse-engineering/*`).
- `produces` lists **documentation artifacts only**. Application code is covered
  by `workspace_writes: true`, not enumerated in `produces`.
- Question files (`*-questions.md`, clarification files) **are** listed in
  `produces` — session-continuity's loading lists are generated from
  `produces`/`consumes`.

---

## 5. Reserved namespace (future phases)

These keys are **reserved** — documented here so future additions never collide.
No stage declares them today; the generator rejects them until the owning phase
lands (see `docs/integration-plan.md`):

| Key | Owning phase | Purpose |
|-----|--------------|---------|
| `lead_agent`, `support_agents`, `mode` | Phase 4+ (persona system) | Who performs the stage; communication topology |
| `reviewer`, `review_artifact`, `reviewer_max_iterations`, `review_class` | Phase 4+ (reviewer contracts) | Dedicated review pass before the gate |
| `sensors` | Phase 4+ (sensor checklists) | Self-check rules bound to the stage |
| `summary_confirmation` | Phase 4+ | Pre-generation consolidated-summary stop |

Rationale for exclusion now: the persona/reviewer/memory systems were
deliberately deferred (integration-plan decisions D3/D4). The contract only
carries what the current workflow actually uses, plus what the future engine
needs for routing (`slug/phase/execution/requires_stage/for_each/scopes`).

---

## 6. Validation rules (enforced by `scripts/generate.py`)

Hard failures (non-zero exit):

1. **Unknown key** in frontmatter (including reserved-but-inactive keys).
2. `slug` ≠ filename stem, or non-kebab-case.
3. `phase` ≠ containing directory name.
4. Missing required field; wrong type; enum violation.
5. `condition` empty or missing.
6. `for_each` present with a value other than `unit-of-work`.
7. `requires_stage` entry not a known stage slug.
8. Cycle detected in the `requires_stage` graph.
9. `scopes` non-empty (until Phase 2).

Advisory warnings (exit zero, printed):

10. `consumes[].artifact` matches no stage's `produces` (likely typo or
    missing producer).
11. A `consumes[].required: true` artifact whose producer is not in
    `requires_stage` (data dependency missing its DAG edge).
12. `produces` entry colliding with another stage's `produces`
    (two writers for one artifact).

---

## 7. Consumers of this contract

| Consumer | When | What it reads |
|---|---|---|
| `scripts/generate.py` | Author-time (skill maintenance) | All fields; regenerates every `GENERATED` section; validates §6 |
| The model (runtime) | Workflow execution | Reads frontmatter inline with the stage body; `condition`/`gate` inform stage behavior |
| Future scope matrix (Phase 2) | Author-time | `scopes` transpose → EXECUTE/SKIP grid |
| Future engine (Phase 3) | Runtime | Routing/state fields; **zero changes to these files** |

---

## 8. Worked example

`references/inception/requirements-analysis.md` after contract application:

```yaml
---
slug: requirements-analysis
phase: inception
execution: ALWAYS
condition: Always executes with adaptive depth — every request needs its intent
  and requirements assessed; depth (minimal/standard/comprehensive) scales with
  clarity, complexity, and risk
gate: approve-continue
produces:
  - inception/requirements/requirements.md
  - inception/requirements/requirement-verification-questions.md
consumes:
  - artifact: inception/reverse-engineering/*
    required: true
    conditional_on: brownfield
requires_stage:
  - workspace-detection
  - reverse-engineering
depth: adaptive
---
```

Notes: no `for_each` (once per workflow), no `workspace_writes` (docs only),
no `scopes` (reserved for Phase 2). The rule body below the frontmatter is
unchanged from v1.0.

---

## 9. Cross-references

- `docs/integration-plan.md` — the overall fork/integration roadmap (Phases 0–4+)
- `references/common/process-overview.md` — stage inventory (generated)
- `references/common/depth-levels.md` — depth semantics
- v2.0 reference (read-only): `opencode/.aidlc/aidlc-common/protocols/stage-definition.md`
  — the superset this contract borrows from
