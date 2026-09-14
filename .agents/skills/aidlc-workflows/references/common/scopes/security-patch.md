---
name: security-patch
depth: minimal
keywords:
  - security
  - CVE
  - vulnerability
  - patch
description: "Respond to a CVE or vulnerability fast"
---

# security-patch scope

Minimal depth for responding to a CVE or vulnerability. It threads the same
narrow path as `bugfix`, plus nfr-requirements to record the security
constraint explicitly — the one artifact a security fix must not lose.

## Why these stages, why skip those

A security patch is urgent, incremental, and auditable. It skips the whole
design ceremony (user-stories, application-design, units-generation,
nfr-design, infrastructure-design) because the change is targeted, but keeps
nfr-requirements so the security constraint and its remediation criteria are
written down where code-generation will consume them.

## Membership

Keyword triggers: `security`, `CVE`, `vulnerability`, `patch`. The ALWAYS
spine plus reverse-engineering (CONDITIONAL) and nfr-requirements (EXECUTE)
run; everything else is SKIP.
