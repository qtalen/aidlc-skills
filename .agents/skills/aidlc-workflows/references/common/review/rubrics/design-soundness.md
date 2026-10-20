# Rubric — design-soundness

> Model tier: run this review on the **strongest available model** —
> design decisions are the most expensive to get wrong downstream (one
> bad call propagates through the whole round's implementation), making
> this the highest-leverage review in the workflow.

## Scope

The design-stage artifacts this round consumes — application design,
functional design, NFR requirements/design, infrastructure design — reviewed
**as a merged set** at the round-level direction stop, before the direction
brief is presented. Brownfield: affected code paths are starting pointers;
pursue completeness independently.

## Dimensions

1. **Decision risk.** The load-bearing decisions in these artifacts: single
   points of failure, complexity without a stated justification, component
   contracts that do not match where they meet. Evidence: the decision, its
   location, and the concrete failure mode.
2. **Drift vs requirements.** Designs that silently narrow, reinterpret, or
   exceed what `requirements.md` committed to. Evidence: the requirement
   passage vs the design passage.
3. **Missing failure paths.** Error, edge, and degradation handling absent
   exactly where the artifact states consequences (a happy-path-only design
   for a risky flow is a finding).
4. **Integration risk.** Seams between units or layers that **no artifact
   owns** — each side assumes the other handles it. Name the seam and both
   assumptions.
5. **Testability of promises.** Design promises whose acceptance cannot be
   observed by build-and-test — unverifiable by construction.

## Finding format

Every finding carries: evidence (`file:line`) and the inline threshold
triple — **trigger condition / fallback (write "none" if absent) / actual
consequence**. A finding with no statable consequence is a note, not a
blocking finding.

## Out of scope

Transcription errors, numbering, section presence (machine-checkable);
implementation quality of code (that is `code-quality`, at build-and-test);
whether the requirements themselves are right (that was the RA review and
the human gate).
