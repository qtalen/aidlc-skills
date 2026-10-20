---
slug: code-generation
phase: construction
execution: ALWAYS
condition: Always executes for each unit — generates code, tests, and artifacts through a two-part plan
gate: brief
produces:
  - construction/plans/{unit-name}-code-generation-plan.md
  - construction/{unit-name}/code/*
consumes:
  - artifact: inception/application-design/unit-of-work.md
    required: true
  - artifact: construction/{unit-name}/functional-design/*
    required: true
  - artifact: construction/{unit-name}/nfr-design/*
    required: true
  - artifact: construction/{unit-name}/infrastructure-design/*
    required: true
requires_stage:
  - functional-design
  - infrastructure-design
  - nfr-design
  - units-generation
for_each: unit-of-work
workspace_writes: true
scopes:
  classic: EXECUTE
  bugfix: EXECUTE
  refactor: EXECUTE
  security-patch: EXECUTE
  infra: EXECUTE
  express: EXECUTE
---

# Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work through two integrated parts:
- **Part 1 - Planning**: Create detailed code generation plan with explicit steps
- **Part 2 - Generation**: Execute the plan to generate code, tests, and artifacts

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

## Prerequisites
- Unit Design Generation must be complete for the unit, **or** the execution plan has no Units Generation stage — in that case this stage runs exactly once for the whole task as an implicit single unit (see `workflow-planning.md` Step 3.0), using `aidlc-docs/inception/requirements/requirements.md` and (brownfield) `aidlc-docs/inception/reverse-engineering/` artifacts as its inputs in place of unit artifacts
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for code generation

**Direction Stop (once per round — the standing direction gate, B18; formerly Code-Gen Hold / AM-11)**: before starting the FIRST unit's work this round (judge from this session's context and the plan file whether the stop was already presented this round; when uncertain, re-present — the safe direction), present the direction brief and WAIT for the user's go-ahead — an approve-and-continue style interaction — APG-01's intent classification applies to the user's reply, but APG-02~04's engine-transition recording does NOT (the stage is not completing here: no `report` runs at the stop; hold/continue only gates whether stage work begins). The brief is ≤10 lines: unit count and order (from Units Generation), the design-stage key decisions so far (the current unit's designs and any workflow-level choices), notable risks, and any drift relative to Requirements Analysis. This is also the natural model-switch window (e.g. to a faster model for the implementation stages). Saying "continue" (or equivalent semantics, any language) releases the stop and the stage proceeds under brief-gate rules; a change request goes through the normal change flow, after which the stop KEEPS WAITING until continue-semantics. The stop occurs at most once per round: subsequent units and a backward redo into this stage do NOT re-present it (the user can always request an ad-hoc stop conversationally). A session resuming with no unit of this stage completed this round re-presents the stop before continuing.

---

# PART 1: PLANNING

## Step 1: Analyze Unit Context
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Validate unit is ready for code generation

## Step 2: Create Detailed Unit Code Generation Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never aidlc-docs/)
- [ ] Create explicit steps for unit generation:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Unit Testing
  - Business Logic Summary
  - API Layer Generation
  - API Layer Unit Testing
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Unit Testing
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Unit Testing (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts
  - Database entities owned by this unit
  - Service boundaries and responsibilities

## Step 4: Create Unit Plan Document
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story traceability
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the unit code generation plan to the user
- [ ] Highlight unit generation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log Plan Presentation
- [ ] Log the unit-plan presentation (Step 5 summary) with timestamp in `aidlc-docs/audit.md`
- [ ] Use ISO 8601 timestamp format

## Step 7: Proceed (no per-unit plan approval — brief-gate posture, B18)
- [ ] The unit plan summary is informational — do NOT wait for approval; the round-level Direction Stop (top of this file) is the only standing stop in this stage
- [ ] If the user objects to a unit plan in natural language, update the plan and proceed (the objection channel replaces the former approval wait)

## Step 8: Record Interaction
- [ ] Log the interaction outcome with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text when one exists; mark the outcome clearly (briefed / objection handled)

## Step 9: Update Progress
- [ ] Track Part 1 (Planning) progress in the plan file — the Stage Progress / Current Status sections of `aidlc-state.md` are engine-owned; never hand-edit them
- [ ] Prepare for transition to Code Generation

---

# PART 2: GENERATION

## Step 10: Load Unit Code Generation Plan
- [ ] Read the complete plan from `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (unit, dependencies, stories)

## Step 11: Execute Current Step
- [ ] Verify target directory from plan (never aidlc-docs/)
- [ ] **Brownfield only**: Check if target file exists
- [ ] Generate exactly what the current step describes:
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: Workspace root per project structure
  - **Documentation**: `aidlc-docs/construction/{unit-name}/code/` (markdown only)
  - **Build/Config Files**: Workspace root
- [ ] Follow unit story requirements
- [ ] Respect dependencies and interfaces

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the unit code generation plan
- [ ] Mark associated unit stories as [x] when their generation is finished
- [ ] Do not hand-edit `aidlc-docs/aidlc-state.md` — its progress sections are engine-owned
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Continue or Complete Generation
- [ ] If more steps remain, return to Step 10
- [ ] If all steps complete, proceed to present completion message

## Step 14: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete (all units)
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📡 <u>**COMPLETION BRIEF:**</u>**  
> Code generation complete for all units — code at: `[actual-workspace-path]` · docs at: `aidlc-docs/construction/[unit-name]/code/`
> Key decisions: [1-2] · Notable risks: [or "none"]
> Brief-gate posture: proceeding without approval — object anytime in natural language.

---
```

## Step 15: Record and Proceed (briefing gate)
- This stage is `gate: brief` (B18): the completion brief requests no approval — present it and proceed in the SAME interaction
- **Objection channel**: the user may object in natural language at any time — handle per the change flow (`references/common/workflow-changes.md`)

## Step 16: Update Progress
- In the SAME interaction as the brief, run `python <skill>/scripts/engine.py report --stage code-generation --result completed` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-state.md` — they are engine-owned.
- **Per-unit note**: this stage is emitted once by the engine for the whole unit loop. Do the generation work per unit (informative progress messages are fine), but present the completion brief ONCE and call `report` exactly once — after the LAST unit completes; fold per-unit highlights in (notable deviations only, not a recital).

---

## Critical Rules

### Code Location Rules
- **Application code**: Workspace root only (NEVER aidlc-docs/)
- **Documentation**: aidlc-docs/ only (markdown summaries)
- **Read workspace root** from aidlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `lib/`, `pkg/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- Document unit context and dependencies
- Present the unit plan summary and proceed — the round-level Direction Stop (top of this file) is the one standing stop

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark unit stories [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit code generation plan created
- All steps in unit code generation plan marked [x]
- All unit stories implemented according to plan
- All code and tests generated (tests will be executed in Build & Test phase)
- Deployment artifacts generated
- Complete unit ready for build and verification
