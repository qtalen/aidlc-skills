# Mid-Workflow Changes and Stage Management

## Overview

Users may request changes to the execution plan or stage execution during the workflow. This document provides guidance on handling these requests safely and effectively.

**Convergence rule — judgment in conventions, execution in the engine**: which change type applies, its dependency impact, and whether a change is safe remain **model judgment** per the protocols below. Every *execution* of a change — moving the pointer, redoing or skipping a stage, reordering, re-basing the plan — runs through the runtime engine (`scripts/engine.py`; prefer `python`, fall back to `python3`). Never hand-edit the engine-owned region of `aidlc-state.md` or move the stage pointer manually.

---

## Types of Mid-Workflow Changes

### 1. Adding a Skipped Stage

**Scenario**: User wants to add a stage that was originally skipped

**Example**: "Actually, I want to add user stories even though we skipped that stage"

**Handling**:
1. **Confirm Request**: "You want to add User Stories stage. This will create user stories and personas. Confirm?"
2. **Check Dependencies**: Verify all prerequisite stages are complete
3. **Update Execution Plan Summary**: under `## Execution Plan Summary` in `aidlc-state.md` (model-owned region):
   - If the slug is listed on `Stages to Skip`, **remove it from that line first** — Skip wins over Execute, so an Execute entry alone cannot bring it back
   - Add the stage **slug** to `- **Stages to Execute**: slug1, slug2`
4. **Let the engine re-route**: run `engine.py next`. The engine recomputes the route from the plan lines on every call, so the added-back stage is emitted as soon as it is the earliest pending stage (if it precedes the current pointer, it becomes current immediately — that is expected). Do **not** use `jump` for an add-back: jumping to a stage that has just become current is rejected (`invalid-jump`), and a forward jump would mark uncompleted intermediates `[S]`. Never hand-edit stage checkboxes or move the pointer manually.
5. **Log Change**: Document in `audit.md` with timestamp and reason (the engine also appends its own transition entry)

**Considerations**:
- May need to update later stages that could benefit from new artifacts
- Existing artifacts may need revision to incorporate new information
- Timeline will be extended

---

### 2. Skipping a Planned Stage

**Scenario**: User wants to skip a stage that was planned to execute

**Example**: "Let's skip the NFR Design stage for now"

**Handling**:
1. **Confirm Request**: "You want to skip NFR Design. This means no NFR patterns or logical components will be incorporated. Confirm?"
2. **Warn About Impact**: Explain what will be missing and potential consequences
3. **Get Explicit Confirmation**: User must explicitly confirm understanding of impact
4. **Execute the change through the engine — order matters** (never hand-edit stage checkboxes or move the pointer manually):
   - **Current stage, CONDITIONAL**: record the formal skip **first** with `engine.py report --stage <slug> --result skipped --reason "<reason>"`, **then** persist the decision as `- **Stages to Skip**: slug (reason)` under `## Execution Plan Summary` (writing the Skip line first re-routes the pointer past the stage, and the report is then rejected as `invalid-transition`)
   - **Any other planned stage** (a future stage, or a current non-CONDITIONAL stage): write the Skip line first, then run `engine.py next` — the engine re-routes and simply never emits the stage. Do **not** use `jump` to "route past" it: a forward jump marks every uncompleted intermediate stage `[S]`, including the in-flight current stage
5. **Adjust Later Stages**: Note that later stages may need manual setup
6. **Log Change**: Document in `audit.md` with timestamp and reason

**Considerations**:
- Later stages may fail or require manual intervention
- User accepts responsibility for missing artifacts
- Can be added back later if needed

---

### 3. Restarting Current Stage

**Scenario**: User is unhappy with current stage results and wants to redo it

**Example**: "I don't like these user stories. Can we start over?"

**Handling**:
1. **Understand Concern**: "What specifically would you like to change about the stories?"
2. **Offer Options**:
   - **Option A**: Modify existing artifacts (faster, preserves some work)
   - **Option B**: Complete restart (clean slate, more time)
3. **If Restart Chosen**:
   - Archive existing artifacts: `{artifact}.backup.{timestamp}`
   - Execute the restart through the engine: `engine.py jump --stage <slug>` (a redo resets the target stage and everything after it)
   - Re-execute from beginning
4. **Log Change**: Document reason for restart and what will change

**Considerations**:
- Existing work will be lost (but backed up)
- May need to redo dependent stages
- Timeline will be extended

---

### 4. Restarting Previous Stage

**Scenario**: User wants to go back and redo a completed stage

**Example**: "I want to change the architectural decision we made earlier"

**Handling**:
1. **Assess Impact**: Identify all stages that depend on the stage to be restarted
2. **Warn User**: "Restarting Application Design will require redoing: Units Generation, per-unit design (all units), Code Generation. Confirm?"
3. **Get Explicit Confirmation**: User must understand full impact
4. **If Confirmed**:
   - Archive all affected artifacts
   - Execute the redo through the engine: `engine.py jump --stage <slug>` — this resets the target stage and every stage after it; never hand-edit state checkboxes or move the pointer manually
   - Re-execute from that point forward
5. **Log Change**: Document full impact and reason for restart

**Considerations**:
- Significant rework required
- All dependent stages must be redone
- Timeline will be significantly extended
- Consider if modification is better than restart

---

### 5. Changing Stage Depth

**Scenario**: User wants to change the depth level of current or upcoming stage

**Example**: "Let's do a comprehensive requirements analysis instead of standard"

**Handling**:
1. **Confirm Request**: "You want to change Requirements Analysis from Standard to Comprehensive depth. This will be more thorough but take longer. Confirm?"
2. **Update Execution Plan**: Change depth level in `aidlc-docs/inception/plans/execution-plan.md` and update the `- **Depth**:` line under `## Execution Plan Summary` in `aidlc-state.md` (a model-owned, engine-read line — the engine consumes ONLY the Execution Plan Summary copies for routing)
3. **Adjust Approach**: Follow comprehensive depth guidelines for the stage
4. **Update Estimates**: Inform user of new timeline estimate
5. **Log Change**: Document depth change and reason

**Considerations**:
- More depth = more time but better quality
- Less depth = faster but may miss details
- Can only change before or during stage, not after completion

---

### 6. Pausing Workflow

**Scenario**: User needs to pause and resume later

**Example**: "I need to stop for now and continue tomorrow"

**Handling**:
1. **Complete Current Step**: Finish the current step in progress if possible
2. **Park In-Flight Work**: If pausing mid-stage, run `engine.py park --note "<in-flight X; next step Y; caveat Z>"` so the next session gets a precise breakpoint (see session-continuity.md Park Ritual)
3. **Record the Transition**: If a stage finished, write it through the engine (`engine.py report --stage <slug> --result completed|approved`); never hand-edit stage checkboxes
4. **No Manual State Edits**: `aidlc-state.md` is already current — the engine wrote every transition as it happened
5. **Log Pause**: Document pause point in `audit.md`
6. **Provide Resume Instructions**: "When you return, I'll detect your existing project and offer to continue from: [current stage, current step]"

**On Resume**:
1. **Detect Existing Project**: Run `engine.py status` (the recovery data source — includes `resume_note`, `recent_events`, `artifact_alerts`)
2. **Load Context**: Follow the tiered reading protocol in [session-continuity.md](session-continuity.md) — engine output first, then only the current stage's required consumes; do NOT bulk-load all artifacts from completed stages
3. **Show Status**: Display current stage and next step from the status JSON
4. **Offer Options**: Continue (`next`), jump to another stage (`jump --stage`), or Start Fresh (`jump --fresh`)
5. **Log Resume**: Document resume point in `audit.md`

---

### 7. Changing Architectural Decision

**Scenario**: User wants to change from monolith to microservices (or vice versa)

**Example**: "Actually, let's do microservices instead of a monolith"

**Handling**:
1. **Assess Current Progress**: Determine how far into workflow
2. **Explain Impact**: 
   - If before Units Generation: Minimal impact, just update decision
   - If after Units Generation: Must redo Units Generation, all per-unit design
   - If after Code Generation: Significant rework required
3. **Recommend Approach**:
   - Early in workflow: Restart from Application Design stage
   - Late in workflow: Consider if modification is feasible vs. restart
4. **Get Confirmation**: User must understand full scope of change
5. **Execute Change**: Follow restart procedures for affected stages

**Considerations**:
- Architectural changes have cascading effects
- Earlier in workflow = easier to change
- Later in workflow = consider cost vs. benefit

---

### 8. Adding/Removing Units

**Scenario**: User wants to add or remove units after Units Generation

**Example**: "We need to split the Payment unit into Payment and Billing"

**Handling**:
1. **Assess Impact**: Determine which units have completed design/code
2. **Explain Consequences**:
   - Adding unit: Need to do full design and code for new unit
   - Removing unit: Need to redistribute functionality to other units
   - Splitting unit: Need to redo design and code for both resulting units
3. **Update Unit Artifacts**:
   - Modify `unit-of-work.md`
   - Update `unit-of-work-dependency.md`
   - Revise `unit-of-work-story-map.md`
4. **Reset Affected Units**: Mark affected units as needing redesign
5. **Execute Changes**: Follow normal unit design and code process for affected units

**Considerations**:
- Affects all downstream stages for those units
- May affect other units if dependencies change
- Timeline impact depends on how many units affected

---

### 9. Changing Workflow Scope

**Scenario**: User wants to switch to a different scope, re-basing the plan for the remaining stages

**Example**: "This turned out to be a small bug fix - switch us to the bugfix scope"

**Handling**:
1. **Confirm Request**: "You want to change the workflow scope from classic to bugfix. This re-bases the EXECUTE/SKIP/CONDITIONAL plan for remaining stages and updates the default depth. Completed stages are unaffected. Confirm?"
2. **Update State**: Set `- **Scope**: ...` (and the resulting default `- **Depth**: ...`) under `## Execution Plan Summary` in `aidlc-state.md` (the model-owned, engine-read lines — the engine consumes ONLY the Execution Plan Summary copies for routing; a copy under `## Project Information` is informational only)
3. **Re-base Remaining Stages**: Rewrite the model-owned `## Execution Plan Summary` lines — `- **Stages to Execute**: slug1, slug2` and `- **Stages to Skip**: slug (reason)` — for the stages that have not yet executed (the engine consumes these overrides on `next`)
4. **Preserve Completed Work**: Leave already-executed stages and their artifacts untouched
5. **Log Change**: Document the scope change and reason in `audit.md`

**Considerations**:
- Only remaining stages are re-based; completed stages are never rolled back
- Previously skipped stages stay skippable unless the new scope marks them EXECUTE or CONDITIONAL
- The new scope's depth becomes the workflow default but can still be overridden per stage
- A narrower scope may drop artifacts that later stages depend on; warn before confirming

---

### 10. Scope Reduction / Requirement Invalidation

**Scenario**: User moves a requirement out of scope mid-workflow (dropping a requirement), or an upstream artifact is invalidated so that completed work no longer matches the approved scope

**Example**: "Drop the TABLE mode from this iteration" / "把 TABLE 模式移出本迭代" — the related FRs are already analyzed, stories are written, and the plan checklist steps are checked off

**Handling**:
1. **Classify the request** as a change request. If it arrives at an approval gate, approval-gate classification (APG-01 in workflow-conventions) handles it as Request Changes.
2. **Run the impact analysis** and enumerate, item by item: affected functional requirements (`requirements.md`), affected stories (`stories.md`), affected design artifacts (business rules, domain entities, logic models, component methods, ...), and affected plan checklist steps across stage plan files.
3. **Record the gate outcome honestly**: if the current stage's output is what the user is rejecting (its approval gate is pending), record it through the engine first — `python <skill>/scripts/engine.py report --stage <slug> --result rejected --reason "scope reduction: <what was dropped>"` (fall back to `python3`). Never hand-edit stage checkboxes. If no gate outcome is pending, skip this step — the jump in the next step records the course change itself.
4. **Jump to the most upstream affected stage** — unless it IS the current stage: `python <skill>/scripts/engine.py jump --stage <slug>` resets that stage and every stage after it; then run `engine.py next` and re-execute the affected stages in order, each with its normal approval gate. **When the most upstream affected stage is the current stage, skip the jump** — the engine rejects jumping to the current stage (`invalid-jump`); instead revise this stage's artifacts in place (step 5) and re-walk its own gate (re-present the revised output, then record the cycle with `report --result revised`, or `--result approved` when the user approves).
5. **Revise artifacts in place (redo channel) — the protection boundary** ([DOC-04](../extensions/workflow/workflow-conventions/workflow-conventions.md)): split what may be rewritten from what may not:
   - **Protected (append-only, DOC-04)**: question-and-answer files (`[Answer]:` history), clarification/decision prose inside plan files, and `audit.md` entries. NEVER rewrite them; record corrections as appended, timestamped revision notes that map old → new (e.g. "FR-30~34 moved out of scope, numbers preserved").
   - **Current-state (update in place)**: plan checklist steps and the current-state artifacts themselves — `requirements.md` FR sections, `stories.md`, design artifacts, and the model-owned plan lines in `aidlc-state.md` (`## Execution Plan Summary`). Where the artifact format has a revision-record block, append the revision note there and then edit the content in place. Checkpoint content made stale is swept in the same interaction (DOC-01 / CTX-01).
6. **Preserve Deferred / Reserved numbers — never recycle them**: requirement and story identifiers moved out of scope keep their numbers, marked `Deferred` in `requirements.md` and `stories.md` (and noted in their revision records), so existing artifacts and audit entries stay traceable to stable identifiers.
7. **Log**: append a Change Request entry per the Logging Requirements format at the bottom of this file (the engine additionally appends its own transition entries automatically).

**Considerations**:
- Deferred items are candidates for later iterations; their numbers are reserved for traceability continuity.
- The full history of the reduction lives in `audit.md` + appended revision notes; in-place edits must never erase it.
- Timeline shrinks for this iteration but later iterations re-inherit the deferred backlog.
- All stages reset by the jump re-run their gates — treat re-approvals as normal, not as rubber stamps.

---

## General Guidelines for Handling Changes

### Before Making Changes

1. **Understand the Request**: Ask clarifying questions about what user wants to change and why
2. **Assess Impact**: Identify all affected stages, artifacts, and dependencies
3. **Explain Consequences**: Clearly communicate what will need to be redone and timeline impact
4. **Offer Alternatives**: Sometimes modification is better than restart
5. **Get Explicit Confirmation**: User must understand and accept the impact

### During Changes

1. **Archive Existing Work**: Always backup before making destructive changes
2. **Execute Through the Engine**: All stage/pointer changes go through `engine.py` (`report`, `jump`); never hand-edit the engine-owned state region or stage checkboxes
3. **Communicate Progress**: Keep user informed about what's happening
4. **Validate Changes**: Ensure changes are consistent across all artifacts
5. **Test Continuity**: Verify workflow can continue smoothly after changes

### After Changes

1. **Verify Consistency**: Check that all artifacts are aligned with changes
2. **Update Documentation**: Ensure all references are updated
3. **Log Completely**: Document full change history in `audit.md`
4. **Confirm with User**: Verify changes meet user's expectations
5. **Resume Workflow**: Continue with normal execution from new state

---

## Change Request Decision Tree

```
User requests change
    |
    ├─ Is it current stage?
    |   ├─ Yes: Can modify or restart current stage
    |   └─ No: Go to next question
    |
    ├─ Is it a completed stage?
    |   ├─ Yes: Assess impact on dependent stages
    |   |   ├─ Low impact: Modify and update dependents
    |   |   └─ High impact: Recommend restart from that stage
    |   └─ No: Go to next question
    |
    ├─ Is it adding a skipped stage?
    |   ├─ Yes: Check prerequisites, remove from Stages to Skip (if listed),
    |   |        add to Stages to Execute, run engine.py next
    |   └─ No: Go to next question
    |
    ├─ Is it skipping a planned stage?
    |   ├─ Yes: Warn, get confirmation, then either report skipped first
    |   |        (current CONDITIONAL stage) or write Stages to Skip + next
    |   └─ No: Go to next question
    |
    ├─ Is it dropping a requirement (scope reduction / invalidation)?
    |   ├─ Yes: impact analysis, report rejected if the current gate is
    |   |        affected, then jump to the most upstream affected stage
    |   |        (if that IS the current stage, skip the jump: revise in
    |   |        place and re-walk this stage's gate),
    |   |        revise current-state artifacts in place (DOC-04 history
    |   |        stays append-only), keep Deferred numbers reserved,
    |   |        re-walk the affected stages
    |   └─ No: Go to next question
    |
    └─ Is it changing depth level?
        ├─ Yes: Update plan, adjust approach
        └─ No: Clarify request with user
```

---

## Logging Requirements

### Change Request Log Format

```markdown
## Change Request - [Stage Name]
**Timestamp**: [ISO timestamp]
**Request**: [What user wants to change]
**Current State**: [Where we are in workflow]
**Impact Assessment**: [What will be affected]
**User Confirmation**: [User's explicit confirmation]
**Action Taken**: [What was done]
**Artifacts Affected**: [List of files changed/reset]

---
```

---

## Best Practices

1. **Always Confirm**: Never make destructive changes without explicit user confirmation
2. **Explain Impact**: Users need to understand consequences before deciding
3. **Offer Options**: Sometimes there are multiple ways to handle a change
4. **Archive First**: Always backup before making destructive changes
5. **Update Everything Through the Engine**: State transitions go through `engine.py`; model-owned plan lines are updated directly — never hand-edit the engine-owned region
6. **Log Thoroughly**: Document all changes for audit trail
7. **Validate After**: Ensure workflow can continue smoothly
8. **Be Flexible**: Workflow should adapt to user needs, not force rigid process
