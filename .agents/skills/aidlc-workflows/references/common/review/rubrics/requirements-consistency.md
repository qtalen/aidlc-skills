# Rubric — requirements-consistency

## Scope

The workflow's `requirements.md` (the stage's produce), with
`product-design.md` (its Iteration Roadmap section scopes multi-iteration
products) as reality anchors passed in the brief. You review the contract's internal
quality — **not** the product's merit (that is the human's call at the gate).

## Dimensions

Only dimensions a machine cannot check. For each: what to examine, and what
counts as evidence.

1. **Internal consistency.** Statements that conflict across sections —
   goals vs boundaries vs acceptance criteria vs non-goals. Evidence: quote
   both statements with locations.
2. **Boundary observability.** Each stated boundary must be observable in
   principle: could a test, or a user conversation, ever distinguish
   in-scope from out-scope? A boundary nothing can observe is decoration.
3. **Non-goal falsifiability.** A non-goal is real only if one could tell
   when it is violated. Rhetorical non-goals ("we value quality") are
   findings.
4. **Acceptance-criterion testability.** Each criterion must state an
   observable outcome, not an activity ("the page loads" vs "improve the
   page"). Untestable criteria poison every downstream verification.
5. **Upstream fidelity.** Against product-design (and the current roadmap
   row): commitments silently narrowed, dropped, or reinterpreted; scope
   creep beyond them. Evidence: the two conflicting passages, side by side.
6. **Naming stability.** One concept, one term. Drifting synonyms
   ("unit"/"module"/"component" for the same thing) become ambiguity
   downstream.

## Finding format

Every finding carries: evidence (`file:line` or exact quote with location)
and the inline threshold triple — **trigger condition / fallback (write
"none" if absent) / actual consequence**. A finding with no statable
consequence is a note, not a blocking finding.

## Out of scope

Formatting, section presence, numbering, coverage-matrix arithmetic
(machine-checkable — sensor domain); product merit and prioritization (the
human gate); design-level risk (that is `design-soundness`, at the direction
stop).
