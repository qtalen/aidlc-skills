# Runtime Engine Contract

**Purpose**: Normative runtime rules for the AI-DLC orchestration engine (`<skill>/scripts/engine.py`). SKILL.md points here for engine invocation, directive handling, transition semantics, state ownership, and integrity. This file is loaded **on demand** — when the SKILL.md bootstrap table directs here (legacy state, integrity violation), before `jump`/`rebase`, or when an engine error or state-format dispute needs the authoritative answer. Routine operation needs only the compressed protocol in SKILL.md plus the engine's self-describing JSON output.

**Guiding principle**: **judgment belongs to the LLM, precision belongs to the tool, decisions belong to the human.**

---

## 1. Role — Who Owns What

The engine is the single authority for the workflow's deterministic mechanics.

| Concern | Owner | Notes |
|---|---|---|
| Cross-stage routing ("what runs next") | **Engine** | Only `next` decides. The model never routes from memory, from SKILL.md's stage blocks, or from plan prose |
| Stage state machine (pointer, checkboxes, completion) | **Engine** | Written only through `report` |
| Audit transition entries | **Engine** | The engine appends one entry per recorded transition |
| State integrity (drift detection) | **Engine** | State Digest + audit cross-check |
| Changing course (`jump`, Start Fresh) | **Engine** | The only sanctioned way to move the pointer |
| Stage `condition` prose (Execute-IF / Skip-IF) | **Model** | The engine NEVER parses `condition`. CONDITIONAL stages are emitted with `"conditional": true`; the model judges applicability |
| Scope recommendation, depth adaptation, requirement clarification, gate content/options | **Model** | Remains model judgment — unchanged by the engine |
| Approvals / "go or no-go" at a gate | **Human** | Never inferred, never auto-approved |

**Condition prose never enters the engine.** Because of this, a CONDITIONAL stage is always emitted as a `run-stage` directive with `"conditional": true`. When the model judges the stage does not apply, it records that judgment with `report --stage <slug> --result skipped --reason "<why>"`. A skip without `--reason` is rejected by the engine.

### Verb taxonomy (8 subcommands)

| Layer | Verbs | Mutates stage marks / current stage? |
|---|---|---|
| Read | `status`, `next`, `stamp` | No — pure reads (`stamp` reads nothing at all; it only prints the timestamp) |
| Transition | `report`, `jump` | **Yes — the only verbs that change marks or the pointer** (a closed set) |
| Lifecycle | `init`, `park`, `rebase` | No — `init` only creates; `park` is an annotation sub-kind; `rebase` re-renders the region without changing marks or current |

**Transition-invariance law**: annotation verbs (`park`, and `rebase`'s digest re-render) MUST leave the stage marks and the current stage unchanged. Only `report` and `jump` may alter them.

---

## 2. Invocation and Bootstrap Probe

### Calling convention

```
python <skill>/scripts/engine.py <subcommand> [--workspace <path>]
```

- `<skill>` is the absolute path of this skill's directory (the directory containing `SKILL.md`).
- `--workspace <path>` overrides the workspace root; it defaults to the current working directory.
- Python **3.8+** is required. The engine uses only the standard library and ships with the skill — users install nothing.
- Every subcommand prints **exactly one JSON object to stdout** and nothing else. Parse that object; do not parse logs, stderr, or other side channels.
- Every printed JSON object — successful output and `error` objects alike — carries a `timestamp` field: ISO 8601 UTC at second precision (e.g. `2026-09-15T05:40:00Z`), taken at output time. Use it directly as the timestamp source for `audit.md` entries in the same interaction; no separate clock reading is needed. When an interaction needs the engine's clock but no other subcommand, `engine.py stamp` prints exactly this timestamp with zero side effects — it reads nothing and writes nothing (no state, no audit, no handoff).

### Bootstrap probe (before ANY workflow action)

1. Run `python <skill>/scripts/engine.py status`.
2. If step 1 fails because the `python` command is unavailable, retry with `python3 <skill>/scripts/engine.py status`.

This probe is mandatory for every software development request. `status` is both the liveness probe and the session-recovery data source.

### HARD STOP on probe failure

If **both** commands fail (no Python 3.8+ interpreter is available), the workflow MUST NOT start. Stop immediately, ask no workflow questions, and produce no artifacts. Present this installation guidance:

> **Python 3.8+ is required to run the AI-DLC workflow engine, and no interpreter was found.**
>
> Install it using either path, then retry:
>
> - **Official installer**: https://www.python.org/downloads/ — install Python 3.8 or newer. On Windows, check **"Add Python to PATH"** during setup.
> - **Platform package manager**:
>   - Windows: `winget install Python.Python.3`
>   - macOS: `brew install python`
>   - Debian/Ubuntu: `sudo apt install python3`
>
> Once installed, re-run the bootstrap probe. The workflow will not proceed until the probe succeeds.

---

## 3. Orchestration Loop

Cross-stage progression is a loop driven entirely by engine directives:

```
Bootstrap probe (status)
      |
      v
+--> engine.py next
|         |
|         v
|    directive.kind
|     ├─ run-stage → load directive.stage_file (relative to <skill>), execute that stage's rules
|     ├─ done      → workflow complete; present the closing summary and STOP
|     └─ error     → present directive.message + directive.hint verbatim; STOP
|         |
|         v
|    write the outcome through the ONLY transition entry point:
|     engine.py report --stage <slug> --result <completed|approved|rejected|revised|skipped> [--reason]
|         |
+---------+ (repeat)
```

Rules:

- The model MUST NOT decide "the next stage" from memory, from this file's stage blocks, or from any plan document. Only `next` routes.
- For a `run-stage` directive whose gate is not `none`, the stage's approval gate runs to completion (or revision) before `report` is called — see the transition matrix below.
- `next_stage` inside a `run-stage` directive is a prediction ("the stage that would follow if this one completed") and is **presentation-only**. It is never a routing input.
- The loop ends on `done`. There is no implicit "proceed to the next phase" behavior.

---

## 4. Directive Consumption Contract

`next` returns exactly one of three directive kinds.

| `kind` | Required action |
|---|---|
| `run-stage` | Load `stage_file` and execute the stage's rules. |
| `done` | The workflow is complete. Present the closing summary and stop. |
| `error` | Present `message` and `hint` to the user verbatim, then stop. |

MUST:

- On `error`, **present `message` and `hint` as-is** and halt. Do not invent a workaround, and do not advance the workflow.
- **Never fabricate a `report`.** A transition may be recorded only after the corresponding stage outcome actually happened (completion, user approval, gate rejection, revision, or a justified conditional skip).
- **Abandoning a directive means discarding it.** If a `run-stage` directive is not going to be executed (for example, the user redirects the conversation before the stage starts), simply drop it and do not call `report` for it. `next` will re-emit it on the next loop iteration.

**Backward-compatibility clause**: **Consumers MUST ignore unknown fields** in any directive or status object. New fields may be added by future engine versions; ignoring them is what keeps older skills forward-compatible. Never fail or branch on the presence of an unrecognized key.

---

## 5. Transition Semantics (`report`)

`report` is the **only** entry point that writes a stage transition. It atomically updates the state file and appends an audit transition entry.

```
engine.py report --stage <slug> --result <r> [--reason "<text>"]
```

| `result` | Checkbox | Pointer | Applies to |
|---|---|---|---|
| `completed` | `[x]` | advance | A non-gated stage finished normally |
| `approved` | `[x]` | advance | A gated stage the user approved |
| `rejected` | `[R]` | stays on this stage | The user rejected the gate |
| `revised` | `[?]` | stays on this stage | Re-submitted after a revision cycle |
| `skipped` | `[S]` | advance | Only a CONDITIONAL stage judged inapplicable, or a planned SKIP. `--reason` is required |

Usage notes:

- **`completed`** — use for stages with `gate: none` (e.g. Workspace Detection).
- **`approved`** — use for gated stages (`approve-continue` or `two-option`) after the human explicitly approves. The gate options and NO EMERGENT BEHAVIOR discipline are unchanged; the engine only records the outcome.
- **`rejected`** — use when the human requests changes at the gate. The pointer stays on the current stage so it can be revised and re-presented.
- **`revised`** — use after performing a revision cycle and re-submitting the stage output. The pointer stays on the current stage.
- **`skipped`** — use only for a CONDITIONAL stage the model judged not applicable (per its Execute-IF / Skip-IF prose), or a stage the plan marked SKIP. Always supply `--reason`; the engine rejects a reasonless skip.

---

## 5.5 Park Semantics (`park`)

`park` records an in-flight annotation — it is **never a transition**. It lets an interrupted session leave a human-readable "what was in flight" note without advancing, rewinding, or re-marking anything.

```
engine.py park --note "<what is in flight, the next step, and any caveats>"
```

- **`--note` is required.** Newlines in the note are folded to `"; "` and it is truncated to 300 characters. A note left empty by sanitization is a usage error.
- **Same gate as other mutating verbs**: the state file must exist and be engine-owned, and integrity must pass (the digest check runs before any write).
- **A completed workflow cannot park.** With no current stage remaining, `park` fails with error code `workflow-complete`.
- **Effects — exactly two writes:**
  1. The `## Current Status` section of the engine region gains `- **Last Parked**: <slug> — <note>`. The line sits inside the State Digest; marks and current stage are untouched (transition-invariance, §1).
  2. A park entry is appended to `aidlc-docs/handoff.md` (created lazily with a fixed header). The file is append-only, engine-exclusive to write, and the integrity machinery never parses it.
- **Write order is fixed: region first, handoff second.** The region line is the authoritative source (`status` → `resume_note` reads it). A crash between the two writes leaves the handoff file one historical entry short; recovery is unaffected.
- **Dedup**: if the handoff file's last park entry already holds the same (stage, note), the append is skipped (`handoff_appended: false`).
- **Cleared by transitions**: `report`, `jump --stage`, and `jump --fresh` empty the parked note (a transition supersedes what was in flight); `rebase` preserves it.
- **Concurrency**: last-writer-wins on the region, and a duplicated handoff history, is acceptable — neither corrupts anything.
- **Degradation**: an older engine re-rendering the region silently drops the `Last Parked` line and remains digest-consistent; `jump --fresh` archives `handoff.md` together with the whole `aidlc-docs/` directory.
- **No audit entry**: `park` never appends to `audit.md` (engine audit writes are transition entries only — see §6).

---

## 6. State File Partition Ownership

`aidlc-docs/aidlc-state.md` is partitioned. Two parties write it, but each owns disjoint regions. The engine-owned region is delimited by the `ENGINE-STATE` markers.

| Region of the state file | Writer | Covered by State Digest |
|---|---|---|
| Stage Progress checkboxes, Current Status, State Digest, Unit Progress (reserved) — i.e. everything inside the `ENGINE-STATE` marker region | **Engine-exclusive** | ✅ |
| Project Information, Workspace State, Code Location Rules, Extension Configuration, Autonomous Mode, Execution Plan Summary | **Model**, per template | ❌ |

The engine reads `Scope`/`Depth` and the plan lists **only** from the `## Execution Plan Summary` section; copies elsewhere (e.g. under `## Project Information`) are informational and have no routing effect.

Discipline:

- The model **MUST NOT hand-edit** the engine-owned region (the `ENGINE-STATE` marker region) — its checkboxes, Current Status (including the `Last Parked` line), State Digest, or Unit Progress. All changes there flow through engine verbs: transitions via `report` and `jump`, the annotation via `park`, re-baselining via `rebase`. Beyond the transition verbs, none of these may move a checkbox or the pointer — `park` and `rebase` rewrite the region while keeping marks and current unchanged (transition-invariance, §1).
- The model maintains the model-owned regions normally, following the templates in the stage rules.
- **Engine writes to `audit.md` are narrowed to transition entries.** The engine appends one entry per recorded transition only — `park` writes no audit entry. **User input records in `audit.md` remain model-owned**: the model is the sole visible source of user input, and the model's CTX phase summaries are unchanged. Never let an engine transition entry substitute for logging the user's raw input.
- **The `Last Parked` line (inside the engine region) and `aidlc-docs/handoff.md` are engine-exclusive.** The model never writes or reformats either (§5.5).

**Execution Plan Summary is a load-bearing channel.** After the Workflow Planning gate is approved, the model writes the coverage decision as structured lines in the Execution Plan Summary region of the state file:

```markdown
- **Scope**: classic
- **Depth**: standard
- **Stages to Execute**: workspace-detection, requirements-analysis, workflow-planning, code-generation, build-and-test
- **Stages to Skip**: user-stories (no user-facing change), infrastructure-design (no infra changes)
```

The engine **reads** these lines to filter routing (`Scope`/`Depth` gate the scope matrix; the Execute/Skip lists override it). The model **writes** them; the engine never writes this region.

Format note on the `(reason)` annotation: the parenthesised reason on a Skip line is optional, and it **may contain English commas** — the parser reassembles comma-split fragments against the known slug registry, so a reason such as `(deferred, no user-facing change)` no longer produces an "unknown stage slug" error. Keep reasons short regardless; commas are tolerated, not an invitation to write prose.

Precedence rules (deterministic):

1. A slug in `Stages to Skip` is always out — **Skip wins over Execute** and can even exclude an `ALWAYS` stage (the human approved that plan at the Workflow Planning gate).
2. A slug in `Stages to Execute` is in, even if the active scope marks it SKIP (the add-back channel).
3. Otherwise the scope matrix decides: EXECUTE/CONDITIONAL stages are routed, SKIP stages are not.
4. A `Stages to Execute` line still containing its `[placeholder]` brackets is treated as "not yet written" — that line alone falls back to rule 3; a filled `Stages to Skip` line still applies.

The section header must be exactly `## Execution Plan Summary`. Plan consumption is load-bearing, so a renamed or mistyped header is **detected, not silent**: if the engine finds a filled `Stages to Execute` / `Stages to Skip` line anywhere in the file while the exact header is absent, it returns an `error` directive with code `plan-invalid` (routing cannot consume those lines) and the hint restores the exact header. When the exact header **is** present, copies of these lines elsewhere are informational and have no routing effect. Do not rename it.

---

## 7. Integrity (State Digest)

The engine-owned region is protected by a **State Digest**: a SHA-256 over that region only. Every read verifies the digest, and the engine also cross-checks the stage checkboxes against the audit transition entries.

- **Scope**: the digest covers the engine-owned region exclusively. Changes to model-owned regions (Project Information, Workspace State, Execution Plan Summary, extension config, audit user-input entries, etc.) **do not** trigger drift. This is intentional — those regions have legitimate model authorship.
- **On drift** (digest mismatch or audit cross-check inconsistency): the engine returns an `error` directive and halts. The model presents the drift and stops; normal workflow work does not continue. After explicit human confirmation, run `rebase` to re-baseline the digest.
- **Detection is non-blocking — an honest boundary.** There are no hooks in a harness-agnostic skill, so the engine cannot intercept a model's Write/Edit calls. Drift is *detected*, not *prevented*. The threat model is **model oversight or shortcut-taking, not an adversary**: the integrity check exists to catch accidental or lazy hand-edits, not to defeat a determined actor. The corresponding discipline is prompt-level: never hand-edit the engine-owned region.
- **`jump` and integrity are complementary.** Because every legitimate change of course flows through `jump`, the integrity check should not be the thing that surfaces ordinary "I changed my mind" requests.

---

## 8. Jump and Start Fresh

`jump` is the sanctioned channel for the human changing course. It moves the pointer as a first-class engine operation (with an audit entry) instead of leaving the model to hand-edit checkboxes.

```
engine.py jump --stage <slug>
engine.py jump --fresh
```

- **Backward (redo)**: jumping to an earlier stage resets the target stage **and every stage after it** back to `[ ]`.
- **Forward**: jumping past stages that have not executed marks the skipped intermediates as `[S]`.
- A `STAGE_JUMPED` audit entry is recorded.
- **`jump --fresh`** is Start Fresh: it archives `aidlc-docs/` to `aidlc-docs-archive-<timestamp>/` and resets state. It is the execution path behind the resume menu's "Start Fresh" option.

When to jump: a user asks to redo, revisit, reorder, or skip ahead — any deliberate deviation from the routed plan. Use `jump` rather than editing stage checkboxes by hand.

---

## 9. Subcommand Reference

| Subcommand | Mutates state? | Purpose |
|---|---|---|
| `status` | No | Bootstrap probe + session-recovery data source. Returns `state`, `scope`, `depth`, `current_stage`, `last_completed`, `integrity`, `completed`, `remaining`, plus the recovery keys `resume_note` (+ `note_age_seconds`), `recent_events`, `audit_entries`, `audit_bytes`, `artifact_alerts`, `alerts_unavailable`, `autonomous` (active/completed states only — see §10). |
| `init` | Yes (create) | Deterministically create `aidlc-docs/aidlc-state.md` (model-region placeholders + `ENGINE-STATE` region: the 14-stage slug checklist, Current Status, reserved Unit Progress, State Digest) and the `audit.md` header. Errors if the state file already exists. |
| `next` | No | Pure-read routing. Returns exactly one directive: `run-stage`, `done`, or `error`. |
| `report` | Yes | The only transition entry point. `--stage <slug> --result <r> [--reason]`. See §5. |
| `park` | Yes (annotation) | Park in-flight work. `--note <text>` required. Writes the `Last Parked` line into Current Status (inside the digest) and appends to `aidlc-docs/handoff.md`; marks, current stage, and the audit log are untouched. See §5.5. |
| `jump` | Yes | Change course. `--stage <slug>` (redo/forward) or `--fresh` (Start Fresh). See §8. |
| `rebase` | Yes | After human confirmation of a detected drift, re-baseline the State Digest. See §7. |
| `stamp` | No | Print the authoritative engine timestamp. Zero side effect: reads nothing, writes nothing. Use it when an interaction needs the engine's clock but no other subcommand. See §2. |

Consumers must ignore unknown fields in any output (see §4).

---

## 10. Output Samples

### `status` (active)

```json
{
  "engine": "ok",
  "timestamp": "2026-09-15T05:40:00Z",
  "state_version": 1,
  "workspace": "D:/projects/payments",
  "state": "active",
  "current_stage": "workflow-planning",
  "scope": "classic",
  "depth": "standard",
  "last_completed": "requirements-analysis",
  "integrity": "ok",
  "completed": ["workspace-detection", "requirements-analysis"],
  "remaining": ["workflow-planning", "application-design", "units-generation", "functional-design", "nfr-requirements", "nfr-design", "infrastructure-design", "code-generation", "build-and-test"],
  "resume_note": null,
  "autonomous": null,
  "note_age_seconds": null,
  "recent_events": [
    {"event": "STAGE_COMPLETED", "stage": "workspace-detection", "reason": "-", "timestamp": "2026-09-15T05:36:10Z"},
    {"event": "STAGE_APPROVED", "stage": "requirements-analysis", "reason": "-", "timestamp": "2026-09-15T05:39:44Z"}
  ],
  "audit_entries": 3,
  "audit_bytes": 546,
  "artifact_alerts": [],
  "alerts_unavailable": false
}
```

`state` is one of `none` (no state file), `active` (in progress), `completed` (all applicable stages done), `legacy` (a state file exists that predates the engine and has no `ENGINE-STATE` region; do not silently adopt or overwrite it — present the situation, obtain explicit confirmation, and follow the engine's hint before creating engine-owned state), or `corrupt` (the `ENGINE-STATE` marker region is present but incomplete or malformed — e.g. truncated, or a marker line deleted; `integrity` reports `violated` and mutating commands fail with error code `state-corrupt`. Restore the missing marker line from a backup if available — the END line is exactly `<!-- END ENGINE-STATE -->`; otherwise obtain explicit user confirmation and Start Fresh with `jump --fresh`). `current_stage` and `last_completed` are `null` when not applicable. `integrity` is `ok` or `violated`.

**Recovery keys.** The `active` and `completed` states additionally carry:

- `resume_note` — `{stage, note}` when the workflow is parked (the `Last Parked` region line is authoritative), else `null`. Cleared by any `report`/`jump`; preserved by `rebase` (§5.5).
- `note_age_seconds` — age in seconds (`int`) of the current park note, taken from the `**Timestamp**` of the corresponding `handoff.md` entry; `null` when there is no parked note or that timestamp is missing/unparseable. An objective number only — judging staleness stays with the model; negative deltas (clock skew) clamp to 0.
- `autonomous` — parsed from the model-owned `## Autonomous Mode` section (a model-writes-engine-reads channel, like Execution Plan Summary): `{enabled, question_handling, review_stages, last_updated}`; `null` when the section is missing or malformed (no `Enabled` line, or a value other than `Yes`/`No` — treat that as "read the section yourself and apply AM-09"). The section's ownership and digest status are unchanged.
- `recent_events` — the last 5 engine transition entries as `{event, stage, reason, timestamp}`. Parsed **only** from `## Engine Transition` sections of `audit.md`, so model-owned audit entries (which may quote Event-shaped lines) can never forge recovery data; an entry's timestamp is the last `**Timestamp**` line within its section.
- `audit_entries` / `audit_bytes` — count and byte size of the audit transition log; the measurements feeding the audit-partitioning contingency (512 KB scale). `audit_entries` counts **engine transition entries only** (model-side entries are not counted); the engine only measures — it never splits the file.
- `artifact_alerts` — sensor findings, five fixed fields each (shape below).
- `alerts_unavailable` — `true` only when the sensor probe itself failed unexpectedly (fail-open: it arrives with an empty `artifact_alerts` array, and the probe never blocks).

The early-exit branches (`none`, `legacy`, `corrupt`) return **only** the base keys shown in the sample above — none of the recovery keys appear on them (`legacy` and `corrupt` additionally carry their pre-existing diagnostic `hint` field). When `integrity` is `violated`, the artifact sensors still run and `artifact_alerts` is still computed.

**Finding shape** — every `artifact_alerts[]` entry is exactly `{type, severity, subject, message, action_discipline}`. The `type` set may grow in future engine versions but never shrinks, and within a given `state_version` the shape never changes destructively (consumers ignore unknown fields, §4):

```json
{
  "type": "missing-produces",
  "severity": "warning",
  "subject": "requirements-analysis",
  "message": "Completed stage 'requirements-analysis' is missing ALL of its declared concrete produces: aidlc-docs/inception/requirements/requirements.md, aidlc-docs/inception/requirements/requirement-verification-questions.md. Either the artifacts were lost or the stage was reported without producing them.",
  "action_discipline": "Report to the user; do not regenerate or fabricate artifacts."
}
```

```json
{
  "type": "resumed-artifacts",
  "severity": "info",
  "subject": "reverse-engineering",
  "message": "Files the current stage 'reverse-engineering' will produce already exist (possible half-done work from an interrupted session): aidlc-docs/inception/reverse-engineering/tech-stack.md.",
  "action_discipline": "Read existing files before writing; append rather than regenerate (unless in a rejected/revised redo — see session-continuity)."
}
```

- **`missing-produces` (warning)** — fires for a *completed* stage only when it declares **N ≥ 2 concrete produces** (no wildcards, and excluding the engine's own `aidlc-state.md`/`audit.md`) and **all** of them are missing or empty on disk. Stages with 0–1 concrete produces are exempt.
- **`resumed-artifacts` (info)** — fires for the *current* stage when any declared produce already exists on disk. `{unit-name}` templates are globbed as `*` and any single match counts; the path list is capped at 5; engine-owned files are excluded.
- **`checkpoint-missing` (warning)** — fires only when the model-owned `## Extension Configuration` table marks the Context Checkpointing (CTX) extension **Enabled** (a missing or malformed table means not enabled — nothing is checked). Two global CTX-01 anchors: every effective inception stage is done → `aidlc-docs/checkpoints/inception-checkpoint.md` must exist; `build-and-test` is done → `aidlc-docs/checkpoints/construction-checkpoint.md` must exist. Per-unit anchors are a Phase 4 item (they need the Unit Progress region).

```json
{
  "type": "checkpoint-missing",
  "severity": "warning",
  "subject": "inception",
  "message": "The Context Checkpointing extension is enabled and the inception checkpoint anchor is reached, but aidlc-docs/checkpoints/inception-checkpoint.md is missing or empty (CTX-01 phase checkpoint).",
  "action_discipline": "Report to the user; do not fabricate the checkpoint to silence this alert."
}
```

### `next` → `run-stage`

```json
{
  "kind": "run-stage",
  "timestamp": "2026-09-15T05:40:00Z",
  "stage": "requirements-analysis",
  "name": "Requirements Analysis",
  "phase": "inception",
  "gate": "approve-continue",
  "stage_file": "references/inception/requirements-analysis.md",
  "produces": ["inception/requirements/requirements.md", "inception/requirements/requirement-verification-questions.md"],
  "consumes": [
    {"artifact": "inception/reverse-engineering/*", "required": true, "conditional_on": "brownfield"}
  ],
  "conditional": false,
  "next_stage": "user-stories"
}
```

Each `consumes` entry has `artifact` (path/glob, relative to `aidlc-docs/`), `required` (boolean), and `conditional_on` (a condition label such as `"brownfield"`, or `null`).

The semantics of `consumes[].required` are defined by stage-contract.md §2: its scope is the **active plan**, so a scope or plan that skips the producing stage renders that consume moot. The engine emits the static contract as-is and never filters `consumes` by plan; judging applicability is the model's job.

### `next` → `done`

```json
{"kind": "done", "timestamp": "2026-09-15T05:40:00Z"}
```

### `next` → `error`

```json
{
  "kind": "error",
  "timestamp": "2026-09-15T05:40:00Z",
  "code": "integrity-violated",
  "message": "The engine-owned region of aidlc-state.md does not match its State Digest. (hand-edit detected)",
  "hint": "Do not continue. Show this to the user, get explicit confirmation, then run: python <skill>/scripts/engine.py rebase"
}
```

`code` is a stable, machine-readable category; `message` is human-readable; `hint` is a remediation instruction. Present `message` and `hint` verbatim and stop.

The same `error` shape covers mutating-verb failures, e.g. parking a completed workflow:

```json
{
  "kind": "error",
  "code": "workflow-complete",
  "message": "The workflow is complete; there is no in-flight work to park.",
  "hint": "To restart, use: python <skill>/scripts/engine.py jump --fresh",
  "timestamp": "2026-09-15T05:40:00Z"
}
```

### `stamp`

```json
{
  "engine": "ok",
  "kind": "stamp",
  "timestamp": "2026-09-15T05:40:00Z"
}
```

Zero side effect: `stamp` reads nothing and writes nothing (no state, no audit, no handoff). It exists so an audit entry can carry the engine's clock even in an interaction that runs no other engine subcommand.

### Write subcommands

`init`, `report`, `park`, `jump`, and `rebase` print a JSON acknowledgment object on success. Treat a `kind: "error"` object (or a non-zero exit status) as failure; otherwise the operation succeeded. Unknown fields in the acknowledgment must be ignored.

A `park` acknowledgment:

```json
{
  "kind": "parked",
  "stage": "workflow-planning",
  "note": "Mid requirements interview; next: confirm NFR scope with user",
  "handoff_file": "aidlc-docs/handoff.md",
  "handoff_appended": true,
  "timestamp": "2026-09-15T05:40:00Z"
}
```

`handoff_appended` is `false` when the handoff file's last entry already holds the same (stage, note) — dedup, §5.5.

A `report` acknowledgment may carry a soft, non-blocking `produces_missing` warning. It appears only for `completed`/`approved` (`rejected`/`revised`/`skipped` are not checked); the check is fail-open and never blocks the transition:

```json
{
  "kind": "reported",
  "stage": "requirements-analysis",
  "result": "approved",
  "current_stage": "user-stories",
  "produces_missing": [
    "aidlc-docs/inception/requirements/requirements.md",
    "aidlc-docs/inception/requirements/requirement-verification-questions.md"
  ],
  "timestamp": "2026-09-15T05:40:00Z"
}
```
