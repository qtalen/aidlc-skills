---
name: infra
depth: standard
keywords:
  - infrastructure
  - deploy
  - infra
description: "Infrastructure and deployment-topology changes"
---

# infra scope

Standard depth for infrastructure changes. It skips the application-design
chain (user-stories, application-design, units-generation, functional-design)
and instead runs the NFR + infrastructure design pass that feeds the build.

## Why these stages, why skip those

Infrastructure work is not about product features, so the application design
stages are skipped. It is about how the system is provisioned and run, so
nfr-requirements, nfr-design, and infrastructure-design are EXECUTE.
reverse-engineering is SKIP: infra work starts from the deployment topology,
not the application source. Unlike v2.0 (which skips code-generation in favor
of a dedicated ci-pipeline stage), this fork keeps code-generation EXECUTE —
it is the stage that writes the IaC.

## Membership

Keyword triggers: `infrastructure`, `deploy`, `infra`. The ALWAYS spine plus
nfr-requirements, nfr-design, and infrastructure-design run; reverse-
engineering and the application design chain are SKIP.
