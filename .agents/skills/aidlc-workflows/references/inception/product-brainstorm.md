---
slug: product-brainstorm
phase: inception
execution: CONDITIONAL
condition:
  execute_if: a product-shaped wish with no usable product design — a new product, a new capability direction, or a major evolution of the product, including wording that is vague but carries product-level intent
  skip_if: an existing product-design.md roadmap already covers the request with no shape change (iteration re-entry), or the user has already provided a complete design (covering positioning and evolution — enough for Requirements Analysis to start directly), or the request does not change product features or design (bugfix, refactor, security patch, ops, or pure implementation of an already-designed iteration)
gate: approve-continue
produces:
  - inception/product-design/product-design.md
consumes:
  - artifact: inception/reverse-engineering/*
    required: false
requires_stage:
  - workspace-detection
  - reverse-engineering
depth: adaptive
scopes:
  classic: CONDITIONAL
  bugfix: SKIP
  refactor: SKIP
  security-patch: SKIP
  infra: CONDITIONAL
  express: SKIP
---

# Product Brainstorm

**Purpose**: Turn a vague product wish into a shared product design — through dialogue, not a questionnaire.

**Assume the role** of a design partner having a Platonic conversation with the product owner.

**Execute when**: a product-shaped wish arrives with no usable product design (new product, new capability direction, major evolution).

**Skip when**: the existing `product-design.md` roadmap already covers the request without a shape change (iteration re-entry); the user already provided a complete design; or the request changes no product feature or design.

**Depth**: adaptive — a small wish may legitimately end as a one-page design (see The Artifact).

## Stance: A Conversation, Not a Questionnaire

This stage is a **stance, not a workflow**. The design emerges from the dialogue; it is not extracted through a predetermined list of questions.

- **Open threads, not interrogations**: raise what matters when it matters; never march through a checklist.
- **Decisions live in the conversation**: acknowledge each decision in-line the round it is made ("Noted: X uses PostgreSQL") — the file comes later, once, at the end.
- **Challenge assumptions**: when the user's framing contains an unexamined assumption, surface it — as a question, with your recommendation and its trade-off, never as a silent correction.
- **Follow the answers**: let each answer open the next thread; a question worth asking is one the previous exchange made valuable.
- **Private scaffolding, never a template**: the six-domain lens and the first-principles scaffold below are your *inner* basis for choosing threads. They are never presented as a form, and no domain is a mandatory question.

## Opening: Criteria Announcement and Graceful Exit

On the first turn of this stage, announce your read of the request in one line, e.g. "This looks like a new product wish — I'd like to explore the product shape with you first; if that's not what you want, say so and I'll skip this stage." Then begin.

- Intent classification is **semantic, never keyword matching**.
- When genuinely uncertain whether this stage applies, **execute** — the cost is asymmetric (a wrong skip can only be recovered by a later suggestion to return here; a wrong execute costs one opening exchange).
- The user holds the termination right at every moment: if they say this is not needed, exit gracefully — `engine.py report --stage product-brainstorm --result skipped --reason user-declined` — and Requirements Analysis stops suggesting a return for the rest of this session.

## Understanding Write-Back (early checkpoint)

After the opening exchange, **before diving deeper**, present a short note that restates:

- the user's intent, in one or two sentences;
- the constraints and success criteria you heard;
- **what you are assuming** — explicitly separated from what was actually said.

Invite corrections and wait for them. A user who answers quickly is not a reason to skip this checkpoint — it is the cheapest moment to discover you understood the wish wrong.

## Two Boundaries That Never Move

- **Evidence boundary**: repository evidence (Reverse Engineering output, existing artifacts, established patterns) establishes the *status quo and technical constraints*. It **never decides user intent**. An existing pattern is an option and a recommendation basis, not a decision — present it as "here is what exists, and here is what I'd recommend", and the choice stays with the user.
- **Declaration-as-fact boundary**: when the user declares the product or an outcome itself ("make me a chess game"), the declaration enters the fact list and is **never challenged**. Decompose only its *surrounding context* (who uses it, in what scenario, what "done" looks like). A category-default feature that your analysis would cut is **never silently dropped — it becomes a question**.

## First-Principles Scaffold (private)

Before opening threads, work through this scaffold internally — it is the basis for your questions, never a form the user sees:

1. **Restate the problem** in one sentence, stripped of implementation detail ("user profiles load too slowly" — not "add a Redis cache").
2. **List the basic facts**: physical constraints, business rules, technical invariants, genuine user needs — facts only, not conventions.
3. **Challenge assumptions**: is each item a fact or a convention? What breaks if it is removed? Is this solving the real problem or a symptom?
4. **Build bottom-up**: start from the smallest mechanism; every addition must answer "which fact requires this?".
5. **Validate**: does this solve the original problem? Which assumptions remain unverified? What is the simplest experiment?

The fact list becomes the skeleton for your conversation threads. (Deliberately narrower than its source: no anti-over-engineering dimension here — depth control lives in the artifact, not in this lens.)

**Six domains** (functional, non-functional, user scenarios, business context, technical context, quality attributes) serve the same way: the inner checklist behind your threads, not a questionnaire to administer.

## Dialogue Discipline

- **One focused question at a time** per message — the highest-value one (the decision that unblocks the most downstream thinking) — and say which decision it unlocks. Free-form responses to topics the *user* raises are unrestricted; serializing applies only to your questions.
- **Recommend with a trade-off**: when you hold a well-founded recommendation, state it and what choosing otherwise costs.
- **YAGNI**: fight scope the user did not ask for — every "while we're at it" addition is a question, not a default.
- **Preference questions are never waived**: preference-driven decisions (implementation stack, deployment form, UI language, ...) remain questions even under a "non-technical user" picture or an inferred runtime shape. Evidence-First exempts only evidence-resolvable items and category facts — a persona is a lens, not a classifier, and a runtime-form inference (e.g. "zero-dependency page") constrains the recommendation, never the asking.
- **Red flags** — check yourself against these:
  - "The wish is too small for a roadmap" — a one-page design *is* a valid roadmap.
  - "The user answers quickly, skip the write-back" — fast answers make the checkpoint *more* valuable, not less.
  - "This feature is obvious, cut it silently" — category defaults become questions, never silent cuts.
  - "Let's just fill in the standard question list" — that is the retired anti-pattern; threads come from the dialogue.
  - "The user seems impatient, propose Autonomous Mode" — AM is deferred (see below); the fast path exists instead.
- **ASCII visualization**: when structure is easier seen than read (a screen layout, a stage flow, a module map), sketch it inline in ASCII. Per-diagram criterion: does the picture make the point clearer than the words would? If not, drop it. (No browser dependence — this skill is harness-neutral.)

## Tools Within the Dialogue

The dialogue leads; tools serve. A decision with a **small set of fixed options** (an opt-in flag, a choice among three layouts, yes/no deployment target) may be asked via the structured question tool at any moment — that is not a failure of the dialogue, it is the right instrument for that decision.

Tool calls made during this stage are **exempt from the question-file requirement** (`question-format-guide.md`): the question and its answer stay in the conversation record and are crystallized into `product-design.md` at the end, in one write. Do not create a questions file for this stage's dialogue.

## Splitting the Evolution (iteration thinking)

Think in iterations from the start; the roadmap section of the artifact records the split.

- **What an iteration is**: the smallest demonstrable increment that can end a full workflow round with all quality gates green — the criterion is "can it be closed with full quality", not a size intuition.
- **Hard criteria**: **H1** downward closure (iteration K must not depend on capabilities planned for iteration >K); **H2** observable outcome (every iteration ends with something externally checkable — no dark iterations). Violations must be fixed before the gate approves, or explicitly waived on record.
- **Soft criteria** (guidance, not gates): skeleton first (iteration 1 is the thinnest end-to-end vertical slice, never "finish one layer first"); one-sentence narrative (if you cannot tell what an iteration delivers in one sentence it is too thin to stand alone; if you need a list, too thick — split it); risk early; reserve a hardening iteration after a run of feature iterations or when deferred items pile up.
- **The user's explicit split always wins**: audit it against the criteria, report violations with their cost (the classic case: cross-cutting layer splits — "iteration 1 all frontend, iteration 2 all backend" — violate H2 and skeleton-first; suggest vertical slices instead), and proceed with theirs if they insist, recording the risk note. Never re-split a user-provided split on your own authority.
- **Small is legal**: N=1 (single iteration, no roadmap beyond it) is a valid outcome; the one-page floor applies. Non-classic scopes do not split by default.
- **"Suggest a smaller split" is an approved rejection action**: when the user insists on one oversized delivery and you judge the risk high, give the split suggestion with its trade-off — neither silently comply nor refuse service.

## Crystallization

**When**: positioning is clear; the evolution direction has shape; the iteration split has shape; open items are explicit. No forced ending mid-thinking — but crystallization is this stage's only exit; "thinking was the output" applies only mid-dialogue.

1. **Present section by section, confirm section by section**: Positioning → Users and Scenarios → Evolution Direction → Iteration Split. One section per turn; the next section starts after the previous one survives its confirmation.
2. **Approval-scope precision**: a "continue" approves only what was just presented. There is **no pre-authorization** — later sections still need their own confirmation, even for an eager user.
3. **Four-way self-check** before writing: placeholders left? internal contradictions? ambiguous phrasing? scope creep beyond the dialogue?
4. **One-time write**: create `aidlc-docs/inception/product-design/product-design.md` in a single write at the end. During the dialogue there are **zero product writes** (audit entries are the only exception — they are not product artifacts). Verify after the write that the file exists and is non-empty.
5. **Gate**: present the artifact for approval (approve-continue). Record via `engine.py report --stage product-brainstorm --result approved | rejected | revised` (fall back to `python3`). Never hand-edit the engine-owned state region.

**Small finishing decisions are asked one by one**: telemetry, icons, naming, and similar small calls each get their own question with a recommendation — never a bundled "approve all defaults" package that a single rejection voids wholesale.

**Audit granularity**: log milestone-level entries — the opening announcement, the understanding write-back, the crystallization, the gate — not every dialogue round.

## The Artifact: product-design.md

Structure (adaptive depth — a small wish may compress sections to a line, but never below the one-page floor: positioning paragraph + single iteration + three "later" items):

```markdown
# Product Design — [Name]

## Positioning
[What this product is, for whom, in one paragraph]

## Users and Scenarios
[Who uses it, doing what; the 2-4 scenarios that define success]

## Key Decisions
| Decision | Rationale | Source |
|---|---|---|
| [e.g. web-first, no native app] | [why] | [which exchange/round] |

## Evolution Direction
[Where this product is heading across iterations, in prose]

## Iteration Roadmap
[see format below]

## Out of Scope
[Explicitly excluded, with the reason]

## Open Items
[Unresolved questions, parked deliberately]
```

**Depth is declared, then earned**: state the intended depth early; discovering real complexity **raises** it (one-way ratchet — complexity discovered is never waved away by fiat).

**Iteration Roadmap section format** (adapted from the B16 template):

```markdown
## Iteration Roadmap

### Iteration Status
| # | Status | Goal (one sentence) | Scope (FR/US subset) | DoD | Git |
|---|--------|---------------------|----------------------|-----|-----|
| 1 | next | ... | ... | ... | — |
| 2 | planned | ... | ... | ... | — |

<!-- Status values: planned / next / in-progress / shipped / dropped -->
<!-- DoD field composition: full regression green + demonstrable acceptance
     for this iteration (hard); staging deployment rehearsal + thin ops
     handover (placeholder — upgrades to hard when Operations becomes real);
     hardening items if any -->

### Shipped Log
<!-- rollup: one compressed line + git commit pointer, written at the moment
     an iteration ships; immutable afterwards -->

### Deferred / Backlog
<!-- numbered, never recycled — the candidate pool for later iterations -->

### Revision Record
<!-- append-only (DOC-04): when, why, and what changed -->
```

Iteration numbering starts at 1 for the current product; FR/US identifiers follow Requirements Analysis and User Stories numbering once those exist (on re-entry, subsets reference them).

## Autonomous Mode and Park

The brainstorm dialogue is **exclusively human territory** — no mechanism may make product decisions for the user. (When Product Brainstorm becomes the current stage while Autonomous Mode is on, AM-05's brainstorm trigger deactivates the mode first — see `references/extensions/workflow/autonomous-mode/autonomous-mode.md`; this section then applies in standard mode.)

- **Activate intent during the dialogue**: deferred, never executed here. Announce in one line ("Autonomous Mode will activate at Requirements Analysis"), log it in audit — do **not** write `Enabled: Yes`. A full, fresh activation flow (AM-02, including the code-gen hold question) runs at the Requirements Analysis boundary. During the deferral window, an exit/cancel intent cancels the pending activation (no AM state change; one audit line). The pending activation never persists across sessions. (AM deferral semantics: `references/extensions/workflow/autonomous-mode/autonomous-mode.md`, AM-02.)
- **The impatient user takes the fast path, not AM**: draft a full-default `product-design.md` from everything heard so far and present it — but the gate still requires explicit human approval. Speed comes from defaults, never from delegated decisions.
- **Park is not offered for the dialogue**: the discussion does not persist across sessions. An interruption or context compaction abandons the current dialogue — on resume, restart the conversation (the understanding write-back makes this cheap) or take the fast path. This is a deliberate, recorded trade-off. (Contrast with normal stages: `references/common/session-continuity.md`, Park Ritual.)

## Gate and Reporting

Approval gate before proceeding (see Crystallization step 5). Completion message follows the standard structure:

```markdown
# 💡 Product Brainstorm Complete

[AI-generated summary: positioning in one sentence, iteration count, first iteration's goal]

> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the product design at: `aidlc-docs/inception/product-design/product-design.md`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to any section of the design
> ✅ **Approve & Continue** - Approve the design and proceed to **Requirements Analysis**
```

- MANDATORY: do not proceed until the user explicitly approves.
- MANDATORY: log the user's response in audit.md with the complete raw input.
- Downstream handoff: Requirements Analysis loads `product-design.md` as input context and scopes its work to the current (first) iteration.
