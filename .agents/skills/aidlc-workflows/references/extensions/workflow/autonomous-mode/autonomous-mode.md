# Autonomous Mode Rules

## Overview

MANDATORY cross-cutting rules for every AI-DLC workflow execution while Autonomous Mode is active. This file has a companion `autonomous-mode.opt-in.md` — a lightweight trigger stub loaded at workflow start. **This full rules file is loaded ON-DEMAND, only when the stub detects a trigger phrase or persisted `Enabled: Yes` state.** Autonomous Mode is **OFF by default**: these rules stay dormant until the user explicitly triggers activation (AM-01). **Lifecycle**: activation scopes Autonomous Mode to the current workflow round — it ends at round completion (AM-10, engine-enforced) or earlier on an explicit Pause/Deactivate (AM-05/AM-07). A new round always starts in standard mode; re-activation is a fresh AM-02 (question handling is re-asked). Once active, they override stage approval gates (APG group) and question collection (QT group) per the rules below.

- **AM-01** Trigger Detection — recognize activation phrases in ANY user message, at ANY stage
- **AM-02** Activation Flow — audit, ask question-handling preference, auto-approve pending gate, persist state
- **AM-03** Stage Auto-Approval — skip "Wait for Explicit Approval" for non-review stages
- **AM-04** Question Handling — `auto-recommended` vs `manual` answer collection
- **AM-05** Pause — full deactivation on interrupt: stop, park, flip off, offer how to proceed
- **AM-06** Review Stage List — named stages keep standard approval gates
- **AM-07** Deactivation — full return to the standard workflow
- **AM-08** State Persistence — `## Autonomous Mode` section in aidlc-state.md
- **AM-09** Session Resumption — restore and announce autonomous mode on resume
- **AM-10** Round-Boundary Expiry — Autonomous Mode ends with the workflow round (engine flip + self-heal)

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
2. **Ask configuration via the structured question tool** (see QT-01) — ONE tool invocation, TWO questions (presented in the user's conversation language):
   - **Question 1 (question handling)**: "在自主模式下，question 问题将如何处理？" / "How should questions be handled in Autonomous Mode?"
     - **Option A**: workflow 自动选择推荐 (Recommended) 答案并写入文档，然后继续往下进行 / The workflow automatically selects the recommended answer, writes it into the question file, and continues
     - **Option B**: 用户手动选择答案并写入文档，然后继续往下进行 / The user manually selects answers via the structured question tool, answers are written into the question file, then the workflow continues
     - Do NOT add an explicit "Other" option when the structured question tool has built-in custom input — that covers it. A custom (Other) answer takes effect as the question-handling mode; record the verbatim custom text in state and audit.md. (If the tool has no built-in custom input, add an explicit "Other" option, per QT-01.)
   - **Question 2 (review stages)**: "哪些阶段需要保留人工审核关卡？" / "Which stages should keep their standard human approval gates?" — a multi-select over the stage names below; stages NOT selected are auto-approved per AM-03. Preselect the stages in the section's current `Review Stages` value (a previous round's list survives there for reference); when that value is `None` or absent, preselect nothing. The user may also name stages freely via custom input (resolve names per AM-06.6).
<!-- BEGIN GENERATED: stage-names | do not hand-edit — regenerated by scripts/generate.py -->
Workspace Detection, Reverse Engineering, Requirements Analysis, User Stories, Workflow Planning, Application Design, Units Generation, Functional Design, NFR Requirements, NFR Design, Infrastructure Design, Code Generation, Build and Test
<!-- END GENERATED: stage-names -->
   - If no structured question tool is available or it errors out, ask via a question file per `../../../common/question-format-guide.md` (fallback per QT-04) and note the fallback in audit.md.
3. **Auto-approve pending gate**: If a stage approval gate is currently waiting for user confirmation, treat that stage's documents as approved — record the transition with the engine (`engine.py report --stage <slug> --result approved`, never a hand-edit of the stage checkboxes), log `Auto-approved (Autonomous Mode)` in audit.md, and proceed to the next stage automatically.
4. **Persist state**: Create or update the `## Autonomous Mode` section in aidlc-state.md per AM-08 (Enabled: Yes; Question Handling per Question 1; Review Stages per Question 2 — "None" when nothing is selected).
5. **Announce**: Briefly confirm activation to the user: autonomous mode is on, the chosen question-handling mode, the review-stage list, and that the mode lasts until this workflow round completes or the user explicitly stops it (AM-10). If the workflow is currently **completed** (activation in the gap before a re-entry), also warn that this configuration will be expired by the engine at re-entry — re-activate after the new round starts.
6. **Continue**: Resume workflow execution immediately under the new configuration.

## AM-03: Stage Auto-Approval

While Autonomous Mode is active and the current stage is **NOT** in the Review Stages list (AM-06):

1. **Override APG-01~04**: The "Wait for Explicit Approval" / "DO NOT PROCEED until user confirms" steps in SKILL.md and all stage rule files are suspended for this stage. AM-03 takes precedence.
2. Stage completion messages are still generated and presented **for information only** — the user can see what was produced, but the workflow does NOT wait.
3. In the SAME interaction as the completion message: record the transition through the engine (`engine.py report --stage <slug> --result approved` for a gate stage, `--result completed` for a non-gate stage — never a hand-edit of the stage checkboxes), append an audit.md entry with `**AI Response**: "Auto-approved (Autonomous Mode)"`, and immediately begin the next stage.
4. APG-05 still applies: completion message templates are never modified.
5. All other completion obligations remain in force (plan checkbox updates, DOC-01 sweep, extension compliance summary, content validation) — auto-approval skips ONLY the wait, never the work.

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
6. If a question is genuinely undecidable from available context (no defensible recommendation), escalate **that single question**: ask the user via the structured question tool (question text, options, and the "(Recommended)" marking included) and write the answer back with attribution — Autonomous Mode stays active; do NOT route this through AM-05.

### Mode `manual`

Follow the standard QT-01~04 flow exactly as if Autonomous Mode were off: question file creation → structured question tool invocation → user answers → write-back → validation → proceed. Only stage approval gates (AM-03) are automated in this mode.

### Custom (Other) mode

Honor the user's verbatim custom instruction for how questions are handled. If the instruction is ambiguous or unactionable, ask for clarification via the structured question tool — Autonomous Mode stays active.

## AM-05: Pause

On detecting a **Pause** intent while Autonomous Mode is active, Autonomous Mode is **fully deactivated** — pause does not suspend-and-keep the configuration; it ends the mode:

1. **Stop immediately**: Do not finish the current step, stage, or any in-progress generation — halt within the current interaction. If a step was interrupted mid-way, park it first: run `engine.py park --note "<in-flight step, exact interruption point, next action>"` (see session-continuity.md Park Ritual) so it can be resumed cleanly from `resume_note`; never write breakpoint notes into `audit.md` or the engine-owned state region.
2. **Audit**: Log the pause trigger with complete raw input.
3. **Deactivate**: Update aidlc-state.md `## Autonomous Mode` → Enabled: No (keep Question Handling and Review Stages values for reference, per AM-08).
4. **Announce**: Autonomous Mode is off — subsequent stages use standard approval gates and the standard question flow; re-activation requires an explicit Activate intent (AM-01) and runs a fresh AM-02 (question handling and review stages are re-asked).
5. **Ask how to proceed** via the structured question tool:
   - **Option A**: 以标准模式继续当前工作（关卡照常等待你的确认）/ Continue the interrupted work in standard mode (gates wait for your approval as usual)
   - **Option B**: 立即重新激活自主模式（重新走 AM-02，重问问题处理方式与审核阶段）/ Re-activate Autonomous Mode now (runs a fresh AM-02 — question handling and review stages are re-asked)
6. Act on the choice: Option A continues under standard rules from the interruption point; Option B executes AM-02 in the same interaction. If the user answers the pause with free-form instructions instead of the menu, honor the instructions under standard mode (the mode is already off); an explicit Activate phrase re-runs AM-02.

## AM-06: Review Stage List

1. Stages named in the Review Stages list use the **standard approval gates**: present the completion message and WAIT for explicit approval per APG-01~05, exactly as if Autonomous Mode were off for that stage.
2. All stages NOT in the list continue under AM-03 auto-approval.
3. The list applies by stage name — for per-unit construction stages, a listed stage is reviewed for EVERY unit.
4. The list is set at activation (AM-02 Question 2) and may be changed mid-round only on the user's explicit request — the model never adds or removes review stages on its own (update per AM-08 and audit the change; the user may name stages by display name or slug via custom input). Changes take effect from the next gate encountered; already auto-approved stages are not revisited.
5. Question handling (AM-04) is independent of the review list: review stages still process question files per the configured mode.
6. **Display name vs. slug**: Review Stages are configured by stage name for human readability, but the runtime engine and its state use **slugs**. The display name is derived from the stage H1 (parenthetical modifiers are stripped), so it can drift; the slug is the file stem (kebab-case) and is the machine identifier. Resolve every name↔slug mapping authoritatively from `scripts/data/stage-graph.json` (compiled from each stage file's `slug` frontmatter field) — never guess from the display name. Whenever an engine command is involved (`report`, `jump`), always pass the slug.

## AM-07: Deactivation

On detecting a **Deactivate** intent (a Pause per AM-05 also ends the mode — AM-05 performs the same state flip itself):

1. Stop autonomous behavior immediately.
2. Update aidlc-state.md: `## Autonomous Mode` → Enabled: No (keep Question Handling and Review Stages values for reference, or clear them per user instruction).
3. Log deactivation in audit.md with complete raw input.
4. Confirm to the user: the workflow has returned to standard mode — all subsequent stages use standard approval gates and standard question flow.
5. Resume from the current point under standard rules. If a stage was auto-approved mid-flight and the user wants to re-review it, treat that as a normal change request for that stage.

## AM-08: State Persistence

**MANDATORY**: Maintain an `## Autonomous Mode` section in `aidlc-docs/aidlc-state.md`.

`aidlc-state.md` itself is created by the engine (`engine.py init`, see workspace-detection.md); the model owns and maintains the `## Autonomous Mode` section within it. On a new project, add the section with these defaults:

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

**Engine write window (AM-10)**: the engine may flip `Enabled` to `No` (and refresh an existing `Last Updated` line) at the two round boundaries — the completing transition and a re-entry jump — without model involvement. Never "restore" `Enabled: Yes` after an engine expiry; a live mode requires a fresh AM-02.

## AM-09: Session Resumption

When resuming an existing project (per `../../../common/session-continuity.md`):

1. Read the `## Autonomous Mode` section of aidlc-state.md along with the rest of the state file.
2. **If Enabled = Yes**: Autonomous Mode remains active — announce its status in the welcome-back summary (question-handling mode, review stages, last updated), and continue execution under AM rules without requiring re-activation.
3. **If Enabled = No or section missing**: Standard mode; AM rules dormant until a new AM-01 trigger.
4. **If the workflow is completed**: Autonomous Mode is expired (AM-10) — the section reads `Enabled: No`; announce standard mode. A stale `Enabled: Yes` in a pre-AM-10 completed workspace is treated as expired: flip it per AM-08 (auditing the expiry) before continuing a new round, including the plan-line self-revival path.
5. If the section is malformed, fall back to Enabled: No, note the recovery in audit.md, and continue in standard mode.

## AM-10: Round-Boundary Expiry

Autonomous Mode is scoped to the current workflow round. It ends at exactly three boundaries:

1. **Round completion (engine-enforced)**: the transition that completes the workflow — the final `report`, or a `jump` that leaves the workflow completed (e.g. a forward jump to an out-of-plan target past the last routed pending stage) — flips a live section to `Enabled: No` (Question Handling / Review Stages are kept for reference), the ack carries `autonomous_expired: true`, and the audit entry notes the expiry. In the SAME interaction as the closing summary (the `done` directive), announce that Autonomous Mode has ended with the round. After expiry these rules are dormant again — all AM rules are N/A until a new activation.
2. **Re-entry (engine-enforced self-heal)**: a `jump --stage` from the completed state — the sanctioned start of a new same-product round — performs the same flip, healing workspaces completed before AM-10 existed. **Plan-line self-revival path**: when a new round starts WITHOUT a jump (plan lines edited first, `status` re-activating the workflow — see `../../../common/workflow-changes.md`), no engine verb runs; the MODEL must ensure `Enabled: No` before continuing the round (flip the section per AM-08, audit the expiry, and announce it).
3. **Start Fresh / new project**: `jump --fresh` archives the whole `aidlc-docs/` directory — the section disappears with it, and a new project's state file starts section-less. Standard mode directly; there is no state to flip.

After ANY boundary, re-activation requires an explicit Activate intent (AM-01) and a fresh AM-02 — Question Handling is always re-asked, and the persisted Review Stages value serves only as the preselection for AM-02 Question 2; neither is ever silently reused. Mid-round persistence is unchanged: within the same round, sessions resume with Autonomous Mode active (AM-09).

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
| Workflow completion / re-entry / fresh | AM-10 |
| This file's own maintenance | DOC-05, AUD-04 (see workflow-conventions) |
