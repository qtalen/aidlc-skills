# Review Delegation (RV) — mandatory reviewer wiring

This file is loaded on demand by the stages that declare `review_class` in
their frontmatter (requirements-analysis, code-generation, build-and-test).
Every RV clause below is a **mandatory step anchored in the stage's own rule
file** — a stage that declares `review_class` must delegate a review before
presenting the material named in RV-01. The engine is never involved: reviews
happen model-side, before the stage's `report`.

## RV-01 — When a review runs

| Stage | Position | Class | Review completes BEFORE |
|---|---|---|---|
| requirements-analysis | gate advisor | `requirements-consistency` | the gate material is presented to the user (the user reads a pre-reviewed contract) |
| code-generation | direction-stop advisor | `design-soundness` | the direction brief is presented — and before waiting for release. Order is fixed: **delegate → brief → wait**. Never after release. At most once per round (anchors at the round-level direction stop, never per unit) |
| build-and-test | completion verification | `code-quality` | the Step 9 completion brief is presented (i.e., before the commit plan and the authorization question) |

**First fixed action** on entering any review position: read
`references/common/review/index.md` and resolve this stage's `review_class`
to a rubric path. The rubric itself never enters the main session — only the
reviewer reads it (lazy + pull).

## RV-02 — Composing the delegation brief

The brief is contract-assembled. It contains, in order:

1. the **rubric path** — paths in `review/index.md` resolve relative to
   that index's own directory; pass the reviewer a path it can actually
   open (prefer an absolute path when the harness accepts one);
2. the **audited artifacts and reality anchors** for this position, from the
   table below — passing these paths is mandatory, the reviewed object is
   NOT always in produces/consumes;
3. the **acceptance criteria verbatim** (from the stage contract / upstream
   artifact) — expected results come only from contract acceptance criteria;
4. the **read-only clause** (RV-05) and the **output contract** (RV-03),
   restated in the brief.

**Forbidden in the brief**: producer self-narrative ("what I did and why it
is right"). Reality anchors are **starting pointers, not an exhaustive
baseline** — the reviewer must independently pursue completeness; prefer
objective artifacts (file lists, diffs) over producer-judged "affected
paths".

| Position | Audited artifacts | Reality anchors (starting pointers) |
|---|---|---|
| requirements-analysis | `inception/requirements/requirements.md` (produces) | `inception/product-design/product-design.md` — already in RA's consumes with `required: false`; still pass the path explicitly so the reviewer opens it for sure. The roadmap is that file's Iteration Roadmap section (not a separate file) |
| code-generation (direction stop) | the design artifacts feeding this round: the workflow-level application design (`aidlc-docs/inception/application-design/`) plus this round's unit design docs (`aidlc-docs/construction/{unit-name}/` — functional / NFR / infrastructure design) | brownfield: affected code paths (starting pointers; reviewer pursues completeness) |
| build-and-test | **the code produced this round** — the path source of truth is this round's unit plans (`aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`, whose steps document exact paths); cross-check with `git status`/diff where git is available. Non-git workspace: the plans' target-path lists ARE the working file list. Code lives at the workspace root (`src/`, `tests/`, …) — outside any produces/consumes; passing these paths is what makes this position real | the design and requirements artifact paths (the comparison surface for the "matches the artifact documents" dimension) |

## RV-03 — Reviewer output contract

**Findings only.** The reviewer returns findings — it never calls engine
verbs, never opens gates, never approves, never fixes anything itself.

Each finding carries:

- **evidence**: `file:line` (or an exact quote with location);
- the **threshold triple**, inline: *trigger condition / fallback (write
  "none" if absent) / actual consequence*. A finding that cannot state an
  actual consequence has **no blocking power**.

**Naming note**: these are **review findings**. They are NOT the
workflow-conventions "Blocking Finding" (rule-compliance machinery —
audit.md entries, compliance summary formats) and must never be routed into
that process.

## RV-04 — Executor resolution and degradation chain

Resolve the executor by capability, never by name (harness-agnostic):

1. the harness exposes a **dedicated review-capable agent** → best;
2. **generic subagent delegation** → a general agent + the rubric
   (independence retained);
3. **expert-only agents** → usable; the rubric is the lens, the persona is
   second (watch for expert-sympathy bias);
4. **no delegation mechanism** → same-session rubric second read, labeled
   `self-review (degraded)` — or record `review unavailable`.

**Never silently treat a stage as reviewed.** A rubric-bearing general agent
beats a rubric-less expert.

**Lateral variant**: the subagent has no file-read capability → **push
mode**: inline the full rubric text in the brief, and label the log entry
`pushed-rubric`.

**Session discipline (hard rule)**: every real review call runs in a
**brand-new session** — never continue or reuse any existing review
conversation, across same-point re-reviews and cross-point reviews alike.
Tier 4 self-review is the single exception: it is not a review session and
must carry the `degraded` label.

The log records two dimensions — **tier** (which executor class ran the
review) and **containment tier** (RV-05). Never dress a weak guarantee as a
strong one.

## RV-05 — Containment (read-only posture)

- **L0 (structural, always)**: the findings-only output contract — the
  reviewer's language has no "edit" verb; suggestions are text; fixes are
  always executed by the producer.
- **L1 (always)**: the delegation brief carries the read-only clause:
  *"You must not modify any file. Suggestions are text only."*
- **L2 (best effort)**: if the harness has per-agent permissions, prefer a
  read-only reviewer; record the containment tier in the log (mechanical
  read-only / contractual read-only / none).

There is **no snapshot obligation** at this layer. Full detection tooling
(L3) is parked; it goes live immediately if either trigger holds:

1. a real review runs on an environment not covered by permission guards;
2. an unexplained external write to the workspace is observed.

## RV-06 — Triage, fix verification, round budget

**Review event** := (stage, position, iteration[, direction round]).
Re-entry or redo within the same iteration does **not** reset the count —
calls accumulate; a new iteration starts a new event.

**Round budget**: at most **3 review calls per event** — the initial
review plus at most two follow-up calls, each being a **full re-review**
(when the artifact materially changed — new findings allowed) or a
**scoped re-review** (verifying fixes of known findings), chosen by the
nature of the change. A third round that still leaves blocking findings
unresolved → escalate to the user (**fork**) — never a fourth call.
Event lifecycle: once the budget is exhausted (or the event closed) and
the artifact materially changes again **within the same iteration**, that
is not a new call — escalate to the user (**fork**) directly, and render
the review line as `re-review budget exhausted`.

**Materiality** (objective anchors): changes to contract sections,
acceptance criteria, non-goals, boundary text, or code semantics =
**material**; pure formatting, typo fixes, or section moves = **not
material**. A material change spends a full re-review call — a scoped
re-review never covers new content. Re-presenting materially unchanged
gate material **reuses** the event's latest review conclusion: the
review line must state `unchanged since R-00x` so the reuse is
externally checkable; do not re-delegate. When in doubt, treat the
change as material — the reviewer sees the artifact; the producer's
convenience never decides materiality.

**Triage — three exits** for each finding:

- **fix** → verify per its nature (below);
- **reject** → record the reason; the rejection is presented to the user at
  the next gate;
- **escalate** → fork event (the finding challenges a decision itself).

**Fix verification by nature**:

- *mechanical fix* (section added, line number, renumbering) → **diff
  check**: the flagged position changed. Zero LLM.
- *semantic fix* (rewritten ambiguity, changed term) → **scoped
  re-review**: a **brand-new session** whose brief contains this event's
  open semantic findings (a list — one re-review may cover several) plus
  each finding's fix diff; it answers one binary question per finding
  ("resolved: yes/no"), has **no new-finding authority** — side
  observations go to an assumption list for the next checkpoint. Each
  scoped re-review call counts 1 toward the budget regardless of how
  many findings it covers.

**Fix re-feed (build-and-test only)**: code changes resulting from review
findings must **re-run the affected tests and update
`build-and-test-summary.md`** (DOC-03) **before** presenting the completion
brief. Otherwise render the verification line as `unreviewed-after-fix`.

**Zero blocking findings is a success record** — "reviewed per rubric X,
zero blocking findings" is a legitimate, expected outcome. Findings
inflation is a defect, not diligence.

## RV-07 — The review log (`aidlc-docs/reviews.md`)

**Mandatory first step** on entering any review position: read
`reviews.md` for this event's existing entries (per the event definition)
and take the **used-call count**. The count comes from the log — never from
session-context memory.

The file is created on first review; it is model-written workflow
bookkeeping — **not a produce of any stage**, and not in the
session-continuity loading list.

**Append-only hard invariant**: only append; never edit or delete an entry.
Two entry kinds:

- **R-n review entry** — written when the delegation returns, frozen at
  write time. Contains class/rubric (+ content sha256), tier, model,
  session, round used, findings, not-covered. **Never contains triage.**
  When the degradation chain ends at `review unavailable`, still write
  the R entry — `tier: unavailable`, `findings: none (review
  unavailable)` — an honest disclosure, never a silent skip. An
  `unavailable` entry does not consume round budget; record `round: n/a`.
- **T-n disposition entry** — appended later, references its R entry:
  triage results, diff-check / scoped re-review conclusions,
  closure/escalation.

Backfilling an R entry is forbidden — to add state, append a T entry.

```markdown
## R-007 · requirements-analysis · iter 2 · 2026-10-22
- class/rubric: requirements-consistency (sha256:1a2b3c4d5e6f)
- tier: ① dedicated review agent | containment: mechanical read-only (L2)
- model: <reviewer model> | session: fresh (handle if available)
- round: 1 (event: requirements-analysis × gate-advisor × iter 2)
- findings: 2 blocking / 1 note
  - [B1] acceptance criterion 3 not observable (requirements.md:47)
  - [B2] non-goals missing falsifiable boundary (:12)
  - [N1] term drift "unit"/"module"
- not-covered: none (or: execution-dependent dimensions — bash denied)

## T-012 · R-007 · 2026-10-22
- triage: B1 fixed + diff-verified; B2 fixed → scoped re-review R-008 (resolved); N1 → assumption list → next gate
- event closed: round 2/3 used
```

Conventions: rubric version = **content sha256, first 12 hex chars**;
session line records the harness session handle when available, otherwise
`fresh` + delegation timestamp; entry numbers increase monotonically; a
scoped re-review gets its own R entry referencing the original.

## RV-08 — Density guard and gate-line rendering

Review runs **only** at positions declared via `review_class` in
frontmatter. Never invent review points; never attach review to every
stage; never review outside the three positions.

The review line in gate materials / briefs carries **both status and
content**, from this vocabulary — never an unconditional "verified":

- `reviewed (tier ①, L2) — 2 blocking / 1 rejected (see reviews.md R-007)`
- `zero blocking (rubric requirements-consistency)`
- `unchanged since R-007` (materially unchanged re-presentation, RV-06)
- `re-review budget exhausted` (RV-06 event-lifecycle escalation)
- `self-review (degraded)`
- `review unavailable`
- `fork escalated`
- `unreviewed-after-fix`

The build-and-test completion brief is 3 content lines + 1 review line —
under the BRF-01 cap. If it overflows, invoke the BRF-01 self-calibration
clause (report for recalibration) rather than truncating.
