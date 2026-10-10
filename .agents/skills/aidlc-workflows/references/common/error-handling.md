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

Stage-specific failure patterns (contradictions, ambiguous answers, incomplete plans, generation failures) follow the procedures already defined in each stage rule file and the contradiction/ambiguity machinery in `question-format-guide.md` — they are not restated per stage here. Two cross-stage rules apply everywhere:

- **HUMAN TASK marking**: when a step requires human-only action (credentials, network/system access, organizational approvals), mark it **HUMAN TASK**, provide instructions, and wait for user confirmation before proceeding.
- **Engine-owned state**: any error touching `aidlc-state.md` is handled exclusively through the engine (see Recovery Procedures below) — never by hand-editing the state region.

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

**Recovery**: follow `references/common/workflow-changes.md` — Type 3 (Restarting Current Stage) / Type 4 (Restarting Previous Stage). Essentials: confirm the user accepts that existing work will be lost; execute only through the engine — `engine.py jump --stage <slug>` resets the target stage and every stage after it (never hand-edit the stage status); clear the stage checkboxes in the plan files; re-execute from the beginning.

### User Wants to Skip Stage

**Scenario**: User wants to skip a stage that was planned

**Recovery**: follow `references/common/workflow-changes.md` — Type 2 (Skipping a Planned Stage): confirm impact and get explicit confirmation, record the skip through the engine (the **order matters** rule and the exact command sequence live there), and document the reason in `audit.md`. Later stages may need manual setup if dependencies are missing.

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

**Consider Fresh Start If** (a *new product intent*, or damage the engine cannot recover from):
- Multiple stages have errors
- State file is severely corrupted
- User cannot provide missing information
- Artifacts are inconsistent across phases

**Never fresh-start triggers**: significant requirement changes and architectural reversals are **same-product evolution** — handle them in place per `references/common/workflow-changes.md` (Re-Entering a Completed Workflow when the workflow has completed; Type 7 / Type 10 mid-workflow). Do not archive a working tree for these.

**Before Starting Over**:
1. Document lessons learned
2. Identify what to preserve
3. Get user confirmation
4. Create new execution plan
5. Reset through the engine: `python <skill>/scripts/engine.py jump --fresh` (archives `aidlc-docs/` and resets state) — never rebuild the state file by hand; archival is owned exclusively by this engine step, never done manually before it

## Session Resumption Errors

**Sensor-first ordering**: Before applying any recovery step in this section, run `engine.py status` and check `artifact_alerts` (missing-produces). If it flags missing artifacts, report them to the user first — never write or fabricate the artifacts yourself. Only after the user decides (confirming the artifacts are lost and must be redone) proceed to the recovery paths below.

**Artifacts/state mismatches at resumption** — identify the case, recover through the engine (never hand-edit the state region):

- **Stage recorded complete, but its artifacts are missing, empty, or corrupted**: confirm the recorded state with `engine.py status`, rewind with `engine.py jump --stage <slug>` (resets the target and every stage after it), re-execute the stage, then complete it through `engine.py report`. If regeneration is impossible, ask the user to provide the information and document the gap in `audit.md`.
- **Artifacts complete and valid, but the stage was never recorded**: catch up through the engine — `engine.py report --stage <slug> --result approved` (or `--result completed` for a non-gate stage) — then continue.
- **Loaded artifacts contradict each other**: identify the contradictions, present them to the user, reconcile per the confirmed truth before proceeding.
- **The engine state itself is inconsistent** (e.g. multiple stages appear current, or `integrity: violated`): run `engine.py status`; on a violated digest HALT and present the drift plus the last audit transition entry; ask the user which stage they are actually on; after confirmation, `engine.py rebase` (or `jump --stage <slug>` to rewind).

**Resumption practices**: validate state first (`status` + `integrity`); load artifacts incrementally per the tiered-reading rules in `session-continuity.md`; fail fast on critical gaps; offer regenerate / provide-manually / re-enter options (same-product iteration → `jump --stage`, see `workflow-changes.md`); log every recovery action in `audit.md`.

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
