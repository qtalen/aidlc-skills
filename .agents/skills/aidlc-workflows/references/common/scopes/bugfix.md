---
name: bugfix
depth: minimal
keywords:
  - fix
  - bug
  - broken
description: "Fix a specific bug in an existing codebase"
---

# bugfix scope

Minimal depth for fixing one specific bug in an existing codebase. It skips
every design ceremony, runs reverse-engineering to understand the current
code (brownfield only), pulls requirements for the fix, then generates and
tests it.

## Why these stages, why skip those

A bug fix is incremental work on a known system. It needs to understand what
exists (reverse-engineering, CONDITIONAL on brownfield), state what "fixed"
means (requirements-analysis), and change-plus-verify (code-generation,
build-and-test). It does not need user-stories, application-design,
units-generation, the NFR/infrastructure design pass, or operations — the
change is too targeted to pay for them.

## Membership

Keyword triggers: `fix`, `bug`, `broken`. workspace-detection,
requirements-analysis, workflow-planning, code-generation, and build-and-test
execute (as in every scope); reverse-engineering is CONDITIONAL; everything
else is SKIP.
