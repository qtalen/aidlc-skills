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
- Every printed JSON object — successful output and `error` objects alike — carries a `timestamp` field: ISO 8601 UTC at second precision (e.g. `2026-09-15T05:40:00Z`), taken at output time. Use it directly as the timestamp source for `audit.md` entries in the same interaction; no separate clock reading is needed.

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

## 6. State File Partition Ownership

`aidlc-docs/aidlc-state.md` is partitioned. Two parties write it, but each owns disjoint regions. The engine-owned region is delimited by the `ENGINE-STATE` markers.

| Region of the state file | Writer | Covered by State Digest |
|---|---|---|
| Stage Progress checkboxes, Current Status, State Digest, Unit Progress (reserved) — i.e. everything inside the `ENGINE-STATE` marker region | **Engine-exclusive** | ✅ |
| Project Information, Workspace State, Code Location Rules, Extension Configuration, Autonomous Mode, Execution Plan Summary | **Model**, per template | ❌ |

The engine reads `Scope`/`Depth` and the plan lists **only** from the `## Execution Plan Summary` section; copies elsewhere (e.g. under `## Project Information`) are informational and have no routing effect.

Discipline:

- The model **MUST NOT hand-edit** the engine-owned region (the `ENGINE-STATE` marker region) — its checkboxes, Current Status, State Digest, or Unit Progress. All changes there flow through `report`, `jump`, or `rebase`.
- The model maintains the model-owned regions normally, following the templates in the stage rules.
- **User input records in `audit.md` remain model-owned.** The model is the sole visible source of user input; the engine additionally appends its own transition entries to the audit log. Never let an engine transition entry substitute for logging the user's raw input.

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
| `status` | No | Bootstrap probe + session-recovery data source. Returns `state`, `scope`, `depth`, `current_stage`, `last_completed`, `integrity`, `completed`, `remaining`. |
| `init` | Yes (create) | Deterministically create `aidlc-docs/aidlc-state.md` (model-region placeholders + `ENGINE-STATE` region: the 14-stage slug checklist, Current Status, reserved Unit Progress, State Digest) and the `audit.md` header. Errors if the state file already exists. |
| `next` | No | Pure-read routing. Returns exactly one directive: `run-stage`, `done`, or `error`. |
| `report` | Yes | The only transition entry point. `--stage <slug> --result <r> [--reason]`. See §5. |
| `jump` | Yes | Change course. `--stage <slug>` (redo/forward) or `--fresh` (Start Fresh). See §8. |
| `rebase` | Yes | After human confirmation of a detected drift, re-baseline the State Digest. See §7. |

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
  "remaining": ["workflow-planning", "application-design", "units-generation", "functional-design", "nfr-requirements", "nfr-design", "infrastructure-design", "code-generation", "build-and-test"]
}
```

`state` is one of `none` (no state file), `active` (in progress), `completed` (all applicable stages done), `legacy` (a state file exists that predates the engine and has no `ENGINE-STATE` region; do not silently adopt or overwrite it — present the situation, obtain explicit confirmation, and follow the engine's hint before creating engine-owned state), or `corrupt` (the `ENGINE-STATE` marker region is present but incomplete or malformed — e.g. truncated, or a marker line deleted; `integrity` reports `violated` and mutating commands fail with error code `state-corrupt`. Restore the missing marker line from a backup if available — the END line is exactly `<!-- END ENGINE-STATE -->`; otherwise obtain explicit user confirmation and Start Fresh with `jump --fresh`). `current_stage` and `last_completed` are `null` when not applicable. `integrity` is `ok` or `violated`.

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

### Write subcommands

`init`, `report`, `jump`, and `rebase` print a JSON acknowledgment object on success. Treat a `kind: "error"` object (or a non-zero exit status) as failure; otherwise the operation succeeded. Unknown fields in the acknowledgment must be ignored.
