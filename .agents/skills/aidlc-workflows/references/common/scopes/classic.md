---
name: classic
depth: standard
keywords: []
description: "Full lifecycle with adaptive stage self-selection — the implicit default"
default: true
---

# classic scope

`classic` is the implicit default scope — used when no scope keywords match and
the user does not name one. It reproduces the AI-DLC v1.0 experience: every
ALWAYS stage runs, and every CONDITIONAL stage self-selects from project
context at Workflow Planning time.

## Why these stages, why skip those

Nothing is pre-skipped. The five ALWAYS stages (workspace-detection,
requirements-analysis, workflow-planning, code-generation, build-and-test)
form the spine; the CONDITIONAL stages (reverse-engineering, user-stories,
application-design, units-generation, functional-design, nfr-requirements,
nfr-design, infrastructure-design, operations) decide from context exactly as
their `condition` fields describe. Choose another scope when the task shape is
known up front and you want the pruning done before the questions start.

## Membership

All 14 stages are EXECUTE or CONDITIONAL; nothing is SKIP. No keyword
triggers — selected by name or by default.
