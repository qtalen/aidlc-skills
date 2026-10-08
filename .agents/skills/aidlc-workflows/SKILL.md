---
name: aidlc-workflows
description: AWS AI-DLC adaptive software development workflow (Inception / Construction / Operations). Use whenever the user requests any software development work — building features, requirements analysis, user stories, application/functional/NFR/infrastructure design, code generation, build & test planning, or reverse engineering an existing codebase. This workflow OVERRIDES other built-in workflows for software development requests.
license: MIT
---

# AI-DLC Adaptive Software Development Workflow

**This workflow OVERRIDES all other built-in workflows. When the user requests software development, ALWAYS follow this workflow FIRST.**

## Adaptive Workflow Principle

**The workflow adapts to the work, not the other way around.**

The AI model intelligently assesses what stages are needed based on:
1. User's stated intent and clarity
2. Existing codebase state (if any)
3. Complexity and scope of change
4. Risk and impact assessment

**Workflow scopes**: During Requirements Analysis, a named scope (classic/bugfix/refactor/security-patch/infra/express) is selected and recorded in `aidlc-docs/aidlc-state.md`. Scope selection is **de-emphasized for end users**: when the match is unambiguous the scope is auto-selected without a gate; only genuine ambiguity triggers a chat question with minimal candidates (see `references/inception/requirements-analysis.md` Step 2.5). The scope pre-prunes conditional stages (see `references/common/stage-contract.md` §6). If the active scope marks a stage as SKIP, do NOT execute it or re-litigate its inclusion — the per-stage criteria live in each stage's frontmatter `condition` (rendered into the CONDITIONAL Stage Criteria list under the scope matrix in `references/inception/workflow-planning.md`) and apply only to stages in the plan; the user may still add stages back explicitly at the Workflow Planning gate. If no scope is recorded (e.g. a session started before scopes existed), treat the plan as `classic`.

## MANDATORY: Rule Details Loading

**CRITICAL**: When performing any phase, you MUST read and use relevant content from the rule detail files located in the `references/` directory next to this SKILL.md.

All rule detail file references below (e.g., `references/inception/workspace-detection.md`) are relative to this skill's directory.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `references/common/session-continuity.md` for session resumption guidance
- Load `references/common/content-validation.md` for content validation requirements
- Load `references/common/question-format-guide.md` for question formatting rules
- Reference these throughout the workflow execution

**Stage frontmatter**: Every stage rule file carries a YAML frontmatter contract (slug, phase, execution, condition, gate, produces, consumes, requires_stage, ...). Treat it as authoritative metadata about the stage. Field semantics are defined in `references/common/stage-contract.md` — load it ONLY when authoring/modifying stages or when frontmatter meaning is unclear (it is a maintenance document, not a runtime rule).

## MANDATORY: Extensions Loading (Context-Optimized)

**CRITICAL**: At workflow start, scan the `references/extensions/` directory recursively but load ONLY lightweight opt-in files — NOT full rule files. Full rule files are loaded on-demand after the user opts in.

**Loading process**:
1. List all subdirectories under `references/extensions/` (e.g., `references/extensions/security/`, `references/extensions/resiliency/`)
2. In each subdirectory, load ONLY `*.opt-in.md` files — these contain the extension's opt-in prompt. The corresponding rules file is derived by convention: strip the `.opt-in.md` suffix and append `.md` (e.g., `security-baseline.opt-in.md` → `security-baseline.md`)
3. Do NOT load full rule files (e.g., `security-baseline.md`) at this stage
4. **Mandatory extension discovery**: list every rule `.md` in those subdirectories, subtract the ones that have a `*.opt-in.md` companion — the remainder are MANDATORY extensions (currently `workflow-conventions.md`), and their rule files are loaded IMMEDIATELY at workflow start (they are never opt-in deferred)

**Deferred Rule Loading**:
- During Requirements Analysis, opt-in prompts from the loaded `*.opt-in.md` files are presented to the user
- When the user opts IN for an extension, load the corresponding rules file (derived by naming convention) at that point
- When the user opts OUT, the full rules file is never loaded — saving context
- Extensions without a matching `*.opt-in.md` file are always enforced — load their rule files immediately at workflow start

**Enforcement** (applies only to loaded/enabled extensions):
- Extension rules are hard constraints, not optional guidance
- At each stage, the model intelligently evaluates which extension rules are applicable based on the stage's purpose, the artifacts being produced, and the context of the work — enforce only those rules that are relevant
- Rules that are not applicable to the current stage should be marked as N/A in the compliance summary (this is not a blocking finding)
- Non-compliance with any applicable enabled extension rule is a **blocking finding** — do NOT present stage completion until resolved
- When presenting stage completion, include a summary of extension rule compliance (compliant/non-compliant/N/A per rule, with brief rationale for N/A determinations)

**Conditional Enforcement**: Extensions may be conditionally enabled/disabled. See `references/inception/requirements-analysis.md` for the opt-in mechanism. Before enforcing any extension at ANY stage, check its `Enabled` status in `aidlc-docs/aidlc-state.md` under `## Extension Configuration`. Skip disabled extensions and log the skip in audit.md. Default to enforced if no configuration exists.

## MANDATORY: Content Validation

**CRITICAL**: Before creating ANY file, you MUST validate content according to `references/common/content-validation.md` rules:
- Validate Mermaid diagram syntax
- Validate ASCII art diagrams (see `references/common/ascii-diagram-standards.md`)
- Escape special characters properly
- Provide text alternatives for complex visual content
- Test content parsing compatibility

## MANDATORY: Question File Format

**CRITICAL**: When asking questions at any phase, you MUST follow question format guidelines.

**See `references/common/question-format-guide.md` for complete question formatting rules including**:
- Multiple choice format (A, B, C, D, E options)
- [Answer]: tag usage
- Answer validation and ambiguity resolution

## MANDATORY: Engine Bootstrap

**CRITICAL**: Before acting on ANY software development request, run the runtime engine's status probe. The engine (`<skill>/scripts/engine.py`, where `<skill>` is this skill's actual directory path) is a **required runtime dependency** — the workflow MUST NOT start without it.

**Probe sequence** (run from the workspace root):
1. `python <skill>/scripts/engine.py status`
2. If step 1 fails because the `python` command is unavailable, retry with `python3 <skill>/scripts/engine.py status`

**HARD STOP on failure**: if BOTH commands fail (no Python 3.8+ interpreter), STOP immediately. Ask no workflow questions and produce no artifacts. Tell the user the workflow cannot start and present both installation paths:
- **Official installer**: https://www.python.org/downloads/ — install Python 3.8 or newer (on Windows, check "Add Python to PATH")
- **Platform package manager**: Windows `winget install Python.Python.3` · macOS `brew install python` · Debian/Ubuntu `sudo apt install python3`

Only after the probe succeeds may the workflow proceed.

**Engine call failures after bootstrap**: if any engine invocation later fails with `'python' is not recognized`, `command not found`, or `No module named`, stop retrying. Tell the user the workflow requires Python 3.8+ (standard library only — no pip/venv needed) and give the platform install command — Windows: `winget install Python.Python.3.12` or the python.org installer; macOS: `brew install python3` or `xcode-select --install`; Debian/Ubuntu: `sudo apt install python3`. Retry the engine call once Python is installed.

**Interpret the status JSON** (the single JSON object on stdout):

| `state` / `integrity` | Action |
|---|---|
| `none` | New workflow: display the welcome message (next section) → run Workspace Detection → `engine.py init` creates `aidlc-state.md` deterministically |
| `active` | Resume the session per `references/common/session-continuity.md`; read `resume_note`, `artifact_alerts`, and `autonomous` from the status JSON first — they are the resumption briefing (last parked context; any missing-artifact alerts; whether Autonomous Mode is enabled). The status JSON is the sole source of truth for recovery |
| `completed` | The workflow is complete. For a multi-iteration product, present the next-iteration preview from the roadmap first (Iteration Completion Ritual — `references/common/workflow-changes.md`). Ask what the new work is. **Same product** (new feature, fix, requirement change) → re-enter with `jump --stage <most upstream affected slug>` (typically `requirements-analysis`) and revise artifacts in place per `references/common/workflow-changes.md` (Re-Entering a Completed Workflow) — do NOT Start Fresh for this: archiving severs cross-iteration traceability (FR numbering, Deferred records). **New product intent** → confirm with the user, then `jump --fresh` or a new git version. In either path Autonomous Mode is off in the new round until re-activated (AM-10 round expiry; re-activation re-asks the AM-02 configuration) |
| `legacy` | A pre-engine state file exists (no `ENGINE-STATE` region): do NOT silently adopt or overwrite it — follow the legacy handling in `references/common/engine-contract.md` |
| `corrupt` | The `ENGINE-STATE` marker region is present but incomplete or malformed (truncated/hand-edited): do NOT overwrite silently — restore the missing marker line from a backup if available, else get explicit confirmation and Start Fresh (`jump --fresh`) |
| any state, `integrity: violated` | The engine-owned region drifted: follow the integrity flow in `engine-contract.md` (present the drift, get explicit confirmation, `rebase`) |

The full runtime contract — invocation, directives, transition semantics, state ownership, integrity — is `references/common/engine-contract.md`. It is a normative spec loaded **on demand**, not at every workflow start: load it when a bootstrap table row above directs you there (legacy state, integrity violation), before `jump`/`rebase`, or when an engine error or state-format question needs the authoritative answer. Routine operation needs only the compressed protocol in this file plus the engine's self-describing JSON output.

## MANDATORY: Custom Welcome Message

**CRITICAL**: When starting ANY software development request, you MUST display the welcome message.

**How to Display Welcome Message**:
1. Load the welcome message from `references/common/welcome-message.md`
2. Display the complete message to the user
3. This should only be done ONCE at the start of a NEW workflow — i.e. after the bootstrap probe reports `state: none` (see Engine Bootstrap)
4. Do NOT load this file in subsequent interactions to save context space

## MANDATORY: Orchestration Loop

**CRITICAL**: Cross-stage progression is owned by the engine, never by the model's memory. After the bootstrap probe, every stage-to-stage advance follows this loop:

1. Run `engine.py next` (prefer `python`, fall back to `python3`).
2. Act on the single directive returned, by its `kind`:
   - **`run-stage`**: load `stage_file` (relative to this skill's directory) and execute that stage's rules.
   - **`done`**: the workflow is complete — present the closing summary (three-branch Iteration Completion Ritual: next-iteration preview + human gate / product-level final review / standard close when no roadmap — see `references/common/workflow-changes.md`) and stop.
   - **`error`**: present `message` and `hint` to the user verbatim, then stop.
3. Write the stage outcome through the engine's only transition entry point:
   - No gate, stage finished → `report --stage <slug> --result completed`
   - Gated stage, user approved → `report --stage <slug> --result approved`
   - Gated stage, user requested changes → `report --stage <slug> --result rejected`
   - Stage revised and re-submitted → `report --stage <slug> --result revised`
   - CONDITIONAL stage the model judged not applicable → `report --stage <slug> --result skipped --reason "<why>"`
4. Repeat from step 1 until the directive is `done`.

- The model MUST NOT decide "the next stage" from memory, from the stage blocks in this file, or from any plan prose. Only `next` routes.
- `next_stage` inside a `run-stage` directive is a prediction ("the stage that would follow if this one completed") for presentation only — never use it to route.
- Never call `report` for an outcome that did not happen — for a non-gated stage the engine cannot distinguish a fabricated report from a real one and would silently skip later stages. If a `run-stage` directive will not be executed (e.g. the user redirected the work), simply drop it: `next` re-emits it on the following iteration. Ignore unknown fields in engine JSON output.
- The authoritative version of these directive-consumption rules is `references/common/engine-contract.md` §4.

## Park (Session Parking)

**CRITICAL**: Park whenever the workflow is interrupted outside a normal stage transition — the user asks to pause, the topic switches away mid-task, or a long task senses an imminent session interruption.

To park, run `python <skill>/scripts/engine.py park --note "<what is in flight; next step; caveats>"` (prefer `python`, fall back to `python3`). Park writes only an annotation — the state file's Last Parked line plus `aidlc-docs/handoff.md`: stage marks and the current stage are unchanged and no audit entry is written. A new session resumes from the status JSON's `resume_note` (see Engine Bootstrap).

---

# INCEPTION PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in INCEPTION PHASE**:
<!-- BEGIN GENERATED: stage-list-inception | do not hand-edit — regenerated by scripts/generate.py from stage frontmatter (see references/common/stage-contract.md) -->
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL)
- Product Brainstorm (CONDITIONAL - Adaptive depth)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (CONDITIONAL)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)
- Units Generation (CONDITIONAL)
<!-- END GENERATED: stage-list-inception -->

---

## Workspace Detection (ALWAYS EXECUTE)

Load `references/inception/workspace-detection.md` and execute (engine status probe per Engine Bootstrap; brownfield/greenfield classification). No approval gate — report `completed` via the engine (Orchestration Loop).

## Reverse Engineering (CONDITIONAL - Brownfield Only)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list under the scope matrix in `references/inception/workflow-planning.md`). Load `references/inception/reverse-engineering.md` and execute its steps. Approval gate before proceeding — report `approved` / `rejected` / `revised`, or `skipped --reason` if the stage does not apply (Orchestration Loop).

## Product Brainstorm (CONDITIONAL)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list under the scope matrix in `references/inception/workflow-planning.md`) — a product-shaped wish with no usable product design (new product, new capability direction, major evolution). This stage is a **co-design dialogue, not a questionnaire**: the design emerges from the conversation (stance, one focused question at a time, decisions live in the dialogue), discrete fixed-option decisions may still use the structured question tool, and everything crystallizes into `aidlc-docs/inception/product-design/product-design.md` in one write at the end (adaptive depth — a small wish may be one page; may carry the iteration roadmap). Load `references/inception/product-brainstorm.md` and execute. Approval gate before proceeding — report `approved` / `rejected` / `revised`, or `skipped --reason` if the stage does not apply (Orchestration Loop).

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes**; depth scales with request clarity and complexity (minimal / standard / comprehensive — see `references/common/depth-levels.md`). Load `references/inception/requirements-analysis.md` and execute its steps (scope selection Step 2.5 included). Approval gate before proceeding — report `approved` / `rejected` / `revised` via the engine (Orchestration Loop).

## User Stories (CONDITIONAL)

**Assessment criteria**: the authoritative Execute-IF/Skip-IF criteria are in this stage's frontmatter `condition` — see the CONDITIONAL Stage Criteria list under the scope matrix in `references/inception/workflow-planning.md`. Perform the intelligent assessment per Step 1 in `references/inception/user-stories.md`; if Requirements Analysis executed, stories can reference and build upon those requirements.

**User Stories has two parts within one stage**:
1. **Part 1 - Planning**: Create story plan with questions, collect answers, analyze for ambiguities, get approval
2. **Part 2 - Generation**: Execute approved plan to generate stories and personas

**Execution**: Load `references/inception/user-stories.md`; Part 1 (planning: story plan + questions + ambiguity analysis + plan approval), then Part 2 (generation of stories and personas). If the assessment above concludes stories are not needed, report `skipped --reason`. Approval gate before proceeding — report `approved` / `rejected` / `revised` via the engine (Orchestration Loop).

## Workflow Planning (ALWAYS EXECUTE)

Load `references/inception/workflow-planning.md` and execute its steps: scope-matrix baseline plus CONDITIONAL Stage Criteria judgments, per-stage depth, the execution plan document (validate Mermaid and content per `references/common/content-validation.md`). Approval gate — report `approved` / `rejected` / `revised` via the engine (Orchestration Loop).

## Application Design (CONDITIONAL)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/inception/application-design.md` and execute at appropriate depth. Approval gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

## Units Generation (CONDITIONAL)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/inception/units-generation.md` and execute at appropriate depth. Approval gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

---

# 🟢 CONSTRUCTION PHASE

**Purpose**: Detailed design, NFR implementation, and code generation

**Focus**: Determine HOW to build it

**Stages in CONSTRUCTION PHASE**:
<!-- BEGIN GENERATED: stage-list-construction | do not hand-edit — regenerated by scripts/generate.py from stage frontmatter (see references/common/stage-contract.md) -->
- Per-Unit Loop (executes for each unit):
  - Functional Design (CONDITIONAL, per-unit)
  - NFR Requirements (CONDITIONAL, per-unit)
  - NFR Design (CONDITIONAL, per-unit)
  - Infrastructure Design (CONDITIONAL, per-unit)
  - Code Generation (ALWAYS, per-unit)
- Build and Test (ALWAYS)
<!-- END GENERATED: stage-list-construction -->

**Note**: Each unit is completed fully (design + code) before moving to the next unit.

---

## Per-Unit Loop (Executes for Each Unit)

**For each unit of work, execute the following stages in sequence:**

> **Per-unit reporting rule**: the engine emits each per-unit stage ONCE for the whole unit loop (one state slot per stage). Run the stage's gate per unit, but call `report` exactly once — after the LAST unit's gate outcome. Reporting `approved` after an early unit would mark the stage done and strand the remaining units.
### Functional Design (CONDITIONAL, per-unit)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/construction/functional-design.md` and execute for this unit. Standardized 2-option gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

### NFR Requirements (CONDITIONAL, per-unit)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/construction/nfr-requirements.md` and execute for this unit. Standardized 2-option gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

### NFR Design (CONDITIONAL, per-unit)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/construction/nfr-design.md` and execute for this unit. Standardized 2-option gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

### Infrastructure Design (CONDITIONAL, per-unit)

Applicability: per this stage's frontmatter criteria (CONDITIONAL Stage Criteria list, workflow-planning.md). Load `references/construction/infrastructure-design.md` and execute for this unit. Standardized 2-option gate — report `approved` / `rejected` / `revised`, or `skipped --reason` if not applicable (Orchestration Loop).

### Code Generation (ALWAYS EXECUTE, per-unit)

**Two parts within one stage**: Part 1 (planning — detailed code generation plan with checkboxes, user-approved), Part 2 (generation — execute the approved plan; application code goes to the workspace root, never `aidlc-docs/`). Load `references/construction/code-generation.md` and execute. Standardized 2-option gate — report `approved` / `rejected` / `revised` via the engine (Orchestration Loop).

---

## Build and Test (ALWAYS EXECUTE)

Load `references/construction/build-and-test.md` and generate comprehensive build/test instruction files for all units (full artifact list there). Approval gate — report `approved` / `rejected` / `revised` via the engine (Orchestration Loop).

---

# 🟡 OPERATIONS PHASE

**Purpose**: Placeholder for future deployment and monitoring workflows

**Focus**: How to DEPLOY and RUN it (future expansion)

**Stages in OPERATIONS PHASE**:
<!-- BEGIN GENERATED: stage-list-operations | do not hand-edit — regenerated by scripts/generate.py from stage frontmatter (see references/common/stage-contract.md) -->
- Operations (PLACEHOLDER)
<!-- END GENERATED: stage-list-operations -->

---

## Operations (PLACEHOLDER)

**Status**: This stage is currently a placeholder for future expansion. See `references/operations/operations.md`.

The Operations stage will eventually include:
- Deployment planning and execution
- Monitoring and observability setup
- Incident response procedures
- Maintenance and support workflows
- Production readiness checklists

**Current State**: All build and test activities are handled in the CONSTRUCTION phase.

**Engine behavior**: Operations is a CONDITIONAL placeholder that does not execute in practice. The model reports `skipped --reason` for it, after which the engine emits the `done` directive — the workflow ends after Build and Test. There is no further stage to navigate to manually.

## Key Principles

- **Adaptive Execution**: Only execute stages that add value
- **Transparent Planning**: Always show execution plan before starting
- **User Control**: User can request stage inclusion/exclusion
- **Progress Tracking (two-level checkboxes)**: Stage progress is engine-owned — the engine exclusively maintains the ENGINE-STATE region of `aidlc-state.md` (stage checkboxes, Current Status, State Digest) through `report`/`jump` (transitions) and `park` (annotations); the model MUST NOT hand-edit it. Plan-level checkboxes in `aidlc-docs/` plan files are model-owned — mark a step `[x]` in the SAME interaction where the work is completed; never leave completed work untracked.
- **State Ownership**: The model maintains only the model-owned regions of `aidlc-state.md` (Project Information, Workspace State, Code Location Rules, Extension Configuration, Autonomous Mode, Execution Plan Summary — incl. the Scope/Depth/Stages lines the engine reads for routing) per template. The full ownership matrix is in `references/common/engine-contract.md`. (Sole exception: the engine's AM-10 round-boundary expiry flip of the Autonomous Mode `Enabled` line — engine-contract.md §6.)
- **Complete Audit Trail**: Log ALL user inputs and AI responses in audit.md with timestamps — COMPLETE RAW INPUT, never summarized, every interaction (not just approvals). The full audit discipline (append-only, end-of-file anchoring, git-sourced fields, timestamp acquisition) is enforced by workflow-conventions Group 3 (AUD-01–05).
- **Quality Focus**: Complex changes get full treatment, simple changes stay efficient
- **Content Validation**: Always validate content before file creation per content-validation.md rules
- **NO EMERGENT BEHAVIOR**: Construction phases MUST use standardized 2-option completion messages as defined in their respective rule files. DO NOT create 3-option menus or other emergent navigation patterns.

## Audit Log Entry Format

Log every interaction (prompts, approval asks, user responses) using this entry shape. Timestamps are ISO 8601 (YYYY-MM-DDTHH:MM:SSZ); include stage context for each entry:

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Input**: "[Complete raw user input - never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

## Directory Structure

```text
<WORKSPACE-ROOT>/                   # ⚠️ APPLICATION CODE HERE
├── [project-specific structure]    # Varies by project (see references/construction/code-generation.md)
│
├── aidlc-docs/                     # 📄 DOCUMENTATION ONLY
│   ├── inception/                  # 🔵 INCEPTION PHASE
│   │   ├── plans/
│   │   ├── reverse-engineering/    # Brownfield only
│   │   ├── product-design/         # Product Brainstorm output
│   │   ├── requirements/
│   │   ├── user-stories/
│   │   └── application-design/
│   ├── construction/               # 🟢 CONSTRUCTION PHASE
│   │   ├── plans/
│   │   ├── {unit-name}/
│   │   │   ├── functional-design/
│   │   │   ├── nfr-requirements/
│   │   │   ├── nfr-design/
│   │   │   ├── infrastructure-design/
│   │   │   └── code/               # Markdown summaries only
│   │   └── build-and-test/
│   ├── operations/                 # 🟡 OPERATIONS PHASE (placeholder)
│   ├── aidlc-state.md
│   ├── audit.md
│   └── handoff.md                  # Engine-owned park notes
```

**CRITICAL RULE**:
- Application code: Workspace root (NEVER in aidlc-docs/)
- Documentation: aidlc-docs/ only
- Project structure: See `references/construction/code-generation.md` for patterns by project type
