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

**Workflow scopes**: During Requirements Analysis, a named scope (classic/bugfix/refactor/security-patch/infra/express) is selected and recorded in `aidlc-docs/aidlc-state.md`. Scope selection is **de-emphasized for end users**: when the match is unambiguous the scope is auto-selected without a gate; only genuine ambiguity triggers a chat question with minimal candidates (see `references/inception/requirements-analysis.md` Step 2.5). The scope pre-prunes conditional stages (see `references/common/stage-contract.md` §6). If the active scope marks a stage as SKIP, do NOT execute it or re-litigate its inclusion — the per-stage assessment in this file applies only to stages in the plan; the user may still add stages back explicitly at the Workflow Planning gate. If no scope is recorded (e.g. a session started before scopes existed), treat the plan as `classic`.

## MANDATORY: Rule Details Loading

**CRITICAL**: When performing any phase, you MUST read and use relevant content from the rule detail files located in the `references/` directory next to this SKILL.md.

All rule detail file references below (e.g., `references/common/process-overview.md`, `references/inception/workspace-detection.md`) are relative to this skill's directory.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `references/common/engine-contract.md` for runtime engine invocation, directives, transition semantics, state ownership, and integrity
- Load `references/common/process-overview.md` for workflow overview
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

**Interpret the status JSON** (the single JSON object on stdout):

| `state` / `integrity` | Action |
|---|---|
| `none` | New workflow: display the welcome message (next section) → run Workspace Detection → `engine.py init` creates `aidlc-state.md` deterministically |
| `active` | Resume the session per `references/common/session-continuity.md`; the status JSON is the sole source of truth for recovery |
| `completed` | The workflow is already complete; confirm with the user before starting anything new |
| `legacy` | A pre-engine state file exists (no `ENGINE-STATE` region): do NOT silently adopt or overwrite it — follow the legacy handling in `references/common/engine-contract.md` |
| any state, `integrity: violated` | The engine-owned region drifted: follow the integrity flow in `engine-contract.md` (present the drift, get explicit confirmation, `rebase`) |

The full runtime contract — invocation, directives, transition semantics, state ownership, integrity — is `references/common/engine-contract.md`.

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
   - **`done`**: the workflow is complete — present the closing summary and stop.
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
- Directive consumption rules (including "ignore unknown fields") are normative in `references/common/engine-contract.md`.

---

# INCEPTION PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in INCEPTION PHASE**:
<!-- BEGIN GENERATED: stage-list-inception | do not hand-edit — regenerated by scripts/generate.py from stage frontmatter (see references/common/stage-contract.md) -->
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (CONDITIONAL)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)
- Units Generation (CONDITIONAL)
<!-- END GENERATED: stage-list-inception -->

---

## Workspace Detection (ALWAYS EXECUTE)

1. **MANDATORY**: Log initial user request in audit.md with complete raw input
2. Load all steps from `references/inception/workspace-detection.md`
3. Execute workspace detection:
   - Confirm start/resume state from the engine status probe (see Engine Bootstrap)
   - Scan workspace for existing code
   - Determine if brownfield or greenfield
   - Check for existing reverse engineering artifacts
4. **MANDATORY**: Log findings in audit.md
5. Present completion message to user (see workspace-detection.md for message formats)
6. On completion, report via the engine (see Orchestration Loop): `completed` for this stage.

## Reverse Engineering (CONDITIONAL - Brownfield Only)

**Execute IF**:
- Existing codebase detected
- No previous reverse engineering artifacts found

**Skip IF**:
- Greenfield project
- Previous reverse engineering artifacts exist

**Execution**:
1. **MANDATORY**: Log start of reverse engineering in audit.md
2. Load all steps from `references/inception/reverse-engineering.md`
3. Execute reverse engineering:
   - Analyze all packages and components
   - Generate a business overview of the whole system covering the business transactions
   - Generate architecture documentation
   - Generate code structure documentation
   - Generate API documentation
   - Generate component inventory
   - Generate Interaction Diagrams depicting how business transactions are implemented across components
   - Generate technology stack documentation
   - Generate dependencies documentation

4. **Wait for Explicit Approval**: Present detailed completion message (see reverse-engineering.md for message format) - DO NOT PROCEED until user confirms
5. **MANDATORY**: Log user's response in audit.md with complete raw input
6. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes** but depth varies based on request clarity and complexity:
- **Minimal**: Simple, clear request - just document intent analysis
- **Standard**: Normal complexity - gather functional and non-functional requirements
- **Comprehensive**: Complex, high-risk - detailed requirements with traceability

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/inception/requirements-analysis.md`
3. Execute requirements analysis:
   - Load reverse engineering artifacts (if brownfield)
   - Analyze user request (intent analysis)
   - Determine requirements depth needed
   - Assess current requirements
   - Ask clarifying questions (if needed)
   - Generate requirements document
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Follow approval format from requirements-analysis.md detailed steps - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle.

## User Stories (CONDITIONAL)

**INTELLIGENT ASSESSMENT**: Use multi-factor analysis to determine if user stories add value:

**ALWAYS Execute IF** (High Priority Indicators):
- New user-facing features or functionality
- Changes affecting user workflows or interactions
- Multiple user types or personas involved
- Complex business requirements with acceptance criteria needs
- Cross-functional team collaboration required
- Customer-facing API or service changes
- New product capabilities or enhancements

**LIKELY Execute IF** (Medium Priority - Assess Complexity):
- Modifications to existing user-facing features
- Backend changes that indirectly affect user experience
- Integration work that impacts user workflows
- Performance improvements with user-visible benefits
- Security enhancements affecting user interactions
- Data model changes affecting user data or reports

**COMPLEXITY-BASED ASSESSMENT**: For medium priority cases, execute user stories if:
- Request involves multiple components or services
- Changes span multiple user touchpoints
- Business logic is complex or has multiple scenarios
- Requirements have ambiguity that stories could clarify
- Implementation affects multiple user journeys
- Change has significant business impact or risk

**SKIP ONLY IF** (Low Priority - Simple Cases):
- Pure internal refactoring with zero user impact
- Simple bug fixes with clear, isolated scope
- Infrastructure changes with no user-facing effects
- Technical debt cleanup with no functional changes
- Developer tooling or build process improvements
- Documentation-only updates

**ASSESSMENT CRITERIA**: When in doubt, favor inclusion of user stories for:
- Requests with business stakeholder involvement
- Changes requiring user acceptance testing
- Features with multiple implementation approaches
- Work that benefits from shared team understanding
- Projects where requirements clarity is valuable

**ASSESSMENT PROCESS**:
1. Analyze request complexity and scope
2. Identify user impact (direct or indirect)
3. Evaluate business context and stakeholder needs
4. Consider team collaboration benefits
5. Default to inclusion for borderline cases

**Note**: If Requirements Analysis executed, Stories can reference and build upon those requirements.

**User Stories has two parts within one stage**:
1. **Part 1 - Planning**: Create story plan with questions, collect answers, analyze for ambiguities, get approval
2. **Part 2 - Generation**: Execute approved plan to generate stories and personas

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/inception/user-stories.md`
3. **MANDATORY**: Perform intelligent assessment (Step 1 in user-stories.md) to validate user stories are needed
4. Load reverse engineering artifacts (if brownfield)
5. If Requirements exist, reference them when creating stories
6. Execute at appropriate depth (minimal/standard/comprehensive)
7. **PART 1 - Planning**: Create story plan with questions, wait for user answers, analyze for ambiguities, get approval
8. **PART 2 - Generation**: Execute approved plan to generate stories and personas
9. **Wait for Explicit Approval**: Follow approval format from user-stories.md detailed steps - DO NOT PROCEED until user confirms
10. **MANDATORY**: Log user's response in audit.md with complete raw input
11. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

## Workflow Planning (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/inception/workflow-planning.md`
3. **MANDATORY**: Load content validation rules from `references/common/content-validation.md`
4. Load all prior context:
   - Reverse engineering artifacts (if brownfield)
   - Intent analysis
   - Requirements (if executed)
   - User stories (if executed)
5. Execute workflow planning:
   - Determine which phases to execute
   - Determine depth level for each phase
   - Create multi-package change sequence (if brownfield)
   - Generate workflow visualization (VALIDATE Mermaid syntax before writing)
6. **MANDATORY**: Validate all content before file creation per content-validation.md rules
7. **Wait for Explicit Approval**: Present recommendations using language from workflow-planning.md Step 9, emphasizing user control to override recommendations - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input
9. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle.

## Application Design (CONDITIONAL)

**Execute IF**:
- New components or services needed
- Component methods and business rules need definition
- Service layer design required
- Component dependencies need clarification

**Skip IF**:
- Changes within existing component boundaries
- No new components or methods
- Pure implementation changes

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/inception/application-design.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see application-design.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

## Units Generation (CONDITIONAL)

**Execute IF**:
- System needs decomposition into multiple units of work
- Multiple services or modules required
- Complex system requiring structured breakdown

**Skip IF**:
- Single simple unit
- No decomposition needed
- Straightforward single-component implementation

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/inception/units-generation.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see units-generation.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

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

**Execute IF**:
- New data models or schemas
- Complex business logic
- Business rules need detailed design

**Skip IF**:
- Simple logic changes
- No new business logic

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `references/construction/functional-design.md`
3. Execute functional design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in functional-design.md - DO NOT use emergent 3-option behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

### NFR Requirements (CONDITIONAL, per-unit)

**Execute IF**:
- Performance requirements exist
- Security considerations needed
- Scalability concerns present
- Tech stack selection required

**Skip IF**:
- No NFR requirements
- Tech stack already determined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `references/construction/nfr-requirements.md`
3. Execute NFR assessment for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-requirements.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

### NFR Design (CONDITIONAL, per-unit)

**Execute IF**:
- NFR Requirements was executed
- NFR patterns need to be incorporated

**Skip IF**:
- No NFR requirements
- NFR Requirements was skipped

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `references/construction/nfr-design.md`
3. Execute NFR design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

### Infrastructure Design (CONDITIONAL, per-unit)

**Execute IF**:
- Infrastructure services need mapping
- Deployment architecture required
- Cloud resources need specification

**Skip IF**:
- No infrastructure changes
- Infrastructure already defined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `references/construction/infrastructure-design.md`
3. Execute infrastructure design for this unit
4. **MANDATORY**: Present standardized 2-option completion message as defined in infrastructure-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle. If this stage does not apply, report `skipped --reason` instead.

### Code Generation (ALWAYS EXECUTE, per-unit)

**Always executes for each unit**

**Code Generation has two parts within one stage**:
1. **Part 1 - Planning**: Create detailed code generation plan with explicit steps
2. **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `references/construction/code-generation.md`
3. **PART 1 - Planning**: Create code generation plan with checkboxes, get user approval
4. **PART 2 - Generation**: Execute approved plan to generate code for this unit
5. **MANDATORY**: Present standardized 2-option completion message as defined in code-generation.md - DO NOT use emergent behavior
6. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
7. **MANDATORY**: Log user's response in audit.md with complete raw input
8. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle.

---

## Build and Test (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `references/construction/build-and-test.md`
3. Generate comprehensive build and test instructions:
   - Build instructions for all units
   - Unit test execution instructions
   - Integration test instructions (test interactions between units)
   - Performance test instructions (if applicable)
   - Additional test instructions as needed (contract tests, security tests, e2e tests)
4. Create instruction files in the `build-and-test/` subdirectory (full artifact list: see `references/construction/build-and-test.md`)
5. **Wait for Explicit Approval**: Ask: "**Build and test instructions complete. Approve to record this stage?**" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. On completion, report via the engine (see Orchestration Loop): `approved` after user approval; `rejected` if changes are requested; `revised` after a revision cycle.

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
- **Progress Tracking**: Stage progress is engine-owned. The engine exclusively maintains the ENGINE-STATE region of `aidlc-state.md` (stage checkboxes, Current Status, State Digest) through `report`/`jump`. The model MUST NOT hand-edit that region.
- **State Ownership**: The model maintains only the model-owned regions of `aidlc-state.md` (Project Information, Workspace State, Code Location Rules, Extension Configuration, Autonomous Mode, Execution Plan Summary — incl. the Scope/Depth/Stages lines the engine reads for routing) per template. The full ownership matrix is in `references/common/engine-contract.md`.
- **Complete Audit Trail**: Log ALL user inputs and AI responses in audit.md with timestamps
  - **CRITICAL**: Capture user's COMPLETE RAW INPUT exactly as provided
  - **CRITICAL**: Never summarize or paraphrase user input in audit log
  - **CRITICAL**: Log every interaction, not just approvals
- **Quality Focus**: Complex changes get full treatment, simple changes stay efficient
- **Content Validation**: Always validate content before file creation per content-validation.md rules
- **NO EMERGENT BEHAVIOR**: Construction phases MUST use standardized 2-option completion messages as defined in their respective rule files. DO NOT create 3-option menus or other emergent navigation patterns.

## MANDATORY: Plan-Level Checkbox Enforcement

### MANDATORY RULES FOR PLAN EXECUTION
1. **NEVER complete any work without updating plan checkboxes**
2. **IMMEDIATELY after completing ANY step described in a plan file, mark that step [x]**
3. **This must happen in the SAME interaction where the work is completed**
4. **NO EXCEPTIONS**: Every plan step completion MUST be tracked with checkbox updates

### Two-Level Checkbox Tracking System
- **Plan-Level**: Track detailed execution progress within each stage. Plan files live in `aidlc-docs/` and remain model-owned — update their checkboxes immediately in the same interaction where the work is completed.
- **Stage-Level**: Overall workflow progress lives in the engine-owned region of `aidlc-state.md`. It is maintained exclusively by the engine through `report`/`jump` (see Orchestration Loop) — the model MUST NOT hand-edit it.
- **Update immediately**: All plan-level checkbox updates happen in the SAME interaction where the work is completed.

## Prompts Logging Requirements
- **MANDATORY**: Log EVERY user input (prompts, questions, responses) with timestamp in audit.md
- **MANDATORY**: Capture user's COMPLETE RAW INPUT exactly as provided (never summarize)
- **MANDATORY**: Log every approval prompt with timestamp before asking the user
- **MANDATORY**: Record every user response with timestamp after receiving it
- **CRITICAL**: ALWAYS append changes to EDIT audit.md file, NEVER use tools and commands that completely overwrite its contents
- **CRITICAL**: NEVER use file writing tools and commands that overwrite the entire contents of audit.md, as this causes duplication
- Use ISO 8601 format for timestamps (YYYY-MM-DDTHH:MM:SSZ)
- Include stage context for each entry

### Audit Log Format:
```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Input**: "[Complete raw user input - never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

### Correct Tool Usage for audit.md

✅ CORRECT:

1. Read the audit.md file
2. Append/Edit the file to make changes

❌ WRONG:

1. Read the audit.md file
2. Completely overwrite the audit.md with the contents of what you read, plus the new changes you want to add to it

## Directory Structure

```text
<WORKSPACE-ROOT>/                   # ⚠️ APPLICATION CODE HERE
├── [project-specific structure]    # Varies by project (see references/construction/code-generation.md)
│
├── aidlc-docs/                     # 📄 DOCUMENTATION ONLY
│   ├── inception/                  # 🔵 INCEPTION PHASE
│   │   ├── plans/
│   │   ├── reverse-engineering/    # Brownfield only
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
│   └── audit.md
```

**CRITICAL RULE**:
- Application code: Workspace root (NEVER in aidlc-docs/)
- Documentation: aidlc-docs/ only
- Project structure: See `references/construction/code-generation.md` for patterns by project type
