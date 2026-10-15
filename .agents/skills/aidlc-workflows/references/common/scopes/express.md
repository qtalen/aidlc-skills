---
name: express
depth: minimal
keywords:
  - express
  - lightweight
  - quick
description: "Lightest run: requirements to code with no design pass"
---

# express scope

`express` is the lightest run: a straight line from requirements to code and
test, with no design pass at all.

## Why these stages, why skip those

Some tasks need a written contract and verified code, nothing more.
requirements-analysis establishes the contract, code-generation implements
it, build-and-test verifies it. reverse-engineering stays CONDITIONAL so
brownfield work still gets codebase understanding; every design stage
(user-stories, application-design, units-generation, functional-design,
nfr-requirements, nfr-design, infrastructure-design) and operations are SKIP.
If the result outgrows the scope, re-scope to `classic` and run the full arc.

## Membership

Keyword triggers: `express`, `lightweight`, `quick`. The ALWAYS spine plus
CONDITIONAL reverse-engineering run; everything else is SKIP.
