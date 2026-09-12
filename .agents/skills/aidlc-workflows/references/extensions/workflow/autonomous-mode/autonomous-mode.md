# Autonomous Mode Rules

## Overview

MANDATORY cross-cutting rules for every AI-DLC workflow execution while Autonomous Mode is active. This file has a companion `autonomous-mode.opt-in.md` — a lightweight trigger stub loaded at workflow start. **This full rules file is loaded ON-DEMAND, only when the stub detects a trigger phrase or persisted `Enabled: Yes` state.** Autonomous Mode is **OFF by default**: these rules stay dormant until the user explicitly triggers activation (AM-01). Once active, they override stage approval gates (APG group) and question collection (QT group) per the rules below.

- **AM-01** Trigger Detection — recognize activation phrases in ANY user message, at ANY stage
- **AM-02** Activation Flow — audit, ask question-handling preference, auto-approve pending gate, persist state
- **AM-03** Stage Auto-Approval — skip "Wait for Explicit Approval" for non-review stages
- **AM-04** Question Handling — `auto-recommended` vs `manual` answer collection
- **AM-05** Pause — stop immediately and offer adjustment menu
- **AM-06** Review Stage List — named stages keep standard approval gates
- **AM-07** Deactivation — full return to the standard workflow
- **AM-08** State Persistence — `## Autonomous Mode` section in aidlc-state.md
- **AM-09** Session Resumption — restore and announce autonomous mode on resume

**Enforcement**: When Autonomous Mode is active, verify compliance with the applicable AM rules BEFORE presenting any stage completion message or proceeding past any gate. Include AM rules in the stage compliance summary (compliant / non-compliant / N/A per rule, with brief rationale for N/A). Blocking finding behavior follows the same convention as the other groups in `../workflow-conventions/workflow-conventions.md`. When Autonomous Mode is OFF — including whenever this file has not been loaded — all AM rules are N/A.

---

## AM-01: Trigger Detection

**Note on first activation**: Initial detection of an Activate intent (and of persisted `Enabled: Yes` state) is performed by the companion `autonomous-mode.opt-in.md` stub, which loads this file on demand. Once this file is loaded, AM-01 takes over detection of ALL autonomous-mode intents (including Pause and Deactivate) for the rest of the session.

**MANDATORY**: Evaluate EVERY user message — at any stage, at any point in the conversation, not just at workflow start — for Autonomous Mode control semantics, in ANY language (Chinese, English, or others).

| Intent | Example trigger semantics (non-exhaustive) |
|---|---|
| Activate | "进入自主模式", "开启自主模式", "启用自主模式", "enter autonomous mode", "enable autonomous mode", "turn on autonomous mode", "go autonomous" |
| Pause | "暂停自主模式", "暂停一下", "pause autonomous mode", "pause", "hold on" — **only while Autonomous Mode is active** |
| Deactivate | "退出自主模式", "停止自主模式", "关闭自主模式", "exit autonomous mode", "stop autonomous mode", "turn off autonomous mode" |

- Trigger detection is **semantic**, not keyword-exact: any phrasing clearly expressing the intent counts.
- A trigger phrase takes precedence over whatever stage work is in progress — handle it FIRST, then resume or redirect work per the resulting configuration.
- Log every detected trigger in `aidlc-docs/audit.md` with the complete raw user input (per audit logging requirements, including AUD-01 authorship fields).
- While Autonomous Mode is OFF, "pause" semantics have no special meaning (nothing to pause); treat as normal conversation.

## AM-02: Activation Flow

On detecting an **Activate** intent, execute ALL of the following in the SAME interaction:

1. **Audit**: Log the trigger in audit.md with complete raw input.
2. **Ask question-handling preference**: Call the `question` tool with this question (presented in the user's conversation language):
   - **Question**: "在自主模式下，question 问题将如何处理？" / "How should questions be handled in Autonomous Mode?"
   - **Option A**: workflow 自动选择推荐 (Recommended) 答案并写入文档，然后继续往下进行 / The workflow automatically selects the recommended answer, writes it into the question file, and continues
   - **Option B**: 用户手动选择答案并写入文档，然后继续往下进行 / The user manually selects answers via the question tool, answers are written into the question file, then the workflow continues
   - Do NOT add an explicit "Other" option — the tool's built-in custom input covers it. A custom (Other) answer takes effect as the question-handling mode; record the verbatim custom text in state and audit.md.
   - If the `question` tool is unavailable or errors out, ask via a question file per `../../../common/question-format-guide.md` (fallback per QT-04) and note the fallback in audit.md.
3. **Auto-approve pending gate**: If a stage approval gate is currently waiting for user confirmation, treat that stage's documents as approved — mark the stage complete in aidlc-state.md, log `Auto-approved (Autonomous Mode)` in audit.md, and proceed to the next stage automatically.
4. **Persist state**: Create or update the `## Autonomous Mode` section in aidlc-state.md per AM-08 (Enabled: Yes, Question Handling: `auto-recommended` or `manual` or the verbatim custom text, Review Stages: None).
5. **Announce**: Briefly confirm activation to the user: autonomous mode is on, the chosen question-handling mode, and that stage documents are treated as approved unless listed as review stages.
6. **Continue**: Resume workflow execution immediately under the new configuration.

## AM-03: Stage Auto-Approval

While Autonomous Mode is active and the current stage is **NOT** in the Review Stages list (AM-06):

1. **Override APG-01~04**: The "Wait for Explicit Approval" / "DO NOT PROCEED until user confirms" steps in SKILL.md and all stage rule files are suspended for this stage. AM-03 takes precedence.
2. Stage completion messages are still generated and presented **for information only** — the user can see what was produced, but the workflow does NOT wait.
3. In the SAME interaction as the completion message: mark the stage complete in aidlc-state.md (suffix the status with `(autonomous)`), append an audit.md entry with `**AI Response**: "Auto-approved (Autonomous Mode)"`, and immediately begin the next stage.
4. APG-05 still applies: completion message templates are never modified.
5. All other completion obligations remain in force (plan checkbox updates, DOC-01 sweep, extension compliance summary, content validation) — auto-approval skips ONLY the wait, never the work.

**Verification**: no autonomous stage sits waiting for approval; every auto-approval has a corresponding audit entry and state update in the same interaction.

## AM-04: Question Handling

Applies to every `{phase-name}-questions.md` file (including `-clarification-questions.md` variants) created while Autonomous Mode is active.

### Mode `auto-recommended`

1. Create the question file as usual (question-format-guide.md rules unchanged).
2. **Override QT-01**: Do NOT call the `question` tool to collect user answers. Instead, the AI selects the best answer for each question itself — the option it would have marked "(Recommended)".
3. **Write back with attribution**: Fill each `[Answer]:` tag as:

   ```markdown
   [Answer]: B (autonomous - recommended)
   ```

   Immediately after the answer line, append one line:

   ```markdown
   **Rationale** (autonomous): [one-sentence justification grounded in requirements/context]
   ```

   Question text and option lists MUST NOT be altered during write-back (aligns with DOC-04). If the file already contains user-provided answers from before activation, leave them untouched.
4. **Audit**: Log one audit.md entry listing every auto-selected answer (question number, letter, brief rationale).
5. **Proceed**: Run the standard validation (completeness check + contradiction/ambiguity detection) and continue directly — do NOT wait for user confirmation. Clarification question files produced by validation are handled by this same mode.
6. If a question is genuinely undecidable from available context (no defensible recommendation), escalate: pause per AM-05 and ask the user via the `question` tool.

### Mode `manual`

Follow the standard QT-01~04 flow exactly as if Autonomous Mode were off: question file creation → `question` tool invocation → user answers → write-back → validation → proceed. Only stage approval gates (AM-03) are automated in this mode.

### Custom (Other) mode

Honor the user's verbatim custom instruction for how questions are handled. If the instruction is ambiguous or unactionable, pause per AM-05 and ask for clarification via the `question` tool.

## AM-05: Pause

On detecting a **Pause** intent while Autonomous Mode is active:

1. **Stop immediately**: Do not finish the current step, stage, or any in-progress generation — halt within the current interaction. If a step was interrupted mid-way, note the exact interruption point in aidlc-state.md so it can be resumed cleanly.
2. **Audit**: Log the pause trigger with complete raw input.
3. **Offer adjustment menu**: Call the `question` tool with:
   - **Option A**: 重新选择 question 问题的处理方式 / Re-choose the question-handling mode (re-runs the AM-02 step 2 question)
   - **Option B**: 设置需要人工审核的阶段 / Set review stages — present a multi-select (`multiple: true`) question listing ALL stage names (<!-- BEGIN GENERATED: stage-names | do not hand-edit — regenerated by scripts/generate.py -->Workspace Detection, Reverse Engineering, Requirements Analysis, User Stories, Workflow Planning, Application Design, Units Generation, Functional Design, NFR Requirements, NFR Design, Infrastructure Design, Code Generation, Build and Test<!-- END GENERATED: stage-names -->); selected stages go into the Review Stages list (replacing the previous list); the user may also name stages freely via custom input
   - **Option C**: 退出自主模式 / Exit Autonomous Mode (execute AM-07)
   - **Option D**: 恢复自主运行 / Resume autonomous execution (continue from the interruption point)
4. **Persist**: Update the `## Autonomous Mode` section per AM-08 with any changes, then act on the chosen option.
5. If the user answers the pause with free-form instructions instead of the menu, honor the instructions (updating configuration as needed) and ask whether to resume.

## AM-06: Review Stage List

1. Stages named in the Review Stages list use the **standard approval gates**: present the completion message and WAIT for explicit approval per APG-01~05, exactly as if Autonomous Mode were off for that stage.
2. All stages NOT in the list continue under AM-03 auto-approval.
3. The list applies by stage name — for per-unit construction stages, a listed stage is reviewed for EVERY unit.
4. The list may be changed at any time via AM-05 (pause → Option B). Changes take effect from the next gate encountered; already auto-approved stages are not revisited.
5. Question handling (AM-04) is independent of the review list: review stages still process question files per the configured mode.

## AM-07: Deactivation

On detecting a **Deactivate** intent (or AM-05 menu Option C):

1. Stop autonomous behavior immediately.
2. Update aidlc-state.md: `## Autonomous Mode` → Enabled: No (keep Question Handling and Review Stages values for reference, or clear them per user instruction).
3. Log deactivation in audit.md with complete raw input.
4. Confirm to the user: the workflow has returned to standard mode — all subsequent stages use standard approval gates and standard question flow.
5. Resume from the current point under standard rules. If a stage was auto-approved mid-flight and the user wants to re-review it, treat that as a normal change request for that stage.

## AM-08: State Persistence

**MANDATORY**: Maintain an `## Autonomous Mode` section in `aidlc-docs/aidlc-state.md`.

When creating a new aidlc-state.md (Workspace Detection), include the section with defaults:

```markdown
## Autonomous Mode
- **Enabled**: No
- **Question Handling**: N/A
- **Review Stages**: None
- **Last Updated**: [ISO timestamp]
```

While active, keep it current (update on every AM-02/AM-05/AM-07 configuration change):

```markdown
## Autonomous Mode
- **Enabled**: Yes
- **Question Handling**: auto-recommended | manual | [verbatim custom text]
- **Review Stages**: [comma-separated stage names, or "None"]
- **Last Updated**: [ISO timestamp]
```

State updates happen in the SAME interaction as the triggering change. Historical entries are never rewritten (DOC-04) — configuration history lives in audit.md; this section always reflects the CURRENT configuration.

## AM-09: Session Resumption

When resuming an existing project (per `../../../common/session-continuity.md`):

1. Read the `## Autonomous Mode` section of aidlc-state.md along with the rest of the state file.
2. **If Enabled = Yes**: Autonomous Mode remains active — announce its status in the welcome-back summary (question-handling mode, review stages, last updated), and continue execution under AM rules without requiring re-activation.
3. **If Enabled = No or section missing**: Standard mode; AM rules dormant until a new AM-01 trigger.
4. If the section is malformed, fall back to Enabled: No, note the recovery in audit.md, and continue in standard mode.

---

## Enforcement Integration

| Context | Applicable Rules |
|---|---|
| Every user message, any stage | AM-01 |
| Activation detected | AM-02, AM-08 |
| Every stage approval gate while active | AM-03, AM-06 |
| Every question file while active | AM-04 |
| Pause detected | AM-05, AM-08 |
| Deactivation detected | AM-07, AM-08 |
| aidlc-state.md creation/update | AM-08 |
| Session resumption | AM-09 |
| This file's own maintenance | DOC-05, AUD-04 (see workflow-conventions) |
