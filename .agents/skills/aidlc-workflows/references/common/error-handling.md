# Error Handling and Recovery Procedures

## General Error Handling Principles

### When Errors Occur
1. **Identify the error**: Clearly state what went wrong
2. **Assess impact**: Determine if the error is blocking or can be worked around
3. **Communicate**: Inform the user about the error and options
4. **Offer solutions**: Provide clear steps to resolve or work around the error
5. **Document**: Log the error and resolution in `audit.md`

### Error Severity Levels

**Critical**: Workflow cannot continue
- Missing required files or artifacts
- Invalid user input that cannot be processed
- System errors preventing file operations

**High**: Stage cannot complete as planned
- Incomplete answers to required questions
- Contradictory user responses
- Missing dependencies from prior stages

**Medium**: Stage can continue with workarounds
- Optional artifacts missing
- Non-critical validation failures
- Partial completion possible

**Low**: Minor issues that don't block progress
- Formatting inconsistencies
- Optional information missing
- Non-blocking warnings

## Stage-Specific Error Handling

### Workspace Detection Errors

**Error**: Cannot read workspace files
- **Cause**: Permission issues, missing directories
- **Solution**: Ask user to verify workspace path and permissions
- **Workaround**: Proceed with user-provided information only

**Error**: Existing `aidlc-state.md` is corrupted
- **Cause**: Manual editing, incomplete previous run
- **Solution**: Detect the problem with `python <skill>/scripts/engine.py status` (fall back to `python3`). If `integrity` is `violated` (State Digest drift), HALT and present the drift facts with the last recorded audit transition entry. Ask the user whether to re-baseline (after confirmation, `engine.py rebase`) or start fresh (`engine.py jump --fresh`).
- **Recovery**: Never hand-edit the engine-owned state region; all recovery goes through the engine

**Error**: Cannot determine required stages
- **Cause**: Insufficient information from user
- **Solution**: Ask clarifying questions about intent and scope
- **Workaround**: Default to comprehensive execution plan

### Requirements Analysis Errors

**Error**: User provides contradictory requirements
- **Cause**: Unclear understanding, changing needs
- **Solution**: Create follow-up questions to resolve contradictions
- **Do Not Proceed**: Until contradictions are resolved

**Error**: Requirements document cannot be converted
- **Cause**: Unsupported format, corrupted file
- **Solution**: Ask user to provide requirements in supported format
- **Workaround**: Work with user's verbal description

**Error**: Incomplete answers to verification questions
- **Cause**: User skipped questions, unclear what to answer
- **Solution**: Highlight unanswered questions, provide examples
- **Do Not Proceed**: Until all required questions are answered

### User Stories Errors

**Error**: Cannot map requirements to stories
- **Cause**: Requirements too vague, missing functional details
- **Solution**: Return to Requirements Analysis for clarification
- **Workaround**: Create stories based on available information, mark as incomplete

**Error**: User provides ambiguous story planning answers
- **Cause**: Unclear options, complex decision
- **Solution**: Add follow-up questions with specific examples
- **Do Not Proceed**: Until ambiguities are resolved

**Error**: Story generation plan has uncompleted steps
- **Cause**: Execution interrupted, steps skipped
- **Solution**: Resume from first uncompleted step
- **Recovery**: Review completed steps, continue from checkpoint

### Application Design Errors

**Error**: Architectural decision is unclear or contradictory
- **Cause**: Ambiguous answers, conflicting requirements
- **Solution**: Add follow-up questions to clarify decision
- **Do Not Proceed**: Until decision is clear and documented

**Error**: Cannot determine number of services/units
- **Cause**: Insufficient information about boundaries
- **Solution**: Ask specific questions about deployment, team structure, scaling
- **Workaround**: Default to monolith, allow change later

### Design Errors

**Error**: Unit dependencies are circular
- **Cause**: Poor boundary definition, tight coupling
- **Solution**: Identify circular dependencies, suggest refactoring
- **Recovery**: Revise unit boundaries to break cycles

**Error**: Unit design plan has missing steps
- **Cause**: Plan generation incomplete, template error
- **Solution**: Regenerate plan with all required steps
- **Recovery**: Add missing steps to existing plan

**Error**: Cannot generate design artifacts
- **Cause**: Missing unit information, unclear requirements
- **Solution**: Return to Units Generation to clarify unit definition
- **Workaround**: Generate partial design, mark gaps

### NFR Implementation Errors

**Error**: Technology stack choices are incompatible
- **Cause**: Conflicting requirements, platform limitations
- **Solution**: Highlight incompatibilities, ask user to choose
- **Do Not Proceed**: Until compatible choices are made

**Error**: Organizational constraints cannot be met
- **Cause**: Network restrictions, security policies
- **Solution**: Document constraints, ask user for workarounds
- **Escalation**: May require human intervention for setup

**Error**: NFR implementation step requires human action
- **Cause**: AI cannot perform certain tasks (network config, credentials)
- **Solution**: Clearly mark as **HUMAN TASK**, provide instructions
- **Wait**: For user confirmation before proceeding

### Code Generation Planning Errors

**Error**: Code generation plan is incomplete
- **Cause**: Missing design artifacts, unclear requirements
- **Solution**: Return to Design stage to complete artifacts
- **Recovery**: Generate plan with available information, mark gaps

**Error**: Unit dependencies not satisfied
- **Cause**: Dependent units not yet generated
- **Solution**: Reorder generation sequence to respect dependencies
- **Workaround**: Generate with stub dependencies, integrate later

### Code Generation Errors (Part 2: Code Generation)

**Error**: Cannot generate code for a step
- **Cause**: Insufficient design information, unclear requirements
- **Solution**: Skip step, document as incomplete, continue
- **Recovery**: Return to step after gathering more information

**Error**: Generated code has syntax errors
- **Cause**: Template issues, language-specific problems
- **Solution**: Fix syntax errors, regenerate if needed
- **Validation**: Verify code compiles before proceeding

**Error**: Test generation fails
- **Cause**: Complex logic, missing test framework setup
- **Solution**: Generate basic test structure, mark for manual completion
- **Workaround**: Proceed without tests, add in Operations phase

### Operations Errors

**Error**: Cannot determine build tool
- **Cause**: Unusual project structure, multiple build systems
- **Solution**: Ask user to specify build tool and commands
- **Workaround**: Provide generic instructions, user adapts

**Error**: Deployment target is unclear
- **Cause**: Multiple environments, complex infrastructure
- **Solution**: Ask user to specify deployment targets and methods
- **Workaround**: Provide instructions for common platforms

## Recovery Procedures

### Partial Stage Completion

**Scenario**: Stage was interrupted mid-execution

**Recovery Steps**:
1. Load the stage plan file
2. Identify last completed step (last [x] checkbox)
3. Resume from next uncompleted step
4. Verify all prior steps are actually complete
5. Continue execution normally

### State File Corruption / Integrity Violation

**Scenario**: `aidlc-state.md` is corrupted, inconsistent, or its engine-owned region drifted from the State Digest

**Recovery Steps**:
1. Probe the state with `python <skill>/scripts/engine.py status` (fall back to `python3`). The status JSON reports `integrity` and the recorded transitions.
2. If `integrity` is `violated`: HALT. Present the drift facts and the last recorded audit transition entry to the user — do NOT proceed with normal work.
3. After explicit human confirmation, re-baseline with `python <skill>/scripts/engine.py rebase` (the engine recomputes the digest and appends a `STATE_REBASELINED` audit entry).
4. If the user instead wants to abandon the current state, start fresh with `engine.py jump --fresh`.
5. Resume via `engine.py status` + `engine.py next`.

**Hard rule**: the model MUST NOT edit the `<!-- BEGIN ENGINE-STATE -->` / `<!-- END ENGINE-STATE -->` region as any part of recovery — that region is engine-owned and is never a manual repair surface.

### Missing Artifacts

**Scenario**: Required artifacts from prior stage are missing

**Recovery Steps**:
1. Identify which artifacts are missing
2. Determine if they can be regenerated
3. If yes: Return to that stage, regenerate artifacts
4. If no: Ask user to provide information manually
5. Document the gap in `audit.md`

### User Wants to Restart Stage

**Scenario**: User is unhappy with stage results and wants to redo

**Recovery Steps**:
1. Confirm user wants to restart (data will be lost)
2. Archive existing artifacts: `{artifact}.backup`
3. Execute the restart through the engine: `python <skill>/scripts/engine.py jump --stage <slug>` (a redo resets the target stage and every stage after it; never hand-edit the stage status)
4. Clear stage checkboxes in plan files
5. Re-execute stage from beginning

### User Wants to Skip Stage

**Scenario**: User wants to skip a stage that was planned

**Recovery Steps**:
1. Confirm user understands implications
2. Document skip reason in `audit.md`
3. Record the skip through the engine — **order matters** (never hand-edit the stage checkboxes):
   - If the stage is the current stage and CONDITIONAL: `python <skill>/scripts/engine.py report --stage <slug> --result skipped --reason "<reason>"` **first**, then record it on the `Stages to Skip` line (a Skip line written first re-routes the pointer past the stage and the report is rejected)
   - Otherwise: record `- **Stages to Skip**: slug (reason)` in Execution Plan Summary, then run `engine.py next` (the engine never emits the stage). Never `jump` to "route past" it — a forward jump marks the in-flight current stage `[S]`
4. Proceed to next stage
5. Note: May cause issues in later stages if dependencies missing

## Escalation Guidelines

### When to Ask for User Help

**Immediately**:
- Contradictory or ambiguous user input
- Missing required information
- Technical constraints AI cannot resolve
- Decisions requiring business judgment

**After Attempting Resolution**:
- Repeated errors in same step
- Complex technical issues
- Unusual project structures
- Integration with external systems

### When to Suggest Starting Over

**Consider Fresh Start If**:
- Multiple stages have errors
- State file is severely corrupted
- User requirements have changed significantly
- Architectural decision needs to be reversed
- User cannot provide missing information
- Artifacts are inconsistent across phases

**Before Starting Over**:
1. Archive all existing work
2. Document lessons learned
3. Identify what to preserve
4. Get user confirmation
5. Create new execution plan
6. Reset through the engine: `python <skill>/scripts/engine.py jump --fresh` (archives `aidlc-docs/` and resets state) — never rebuild the state file by hand

## Session Resumption Errors

### Missing Artifacts During Resumption

**Error**: Required artifacts from previous stages are missing
- **Cause**: Files deleted, moved, or never created
- **Solution**: 
  1. Identify which stage created the missing artifacts
  2. Check if stage was marked complete in aidlc-state.md
  3. If marked complete but artifacts missing: Regenerate that stage
  4. If not marked complete: Resume from that stage
- **Recovery**: Return to the stage that creates missing artifacts and re-execute

**Error**: Artifact file exists but is empty or corrupted
- **Cause**: Interrupted write, manual editing, file system issues
- **Solution**:
  1. Create backup of corrupted file
  2. Attempt to regenerate from stage that creates it
  3. If cannot regenerate: Ask user for information to recreate
- **Recovery**: Re-execute the stage that creates the artifact

### Inconsistent State During Resumption

**Error**: aidlc-state.md shows a stage complete but its artifacts don't exist
- **Cause**: State updated but artifact generation failed
- **Solution**:
  1. Confirm the recorded state with `engine.py status`, then rewind to the stage with `engine.py jump --stage <slug>` (this resets the target stage and everything after it — never hand-edit the checkboxes)
  2. Re-execute the stage to generate the artifacts
  3. Verify the artifacts exist, then complete the stage through `engine.py report`
- **Recovery**: Rewind via `jump`, re-execute, and report through the engine

**Error**: Artifacts exist but aidlc-state.md shows a stage incomplete
- **Cause**: Artifact generation succeeded but the state transition was not recorded
- **Solution**:
  1. Verify the artifacts are complete and valid
  2. Record the transition through the engine: `python <skill>/scripts/engine.py report --stage <slug> --result approved` (or `--result completed` for a non-gate stage)
  3. Proceed to next stage
- **Recovery**: Complete the stage through the engine — never hand-edit the state region

**Error**: The engine state is inconsistent (e.g. multiple stages appear current)
- **Cause**: Corruption or manual editing of the engine-owned region
- **Solution**:
  1. Run `engine.py status`; if `integrity` is `violated`, HALT and present the drift plus the last audit transition entry to the user
  2. Ask the user which stage they are actually on; after confirmation, `engine.py rebase` (or `engine.py jump --stage <slug>` to rewind)
  3. Never correct the state by hand — the engine owns it
- **Recovery**: Re-baseline through the engine based on the confirmed actual progress

### Context Loading Errors

**Error**: Cannot load required context from previous stages
- **Cause**: Missing files, corrupted content, wrong file paths
- **Solution**:
  1. List which artifacts are needed for current stage
  2. Check which ones are missing or corrupted
  3. Regenerate missing artifacts or ask user for information
- **Recovery**: Complete prerequisite stages before resuming current stage

**Error**: Loaded artifacts contain contradictory information
- **Cause**: Manual editing, multiple people working, incomplete updates
- **Solution**:
  1. Identify contradictions and present to user
  2. Ask user which information is correct
  3. Update artifacts to resolve contradictions
- **Recovery**: Reconcile contradictions before proceeding

### Resumption Best Practices

1. **Always validate state**: Run `engine.py status` and check its `integrity` field; the engine-owned state region is never edited by hand
2. **Load incrementally**: Load artifacts stage-by-stage, validate each
3. **Fail fast**: Stop immediately if critical artifacts are missing
4. **Communicate clearly**: Tell user exactly what's missing and why it's needed
5. **Offer options**: Regenerate, provide manually, or start fresh
6. **Document recovery**: Log all recovery actions in audit.md

## Logging Requirements

### Error Logging Format

```markdown
## Error - [Stage Name]
**Timestamp**: [ISO timestamp]
**Error Type**: [Critical/High/Medium/Low]
**Description**: [What went wrong]
**Cause**: [Why it happened]
**Resolution**: [How it was resolved]
**Impact**: [Effect on workflow]

---
```

### Recovery Logging Format

```markdown
## Recovery - [Stage Name]
**Timestamp**: [ISO timestamp]
**Issue**: [What needed recovery]
**Recovery Steps**: [What was done]
**Outcome**: [Result of recovery]
**Artifacts Affected**: [List of files]

---
```

## Prevention Best Practices

1. **Validate Early**: Check inputs and dependencies before starting work
2. **Checkpoint Often**: Update plan-file checkboxes immediately after completing steps
3. **Communicate Clearly**: Explain what you're doing and why
4. **Ask Questions**: Don't assume - clarify ambiguities immediately
5. **Document Everything**: Log all decisions and changes in `audit.md`
