# Rubric — code-quality

## Scope

The **code produced this round** (paths given in the brief — typically
`src/`, `tests/`, taken from this round's unit plans or the diff),
reviewed against the design and requirements artifacts as the **comparison
surface**. This is a reading review of the implementation, not of the test
evidence.

## Dimensions

1. **Correctness reading.** Logic errors the test suite would not catch:
   unhandled paths that contradict stated behavior, inverted or partial
   conditions, resource leaks with stated consequences. Evidence:
   `file:line` plus the contradicting contract passage.
2. **Performance.** Algorithmic or structural risks **with a statable
   consequence at expected scale** — not stylistic micro-optimizations.
3. **Architecture.** Responsibilities misplaced relative to the design
   artifacts; layering or dependency violations of the stated architecture.
   Evidence: the code location vs the design passage that it contradicts.
4. **Artifact match.** Implementation vs design/requirements: silent
   divergences — behavior that deviates from the artifacts without any
   recorded decision. (A documented, deliberate deviation is not a finding;
   an undocumented one is.)

## Capability conditioning (mandatory)

Dimensions that require **execution** to verify — re-running tests, real
measurement — are **conditional on your tool access**. If the execution tool
(e.g., a shell) is denied or absent:

- **skip** those checks;
- list them in the entry's `not-covered` field (e.g.,
  `execution-dependent dimensions — bash denied`);
- never turn them into findings, and **never present them as verified**.

## Finding format

Every finding carries: evidence (`file:line`) and the inline threshold
triple — **trigger condition / fallback (write "none" if absent) / actual
consequence**. A finding with no statable consequence is a note, not a
blocking finding.

## Out of scope

Style and formatting (machine domain); whether tests really ran and exit
codes are real (that is `evidence-credibility`, deferred to Phase 5B);
whether the requirements are right (RA domain); design-document internal
risk (`design-soundness` domain).
