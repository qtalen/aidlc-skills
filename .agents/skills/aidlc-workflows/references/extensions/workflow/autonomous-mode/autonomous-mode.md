# Autonomous Mode Rules

## Overview

MANDATORY cross-cutting rules for every AI-DLC workflow execution while Autonomous Mode is active. This file has a companion `autonomous-mode.opt-in.md` — a lightweight trigger stub loaded at workflow start. **This full rules file is loaded ON-DEMAND, only when the stub detects a trigger phrase or persisted `Enabled: Yes` state.** Autonomous Mode is **OFF by default**: these rules stay dormant until the user explicitly triggers activation (AM-01). **Lifecycle**: activation scopes Autonomous Mode to the current workflow round — it ends at round completion (AM-10, engine-enforced) or earlier on an explicit Pause/Deactivate (AM-05/AM-07: the mode ends; the workflow itself continues in standard mode to the next approval gate). A new round always starts in standard mode; re-activation is a fresh AM-02 (both activation questions are asked fresh). Once active, every stage is auto-approved (AM-03) and question collection follows the configured mode (AM-04); the human control points are the Code-Gen Hold (AM-11) and an ad-hoc Pause at any moment (AM-05).

- **AM-01** Trigger Detection — recognize activation phrases in ANY user message, at ANY stage
- **AM-02** Activation Flow — audit, ask the two configuration questions (question handling + code-gen hold), auto-approve pending gate, persist state
- **AM-03** Stage Auto-Approval — skip "Wait for Explicit Approval" for every stage
- **AM-04** Question Handling — `auto-recommended` vs `manual` answer collection
- **AM-05** Pause / Stop — full deactivation: flip off, finish in-flight work, continue in standard mode to the next approval gate
- **AM-06** *(removed 2026-09-29, D17 — the review-stage safety valve is replaced by ad-hoc Pause AM-05 plus the Code-Gen Hold AM-11; the number is retired, not reused)*
- **AM-07** Deactivation — same outcome as Pause, reached via the "exit/turn-off" trigger vocabulary
- **AM-08** State Persistence — `## Autonomous Mode` section in aidlc-state.md
- **AM-09** Session Resumption — restore and announce autonomous mode on resume
- **AM-10** Round-Boundary Expiry — Autonomous Mode ends with the workflow round (engine flip + self-heal)
- **AM-11** Code-Gen Hold — optional one-time stop before the Code Generation stage (model-switch window); the mode stays on

**Enforcement**: When Autonomous Mode is active, verify compliance with the applicable AM rules BEFORE presenting any stage completion message or proceeding past any gate. Include AM rules in the stage compliance summary (compliant / non-compliant / N/A per rule, with brief rationale for N/A). Blocking finding behavior follows the same convention as the other groups in `../workflow-conventions/workflow-conventions.md`. When Autonomous Mode is OFF — including whenever this file has not been loaded — all AM rules are N/A.

---

## AM-01: Trigger Detection

**Note on first activation**: Initial detection of an Activate intent (and of persisted `Enabled: Yes` state) is performed by the companion `autonomous-mode.opt-in.md` stub, which loads this file on demand. Once this file is loaded, AM-01 takes over detection of ALL autonomous-mode intents (including Pause and Deactivate) for the rest of the session.

**MANDATORY**: Evaluate EVERY user message — at any stage, at any point in the conversation, not just at workflow start — for Autonomous Mode control semantics, in ANY language (Chinese, English, or others).

| Intent | Example trigger semantics (non-exhaustive) |
|---|---|
| Activate | "进入自主模式", "开启自主模式", "启用自主模式", "enter autonomous mode", "enable autonomous mode", "turn on autonomous mode", "go autonomous" |
| Pause / Stop | "暂停自主模式", "停止自主模式", "暂停一下", "pause autonomous mode", "stop autonomous mode", "pause", "hold on" — **only while Autonomous Mode is active** |
| Deactivate | "退出自主模式", "关闭自主模式", "exit autonomous mode", "turn off autonomous mode" |

- Trigger detection is **semantic**, not keyword-exact: any phrasing clearly expressing the intent counts.
- A trigger phrase takes precedence over whatever stage work is in progress — handle it FIRST, then resume or redirect work per the resulting configuration.
- Log every detected trigger in `aidlc-docs/audit.md` with the complete raw user input (per audit logging requirements, including AUD-01 authorship fields).
- While Autonomous Mode is OFF, "pause" semantics have no special meaning (nothing to pause); treat as normal conversation.
- While Autonomous Mode is active, Pause/Stop and Deactivate both end the mode via AM-05; an explicit immediate interrupt ("停下", "stop now") is NOT a Pause — it is the Park Ritual (see AM-05 point 6).

## AM-02: Activation Flow

On detecting an **Activate** intent, execute ALL of the following in the SAME interaction:

1. **Audit**: Log the trigger in audit.md with complete raw input.
2. **Ask configuration via the structured question tool** (see QT-01) — ONE tool invocation, TWO questions (presented in the user's conversation language):
   - **Question 1 (question handling)**: "在自主模式下，question 问题将如何处理？" / "How should questions be handled in Autonomous Mode?"
      - **Option A**: workflow 自动选择推荐 (Recommended) 答案并写入文档，然后继续往下进行 / The workflow automatically selects the recommended answer, writes it into the question file, and continues
      - **Option B**: 用户手动选择答案并写入文档，然后继续往下进行 / The user manually selects answers via the structured question tool, answers are written into the question file, then the workflow continues
      - Do NOT add an explicit "Other" option when the structured question tool has built-in custom input — that covers it. A custom (Other) answer takes effect as the question-handling mode; record the verbatim custom text in state and audit.md. (If the tool has no built-in custom input, add an explicit "Other" option, per QT-01.)
   - **Question 2 (code-gen hold)**: "进入代码生成阶段前，是否先停下来，给你一个切换模型的机会（例如切换到更快的模型做实施）？" / "Before the Code Generation stage begins, should the workflow make a one-time stop so you can switch models (e.g., to a faster model for implementation)?"
      - **Option A**: 是——代码生成前停一次；你说"继续"后，自主模式继续执行直到本轮工作流完成 / Yes — stop once before code generation; after you say continue, Autonomous Mode runs to the end of this workflow round
      - **Option B**: 否——不停，自主模式一直执行到本轮工作流完成 / No — do not stop; run straight through to the end of this workflow round
      - Ask Question 2 fresh at EVERY activation — no persisted value is ever reused as a preselection or default. Skip Question 2 entirely (record `Code-Gen Hold: N/A`) when the Code Generation stage's work has already begun this round or the stage is not among the remaining stages (check `remaining` in the engine status/next output) — the model-switch window has passed. A custom answer takes effect per its intent (e.g., a different stop point or an extra condition); record the verbatim text in state and audit.md, and ask ONE clarifying question if the intent is ambiguous.
   - If no structured question tool is available or it errors out, ask via a question file per `../../../common/question-format-guide.md` (fallback per QT-04) and note the fallback in audit.md.
3. **Auto-approve pending gate**: If a stage approval gate is currently waiting for user confirmation, treat that stage's documents as approved — record the transition with the engine (`engine.py report --stage <slug> --result approved`, never a hand-edit of the stage checkboxes), log `Auto-approved (Autonomous Mode)` in audit.md, and proceed to the next stage automatically.
4. **Persist state**: Create or update the `## Autonomous Mode` section in aidlc-state.md per AM-08 (Enabled: Yes; Question Handling per Question 1; Code-Gen Hold per Question 2 — `Pending` when yes, `Off` when no, `N/A` when skipped).
5. **Announce**: Briefly confirm activation to the user: autonomous mode is on, the chosen question-handling mode, the code-gen hold choice, and that the mode lasts until this workflow round completes or the user explicitly stops it (AM-10/AM-05). If Question 2 was answered "yes" AND Code Generation is already the current stage with no work begun, present the hold immediately after this announcement (AM-11). If the workflow is currently **completed** (activation in the gap before a re-entry), also warn that this configuration will be expired by the engine at re-entry — re-activate after the new round starts.
6. **Continue**: Resume workflow execution immediately under the new configuration (subject to AM-11 when the hold is armed).

## AM-03: Stage Auto-Approval

While Autonomous Mode is active — **every stage**; there is no review-stage list:

1. **Override APG-01~04**: The "Wait for Explicit Approval" / "DO NOT PROCEED until user confirms" steps in SKILL.md and all stage rule files are suspended. AM-03 takes precedence.
2. Stage completion messages are still generated and presented **for information only** — the user can see what was produced, but the workflow does NOT wait.
3. In the SAME interaction as the completion message: record the transition through the engine (`engine.py report --stage <slug> --result approved` for a gate stage, `--result completed` for a non-gate stage — never a hand-edit of the stage checkboxes), append an audit.md entry with `**AI Response**: "Auto-approved (Autonomous Mode)"`, and immediately begin the next stage.
4. APG-05 still applies: completion message templates are never modified.
5. All other completion obligations remain in force (plan checkbox updates, DOC-01 sweep, extension compliance summary, content validation) — auto-approval skips ONLY the wait, never the work.
6. The Code-Gen Hold (AM-11) takes precedence at the Code Generation boundary: when the hold is armed and Code Generation is about to start, present the hold and wait per AM-11 — do NOT auto-approve past it.

**Verification**: no autonomous stage sits waiting for approval; every auto-approval has a corresponding audit entry and state update in the same interaction.

## AM-04: Question Handling

Applies to every `{phase-name}-questions.md` file (including `-clarification-questions.md` variants) created while Autonomous Mode is active.

### Mode `auto-recommended`

1. Create the question file as usual (question-format-guide.md rules unchanged).
2. **Override QT-01**: Do NOT call the structured question tool to collect user answers. Instead, the AI selects the best answer for each question itself — the option it would have marked "(Recommended)".
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
6. If a question is genuinely undecidable from available context (no defensible recommendation), escalate **that single question**: ask the user via the structured question tool (question text, options, and the "(Recommended)" marking included) and write the answer back with attribution — Autonomous Mode stays active; do NOT deactivate the mode over an undecidable question.

### Mode `manual`

Follow the standard QT-01~04 flow exactly as if Autonomous Mode were off: question file creation → structured question tool invocation → user answers → write-back → validation → proceed. Only stage approval gates (AM-03) are automated in this mode.

### Custom (Other) mode

Honor the user's verbatim custom instruction for how questions are handled. If the instruction is ambiguous or unactionable, ask for clarification via the structured question tool — Autonomous Mode stays active.

## AM-05: Pause / Stop

On detecting a **Pause / Stop** intent ("暂停/停止自主模式") while Autonomous Mode is active, the mode is **fully deactivated** — and the workflow degrades gracefully; it is never frozen mid-generation:

1. **Audit**: Log the trigger with complete raw input.
2. **Deactivate**: Update aidlc-state.md `## Autonomous Mode` → Enabled: No (keep the Question Handling and Code-Gen Hold values for reference, per AM-08).
3. **Announce**: Autonomous Mode is off. The in-flight work will be completed first; the workflow then continues in standard mode to the **next approval gate** and waits there for human approval. From this moment until the workflow round ends, everything runs under standard rules — the mode never restarts itself; only an explicit Activate intent (AM-01) re-runs AM-02.
4. **Continue gracefully**: finish the current in-flight step/artifact to a consistent state — never abandon half-done work, and do not start anything beyond it. The "next approval gate" is the current stage's own completion gate when it is a gate stage; otherwise the first subsequent gate in the routed plan (per-unit segment gates count). Non-gate stages pass through without waiting, exactly as in standard mode.
5. **Pending questions**: an AM-04 escalated question (or an open question file) waiting at pause time continues under the standard QT flow — it is never dropped.
6. **Precedence vs parking**: while Autonomous Mode is active, a Pause intent is handled by THIS rule, not by the Park Ritual (session-continuity.md). An explicit immediate interrupt ("停下", "stop now") is the Park Ritual — the mode stays enabled across the park and AM-09 resumes it. If the user combines both intents (stop now AND pause the mode), park per the ritual and flip the mode off here — the graceful-continue clause is waived.

## AM-06: (removed 2026-09-29)

*The Review Stage List rule was removed in D17 (2026-09-29): pre-configuring per-stage human gates proved unnecessary — the user can pause at any moment (AM-05, graceful degradation to the next approval gate) and the Code-Gen Hold (AM-11) guards the implementation boundary. The rule number is retired, not reused. The state-file `Review Stages` line was removed from the templates; a leftover line in an old workspace is inert — no rule reads it, and the engine parses it leniently as an unknown key and ignores it.*

## AM-07: Deactivation

On detecting a **Deactivate** intent ("退出/关闭自主模式"): the outcome is identical to Pause — the mode ends now and the workflow continues in standard mode to the next approval gate. Execute the AM-05 flow (audit → flip off → announce → graceful continue). One addition: if a stage was auto-approved mid-flight (AM-03) and the user wants it re-reviewed, treat that as a normal change request for that stage (see `../../../common/workflow-changes.md`).

## AM-08: State Persistence

**MANDATORY**: Maintain an `## Autonomous Mode` section in `aidlc-docs/aidlc-state.md`.

`aidlc-state.md` itself is created by the engine (`engine.py init`, see workspace-detection.md); the model owns and maintains the `## Autonomous Mode` section within it. On a new project, add the section with these defaults:

```markdown
## Autonomous Mode
- **Enabled**: No
- **Question Handling**: N/A
- **Code-Gen Hold**: N/A
- **Last Updated**: [ISO timestamp]
```

While active, keep it current (update on every AM-02/AM-05/AM-07 configuration change and every AM-11 hold-state change):

```markdown
## Autonomous Mode
- **Enabled**: Yes
- **Question Handling**: auto-recommended | manual | [verbatim custom text]
- **Code-Gen Hold**: Pending | Passed | Off | N/A | [verbatim custom hold instruction]
- **Last Updated**: [ISO timestamp]
```

`Code-Gen Hold` states: `Pending` (armed — stop before Code Generation per AM-11), `Passed` (released — never re-triggers this activation), `Off` (user declined at AM-02), `N/A` (not applicable — Code Generation not ahead, or its work already began). A custom AM-02 answer (e.g., a different stop point or an extra condition) is recorded verbatim on this line INSTEAD of the enum — AM-11's trigger fires only on exactly `Pending`; a custom variant takes effect per its recorded intent (log it in audit.md as well, and it survives sessions like every other line here). The line is model-written and model-read — the engine's `autonomous` status key carries only `enabled`/`question_handling`/`last_updated` and does not parse this line. After round expiry the line survives as an inert reference, never reused as a preselection or default (AM-02 always asks fresh).

State updates happen in the SAME interaction as the triggering change. Historical entries are never rewritten (DOC-04) — configuration history lives in audit.md; this section always reflects the CURRENT configuration.

**Engine write window (AM-10)**: the engine may flip `Enabled` to `No` (and refresh an existing `Last Updated` line) at the deterministic round boundaries — transitions that complete the workflow, and a re-entry jump — without model involvement. Never "restore" `Enabled: Yes` after an engine expiry; a live mode requires a fresh AM-02.

## AM-09: Session Resumption

When resuming an existing project (per `../../../common/session-continuity.md`):

1. Read the `## Autonomous Mode` section of aidlc-state.md along with the rest of the state file.
2. **If Enabled = Yes**: Autonomous Mode remains active — announce its status in the welcome-back summary (question-handling mode, code-gen hold state, last updated; the hold state is read from this section, not from the engine's `autonomous` key), and continue execution under AM rules without requiring re-activation. If the current stage is Code Generation and `Code-Gen Hold: Pending`, the workflow is sitting at the hold: re-present it (AM-11) instead of starting stage work.
3. **If Enabled = No or section missing**: Standard mode; AM rules dormant until a new AM-01 trigger.
4. **If the workflow is completed**: Autonomous Mode is expired (AM-10) — the section reads `Enabled: No`; announce standard mode. A stale `Enabled: Yes` in a pre-AM-10 completed workspace is treated as expired: flip it per AM-08 (auditing the expiry) before continuing a new round, including the plan-line self-revival path.
5. If the section is malformed, fall back to Enabled: No, note the recovery in audit.md, and continue in standard mode.

## AM-10: Round-Boundary Expiry

Autonomous Mode is scoped to the current workflow round. It ends at exactly three boundaries:

1. **Round completion (engine-enforced)**: the transition that completes the workflow — the final `report`, or a `jump` that leaves the workflow completed (e.g. a forward jump to an out-of-plan target past the last routed pending stage) — flips a live section to `Enabled: No` (Question Handling / Code-Gen Hold are kept for reference), the ack carries `autonomous_expired: true`, and the audit entry notes the expiry. In the SAME interaction as the closing summary (the `done` directive), announce that Autonomous Mode has ended with the round. After expiry these rules are dormant again — all AM rules are N/A until a new activation.
2. **Re-entry (engine-enforced self-heal)**: a `jump --stage` from the completed state — the sanctioned start of a new same-product round — performs the same flip, healing workspaces completed before AM-10 existed. **Plan-line self-revival path**: when a new round starts WITHOUT a jump (plan lines edited first, `status` re-activating the workflow — see `../../../common/workflow-changes.md`), no engine verb runs; the MODEL must ensure `Enabled: No` before continuing the round (flip the section per AM-08, audit the expiry, and announce it).
3. **Start Fresh / new project**: `jump --fresh` archives the whole `aidlc-docs/` directory — the section disappears with it, and a new project's state file starts section-less. Standard mode directly; there is no state to flip.

After ANY boundary, re-activation requires an explicit Activate intent (AM-01) and a fresh AM-02 — both activation questions are asked fresh every time; no persisted configuration value (Question Handling, Code-Gen Hold, or anything else) is ever reused as a preselection or silently carried over. Mid-round persistence is unchanged: within the same round, sessions resume with Autonomous Mode active (AM-09).

## AM-11: Code-Gen Hold

An optional one-time stop right before implementation work begins, configured at activation (AM-02 Question 2). Typical use: switching to a faster model for the implementation stages.

**Arming**: the hold is armed (`Code-Gen Hold: Pending`) only when AM-02 Question 2 is answered "yes" AND the Code Generation stage's work has not yet begun this round (the stage is still ahead, or it is current but no work has started). Otherwise the line records `N/A` — the window has passed. Each activation arms at most one hold; a fresh AM-02 may re-arm one while the window is still open.

**Trigger — present the hold and do NOT start Code Generation work** when `Code-Gen Hold: Pending` and any of:

1. a transition makes Code Generation the current stage (the normal arrival path — this takes precedence over AM-03's "immediately begin the next stage");
2. activation completed while Code Generation was already current with no work begun (present right after the activation announcement, per AM-02 step 5);
3. a session resumes into the hold-waiting state (current stage Code Generation, hold `Pending` — see AM-09).

**Announcement**: state that the workflow is about to start Code Generation, that Autonomous Mode REMAINS ACTIVE (this is a stop point, not a Pause — AM-05 is not involved), and that this is the window to switch models or review the design artifacts; saying "continue" (or similar semantics, in any language) proceeds.

**Release**: on continue-semantics, flip the line to `Passed` (refresh `Last Updated`, one audit entry) in the SAME interaction, then begin Code Generation under AM rules. The hold never re-triggers within this activation — a backward redo into Code Generation does not re-present it (the user can always request an ad-hoc stop conversationally).

**Other responses**: handle per intent — change requests go through the normal change flow, configuration changes are applied as asked. After handling, the hold KEEPS WAITING until continue-semantics arrives. An explicit "skip the hold / no need to stop" counts as continue-semantics for the hold itself (record `Passed` and proceed).

**Not a Pause, not a park**: the mode stays enabled and the Park Ritual is not involved. Contrast: AM-05 ends the mode and continues to the next approval gate in standard mode; the hold suspends progress at one boundary while the mode stays on, then runs to round completion.

---

## Enforcement Integration

| Context | Applicable Rules |
|---|---|
| Every user message, any stage | AM-01 |
| Activation detected | AM-02, AM-08 |
| Every stage approval gate while active | AM-03 |
| Every question file while active | AM-04 |
| Pause / Stop / Deactivate detected | AM-05, AM-07, AM-08 |
| aidlc-state.md creation/update | AM-08 |
| Session resumption | AM-09 |
| Workflow completion / re-entry / fresh | AM-10 |
| Code Generation boundary while hold armed | AM-11 |
| This file's own maintenance | DOC-05, AUD-04 (see workflow-conventions) |
