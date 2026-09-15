# Workflow Conventions Rules

## Overview

MANDATORY cross-cutting rules for every AI-DLC workflow execution. This file has no `.opt-in.md` — it is ALWAYS enforced and loaded at workflow start. It consolidates four rule groups:

- **DOC-01~05** Documentation Consistency — keep aidlc-docs artifacts synchronized with code after every change
- **APG-01~05** Approval Gate Semantics — how user responses at stage approval gates are classified and handled
- **AUD-01~04** Audit Attribution — authorship fields on audit.md entries
- **QT-01~04** Question Tool Flow — after generating a question file, collect answers via the `question` tool, write them back to the file, then proceed

**Enforcement**: At each applicable stage/gate, and after every change request, verify compliance with the applicable rules BEFORE presenting the completion message. Include a compliance summary (compliant / non-compliant / N/A per rule, with brief rationale for N/A).

### Blocking Finding Behavior (applies to all groups)

A **blocking finding** means:
1. List the finding in the stage completion message with rule ID and description
2. Do NOT present "Continue to Next Stage" until resolved (present only "Request Changes" with explanation; for APG/AUD violations, correct the handling/entry first)
3. Log the finding in `aidlc-docs/audit.md` with rule ID, description, and stage context

All rules are **blocking** by default. Rules not applicable to the current stage/change are marked N/A (not a finding).

---

## Group 1: Documentation Consistency (DOC)

### DOC-01: Change-to-Artifact Impact Analysis
After any approved change (new/modified requirement, UI tweak, signature/enum/value-range change), BEFORE the completion message:
1. List affected keywords, numeric ranges, type signatures, component names, counts
2. Search the entire `aidlc-docs/` tree for occurrences of those terms (including superseded values)
3. Update every artifact containing stale references, marking the change origin where the artifact format supports it. When the Context Checkpointing extension is enabled, this sweep includes checkpoint files under `aidlc-docs/checkpoints/` — they are current-state artifacts, not historical records (see CTX-01), so in-place updates to stale checkpoint content are required and do not violate DOC-04

Typical mapping: functionality → requirements/stories/business rules; enums/ranges → domain entities, logic models, component methods; signatures → component methods, interaction flows; new components → inventories, structure trees, summaries; test counts → summary coverage sections.

**Verification**: grep of `aidlc-docs/` shows no stale pre-change values in maintained artifacts; new concepts appear in every artifact enumerating that category; cross-reference/coverage tables include changed items.

### DOC-02: Same-Interaction Plan Tracking
Every change request — including small fixes and visual tweaks — MUST be appended as a step to the relevant stage plan file and marked `[x]` in the SAME interaction where the work completes.

**Verification**: plan file contains the step with story/requirement traceability, checked in the same interaction; no completed code change exists without a checked plan step.

### DOC-03: Documentation Gate in Completion Verification
Completion verification MUST include the DOC-01 sweep in addition to code-level verification (compile/lint/test/build). Code-green is not completion-green. Results stated in summaries must reflect the latest run (current test counts, not copied values).

### DOC-04: Historical Records Are Append-Only
Question-and-answer files, clarification sections of plan files, and `audit.md` entries MUST NOT be retroactively rewritten. Corrections and new decisions are appended as new timestamped entries.

**Verification**: no historical Q&A answer or audit entry edited in place; superseded decisions followed by newer timestamped entries.

### DOC-05: Generic Artifacts, No Cross-Project Leakage
Shared workflow rule files MUST contain no project-specific identifiers (project names, requirement/story numbering from one project). Project-specific content belongs in the project's `aidlc-docs/`, never in shared rules.

---

## Group 2: Approval Gate Semantics (APG)

Stage completion messages keep their standardized two-option templates unchanged — this group is an interpretation layer for the user's free-form response.

**Autonomous Mode override**: When Autonomous Mode is active (see `../autonomous-mode/autonomous-mode.md`), AM-03 suspends APG-01~04 waiting behavior for stages NOT in the Review Stages list; stages in the Review Stages list follow APG-01~05 normally. APG-05 always applies.

### APG-01: Approval Intent Classification
At every approval gate, classify the user's reply into exactly one intent BEFORE acting:

| Intent | Trigger semantics | Examples (non-exhaustive) |
|---|---|---|
| Approve-and-Hold | Approval ONLY, no continuation signal | "approve", "approved", "ok", "okay", "yes", "lgtm", "同意", "批准", "好的", "可以", "没问题" |
| Approve-and-Continue | Continuation (implies approval) | "continue", "go on", "next", "proceed", "继续", "继续吧", "下一步", "接着来", "往下走" |
| Request Changes | Any modification/question/correction | existing behavior per stage rules |

- Approval + unrelated extra instruction (e.g., "批准但不要进入下一步，只提交代码") → **Approve-and-Hold**; execute ONLY the explicit instruction, then ask about continuation.
- Genuinely ambiguous between hold/continue → **Approve-and-Hold** (never auto-start next-stage work on ambiguity).

**Verification**: every approval response logged in audit.md with classified intent; no next-stage work begins on a hold; ambiguity defaults to hold.

### APG-02: Approve-and-Hold Behavior
On Approve-and-Hold, in the SAME interaction:
1. Record the stage transition with the engine: `python <skill>/scripts/engine.py report --stage <slug> --result approved` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-docs/aidlc-state.md` — they are engine-owned; the "awaiting continuation" hold is a behavior state, not a hand-written status
2. Log approval in audit.md with complete raw input and intent "approve-hold"
3. Do NOT begin any next-stage work (no artifacts, no plans, no execution)
4. End the reply with an explicit continuation question naming the exact next stage

### APG-03: Approve-and-Continue Behavior
On Approve-and-Continue: treat exactly as the standard "Approve & Continue" option — record the transition with the engine (`python <skill>/scripts/engine.py report --stage <slug> --result approved`), log with intent "approve-continue", immediately proceed in the same interaction.

### APG-04: Resume from Hold
- A continuation signal at a held gate proceeds to the recorded next stage WITHOUT re-approval (the approval transition was already recorded through the engine at hold time); log the resumption in `audit.md` — never hand-edit the engine-owned state region.
- New instructions (e.g., change requests) at a held gate are handled while the gate stays held until an explicit continuation signal.

**Verification**: resuming never re-asks approval; state file never shows a held gate after the next stage started; intervening requests don't lose the hold state.

### APG-05: No Template Modification
Completion message templates and the "NO EMERGENT BEHAVIOR" constraint remain exactly as defined in stage rule files. Never add a third visible option; hold/continue is expressed through the user's natural-language response.

---

## Group 3: Audit Attribution (AUD)

### AUD-01: Authorship Fields on Every New Entry
Every NEW entry appended to `aidlc-docs/audit.md` MUST include these two lines immediately after the `**Context**` line:

```markdown
**User**: [resolved git user.name]
**Email**: [resolved git user.email]
```

Applies to ALL entry types, including automated `[No user input]` entries.

### AUD-02: Value Resolution from Git Configuration
Resolve dynamically, never hardcoded:
1. Run `git config user.name` and `git config user.email` in the workspace repository (local config takes precedence automatically)
2. Unresolvable (no git / not a repo / key unset) → write `unknown`, never block the workflow
3. Resolve ONCE per session at workflow start (or session resumption) and cache in memory for all subsequent audit writes in that session; re-resolve during the session ONLY if the initial resolution failed. NEVER cache across sessions

### Timestamp Acquisition
- Preferred source: the `timestamp` field carried by the output JSON of any engine subcommand run in the SAME interaction (`status`, `next`, `init`, `report`, `jump`, `rebase` — successes and errors alike). This costs zero extra commands: reuse the value the engine already printed
- Fallback ONLY when that interaction invoked no engine subcommand at all: the harness environment provides only the current date, not a clock — obtain the full ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ) from the system clock (e.g. a `python -c` one-liner on Windows cmd)
- ONE timestamp acquisition per interaction suffices: multiple audit entries written in the same interaction MAY share it
- Batch the fallback acquisition with the AUD-02 git config resolution in a single command at workflow start

### AUD-03: Historical Entries Untouched
Applies only to entries created after adoption; existing entries MUST NOT be retroactively edited (aligns with DOC-04).

### AUD-04: Generic Rule Text
This rule file MUST NOT contain any real person's name or email — placeholders and resolution instructions only.

---

## Group 4: Question Tool Flow (QT)

Applies to every `{phase-name}-questions.md` file (including `-clarification-questions.md` variants) created under `aidlc-docs/`. Does NOT apply to stage completion approval gates — those remain in-chat, template-bound, per APG-05.

**Autonomous Mode override**: When Autonomous Mode is active with question handling `auto-recommended` (see `../autonomous-mode/autonomous-mode.md` AM-04), QT-01's tool-based collection is suspended — the AI selects recommended answers and writes them back with attribution. Modes `manual` and custom follow QT-01~04 normally.

### QT-01: Immediate Question Tool Invocation
After creating a question file, call the `question` tool with the file's questions in the SAME interaction. Do NOT stop and wait for the user to manually edit the file.

Mapping rules:
- Each markdown question → one tool entry: question text → `question`; short topic (e.g., "Q3 Database") → `header` (≤30 chars).
- Options A/B/C/... → `options` array: condensed 1-5 word `label`, full option text in `description`.
- Do NOT add an explicit "Other" option — the tool's built-in custom input covers it.
- If a recommended option exists, place it first with "(Recommended)" in its label.
- Single-choice questions use `multiple: false`; multi-select questions use `multiple: true`.

**Verification**: no question file is left with "fill in the file and let me know when you're done" as the stopping point; the tool is invoked in the same interaction as file creation.

### QT-02: Answer Write-Back
Write the tool's answers back into the question file immediately: fill the matching letter after each `[Answer]:` tag (e.g., `[Answer]: C`). For custom answers, write the "Other" option's letter plus the user's verbatim custom text. Question text and option lists MUST NOT be altered during write-back (aligns with DOC-04).

Do the write-back with the `Edit` tool, anchoring each edit on a unique context string that contains the question title or the adjacent option text in the same block, so that each `[Answer]:` line is matched unambiguously. Do NOT generate a temporary script file to perform the write-back.

### QT-03: Proceed Without Manual Confirmation
After write-back, run the standard validation from `question-format-guide.md` (completeness check + contradiction/ambiguity detection) and proceed to the next step directly — do NOT wait for the user to say "done". If validation produces clarification questions, the clarification file also follows QT-01.

### QT-04: Tool Fallback
If the `question` tool is unavailable, errors out, or returns without answers, fall back to the base manual flow (inform the user, wait for completion confirmation per `question-format-guide.md`) and note the fallback in `aidlc-docs/audit.md`.

---

## Enforcement Integration

| Context | Applicable Rules |
|---|---|
| Every stage completion + every change request | DOC-01, DOC-02, DOC-03 |
| Historical record handling | DOC-04 |
| Shared rule file edits | DOC-05 |
| Every approval gate (all stages, inception + construction) | APG-01 ~ APG-05 |
| Every audit.md write | AUD-01, AUD-02, AUD-03 |
| Every question file creation (requirements, stories, design, clarification) | QT-01 ~ QT-04 |
| Autonomous Mode trigger / gates / questions / pause / resume | AM-01 ~ AM-09 (see `../autonomous-mode/autonomous-mode.md`) |
| This file's own maintenance | DOC-05, AUD-04 |
