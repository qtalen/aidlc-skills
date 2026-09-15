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
> **Runtime neutrality**: Frontmatter remains the **single source of truth** for
> the stage inventory. Beyond authoring, the skill has exactly one runtime
> dependency: the orchestration engine (`scripts/engine.py`, Python 3.8+
> standard library), a required runtime component. The engine reads only the
> author-time compiled artifact `scripts/data/stage-graph.json` and **never
> parses frontmatter** at runtime. The contract defined here stays
> engine-agnostic: any harness that can load the skill and run a shell is
> supported.

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
| `depth` | string | optional | `adaptive` \| `minimal` \| `standard` \| `comprehensive`. Per `depth-levels.md`, all stages scale detail — this field only records a fixed override when one exists. **Omitted means undeclared** (no default is assumed); only an explicit `adaptive` renders the "Adaptive depth" annotation in generated lists. The active scope's default depth (§6) applies workflow-wide unless the user overrides |
| `scopes` | object | yes | Per-scope membership map: `{<scope-name>: EXECUTE \| SKIP \| CONDITIONAL}` — see §6. Must contain **exactly** the scopes registered in `references/common/scopes/` (no missing, no extras). `ALWAYS` stages must be `EXECUTE` in every scope |

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
- Workflow-owned files may be attributed to the stage that conceptually owns
  them even when another rule performs the write — e.g. `audit.md` is listed
  under `workspace-detection`'s `produces` (it owns workflow bootstrap) while
  the actual append discipline lives in SKILL.md. Keep such attributions
  rare and deliberate.

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

## 6. Scopes

A **scope** is a named, pre-approved pruning profile: it decides up front which
CONDITIONAL stages are in the plan, so a bugfix-class task never gets asked
about user stories or design ceremonies. Scopes were introduced in Phase 2
(see `docs/integration-plan.md`).

### 6.1 Scope registry

Scopes are defined one per file under `references/common/scopes/<name>.md`,
with their own frontmatter:

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `name` | string | yes | kebab-case; **must match the filename stem** |
| `depth` | string | yes | `minimal` \| `standard` \| `comprehensive` — the workflow-wide default depth this scope implies (user-overridable) |
| `keywords` | string[] | yes | May be empty. Word-boundary-matched triggers used by Requirements Analysis to select a scope — auto-applied only on an unambiguous unique match; otherwise they narrow the minimal candidate set (see §6.3) |
| `description` | string | yes | One sentence — shown in the scope catalog |
| `default` | boolean | optional per file, **exactly one across the registry** | `true` on exactly one scope (`classic`): the fallback when no keywords match and the user names none |

The body explains *why these stages, why skip those* — loaded on demand (only
the selected scope's file, when justifying the plan to the user).

### 6.2 Membership values

Each stage declares its membership in every scope via the `scopes` map:

| Value | Meaning |
|-------|---------|
| `EXECUTE` | Stage is in the plan for this scope |
| `SKIP` | Stage is excluded from the plan for this scope |
| `CONDITIONAL` | Stage is in the plan only when its own `condition` holds (e.g. `reverse-engineering` runs in `bugfix` only on brownfield) |

Rules:

- `ALWAYS` stages: `EXECUTE` in every scope (scopes only prune CONDITIONAL stages).
- `classic` is the reference scope: it reproduces v1.0 adaptive behavior, so its
  CONDITIONAL stages stay `CONDITIONAL` (self-select from project context).
- Scope decides the *starting plan*; the user can still add/remove individual
  stages at the Workflow Planning gate (existing workflow-changes mechanism).
- **Implicit single unit**: when a plan skips `units-generation`, per-unit
  stages in that plan run exactly once for the whole task as one implicit unit
  (see `references/inception/workflow-planning.md` Step 3.0). Their required
  consumes of unit artifacts are moot in that plan (§2 `consumes[].required`).

### 6.3 Selection and depth binding

- Scope is selected during **Requirements Analysis**: keyword heuristic →
  auto-select on an unambiguous unique match (no gate; the user is informed
  after the fact) → on genuine ambiguity, a minimal-candidate (1–2 options)
  chat question. An explicit scope name from the user always wins.
- The selected scope's `depth` becomes the workflow default depth; the user may
  override at the Workflow Planning gate or any later gate.
- The active scope is recorded in `aidlc-docs/aidlc-state.md`.

---

## 7. Validation rules (enforced by `scripts/generate.py`)

Hard failures (non-zero exit):

1. **Unknown key** in frontmatter (including reserved-but-inactive keys).
2. `slug` ≠ filename stem, or non-kebab-case.
3. `phase` ≠ containing directory name.
4. Missing required field; wrong type; enum violation.
5. `condition` empty or missing.
6. `for_each` present with a value other than `unit-of-work`.
7. `requires_stage` entry not a known stage slug.
8. Cycle detected in the `requires_stage` graph.
9. `scopes` missing, or its key set ≠ the registered scope names
   (every stage must declare every scope explicitly — adding a scope to the
   registry fails the build until each stage files its membership).
10. `scopes` value outside `EXECUTE` / `SKIP` / `CONDITIONAL`.
11. An `ALWAYS` stage with a non-`EXECUTE` value in any scope.
12. Scope registry file: `name` ≠ filename stem, missing field, bad `depth`
    enum, or **zero or more than one** scope with `default: true`.

Advisory warnings (exit zero, printed):

13. `consumes[].artifact` matches no stage's `produces` (likely typo or
    missing producer).
14. A `consumes[].required: true` artifact whose producer is not in
    `requires_stage` (data dependency missing its DAG edge).
15. `produces` entry colliding with another stage's `produces`
    (two writers for one artifact).
16. Per-scope dependency gap: in some scope, a non-per-unit stage that is not
    SKIP has a `consumes[].required: true` entry (without `conditional_on`)
    whose producers are **all** SKIP in that scope. Per-unit (`for_each`)
    stages are exempt — they are covered by the implicit single unit
    convention (§6.2); `conditional_on` consumes are exempt by design.

---

## 8. Consumers of this contract

| Consumer | When | What it reads |
|---|---|---|
| `scripts/generate.py` | Author-time (skill maintenance) | All fields + the scope registry; regenerates every `GENERATED` section (including the scope catalog and scope matrix), compiles `scripts/data/stage-graph.json`; validates §7 |
| The model (runtime) | Workflow execution | Reads frontmatter inline with the stage body; `condition`/`gate` inform stage behavior; the **generated** scope catalog/matrix (not raw frontmatter) drive scope selection and plan pruning |
| Orchestration engine (`scripts/engine.py`) | Runtime | The compiled `scripts/data/stage-graph.json` (author-time artifact); **zero changes to these files** |

---

## 9. Worked example

`references/inception/requirements-analysis.md` after contract application:

```yaml
---
slug: requirements-analysis
phase: inception
execution: ALWAYS
condition: Always executes with adaptive depth — every request needs its intent and requirements assessed; depth (minimal/standard/comprehensive) scales with clarity, complexity, and risk
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
scopes:
  classic: EXECUTE
  bugfix: EXECUTE
  refactor: EXECUTE
  security-patch: EXECUTE
  infra: EXECUTE
  express: EXECUTE
---
```

Notes: no `for_each` (once per workflow), no `workspace_writes` (docs only).
`scopes` lists every registered scope explicitly — `requirements-analysis` is an
`ALWAYS` stage, so it is `EXECUTE` in all six. The rule body below the
frontmatter is unchanged from v1.0.

---

## 10. Cross-references

- `docs/integration-plan.md` — the overall fork/integration roadmap (Phases 0–4+)
- `references/common/process-overview.md` — stage inventory (generated)
- `references/common/scopes/` — scope registry (§6)
- `references/common/depth-levels.md` — depth semantics
- v2.0 reference (read-only): `opencode/.aidlc/aidlc-common/protocols/stage-definition.md`
  — the superset this contract borrows from
