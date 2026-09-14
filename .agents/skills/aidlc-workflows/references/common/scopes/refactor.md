---
name: refactor
depth: minimal
keywords:
  - refactor
  - clean up
  - simplify
description: "Clean up existing code without changing behavior"
---

# refactor scope

Minimal depth for restructuring existing code without changing behavior. Like
`bugfix` it skips most of the design ceremony, but it keeps functional-design:
a refactor reshapes structure, so the design of the behavior being preserved
matters.

## Why these stages, why skip those

Refactoring is structure-preserving change on a known codebase. It runs
reverse-engineering (understand what exists), requirements-analysis (pin down
the behavior to preserve), functional-design (the target shape), then
code-generation and build-and-test (apply and verify the existing suite stays
green). It skips user-stories, application-design, units-generation, and the
NFR/infrastructure stages because there is no new product or infrastructure
surface.

## Membership

Keyword triggers: `refactor`, `clean up`, `simplify`. The ALWAYS spine plus
reverse-engineering (CONDITIONAL) and functional-design (EXECUTE) run;
everything else is SKIP.
