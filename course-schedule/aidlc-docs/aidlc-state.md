# AI-DLC State Tracking

## Project Information
- **Project Name**: course-schedule (课程表 web 小程序，供大学生使用)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-15T04:24:09Z

## Workspace State
- **Existing Code**: No
- **Reverse Engineering Needed**: No
- **Workspace Root**: D:\Documents\PythonProject\aidlc-skills\course-schedule
- **Note**: Project lives as a subdirectory of the aidlc-skills git repository (user's explicit choice)

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis (Q8: B) |
| Resiliency Baseline | No | Requirements Analysis (Q9: B) |
| Property-Based Testing | No | Requirements Analysis (Q10: C) |
| Context Checkpointing | No | Requirements Analysis (Q11: B) |

## Execution Plan Summary
- **Scope**: classic
- **Depth**: standard (scope default)
- **Stages to Execute**: functional-design, code-generation, build-and-test
- **Stages to Skip**: application-design (single simple frontend app), units-generation (implicit single unit), nfr-requirements (tech stack already determined), nfr-design (nfr-requirements skipped), infrastructure-design (pure frontend no infra), operations (placeholder)

<!-- BEGIN ENGINE-STATE | do not hand-edit — maintained by scripts/engine.py -->
State Version: 1
Engine: aidlc-workflows/scripts/engine.py

## Stage Progress

### inception
- [x] workspace-detection
- [S] reverse-engineering
- [x] requirements-analysis
- [S] user-stories
- [x] workflow-planning
- [ ] application-design
- [ ] units-generation

### construction
- [x] functional-design
- [ ] nfr-requirements
- [ ] nfr-design
- [ ] infrastructure-design
- [ ] code-generation
- [ ] build-and-test

### operations
- [ ] operations

## Current Status
- **Lifecycle Phase**: construction
- **Current Stage**: code-generation
- **Status**: Active

## Unit Progress
(reserved — not used in state version 1)

## State Digest
sha256: b61a71484562dc43f53aee46f20b0cd5e596ffa72212832a785025db4b1240bf
<!-- END ENGINE-STATE -->
