---
slug: workspace-detection
phase: inception
execution: ALWAYS
condition: Always executes — detects existing workflow state and codebase, resumes prior work or classifies greenfield/brownfield
gate: none
produces:
  - aidlc-state.md
  - audit.md
consumes: []
requires_stage: []
scopes:
  classic: EXECUTE
  bugfix: EXECUTE
  refactor: EXECUTE
  security-patch: EXECUTE
  infra: EXECUTE
  express: EXECUTE
---

# Workspace Detection

**Purpose**: Determine workspace state and check for existing AI-DLC projects

## Step 1: Check for Existing AI-DLC Project

Check if `aidlc-docs/aidlc-state.md` exists:
- **If exists**: This is a resume — do NOT recreate state. Run the engine status probe (prefer `python`, fall back to `python3`):
  ```
  python <skill>/scripts/engine.py status
  python3 <skill>/scripts/engine.py status
  ```
  Then follow the session-continuity flow (`references/common/session-continuity.md`) to present the recovery menu.
- **If not exists**: Continue with new project assessment

## Step 2: Scan Workspace for Existing Code

**Determine if workspace has existing code:**
- Scan workspace for source code files (.java, .py, .js, .ts, .jsx, .tsx, .kt, .kts, .scala, .groovy, .go, .rs, .rb, .php, .c, .h, .cpp, .hpp, .cc, .cs, .fs, etc.)
- Check for build files (pom.xml, package.json, build.gradle, etc.)
- Look for project structure indicators
- Identify workspace root directory (NOT aidlc-docs/)

**Record findings:**
```markdown
## Workspace State
- **Existing Code**: [Yes/No]
- **Programming Languages**: [List if found]
- **Build System**: [Maven/Gradle/npm/etc. if found]
- **Project Structure**: [Monolith/Microservices/Library/Empty]
- **Workspace Root**: [Absolute path]
```

## Step 3: Assess Brownfield Status and Reverse Engineering Need

**IF workspace is empty (no existing code)**:
- Set flag: `brownfield = false`
- Reverse Engineering does not apply (greenfield)

**IF workspace has existing code**:
- Set flag: `brownfield = true`
- Check for existing reverse engineering artifacts in `aidlc-docs/inception/reverse-engineering/`
- **IF reverse engineering artifacts exist**:
    - Check if artifacts are stale (compare artifact timestamps against codebase's last significant modification)
    - **IF artifacts are current**: Reverse Engineering does not apply (load them when Requirements Analysis runs)
    - **IF artifacts are stale**: Reverse Engineering applies (rerun to refresh artifacts)
    - **IF user explicitly requests rerun**: Reverse Engineering applies regardless of staleness
- **IF no reverse engineering artifacts**: Reverse Engineering applies

These flags feed the Reverse Engineering stage's conditional judgment (`skipped --reason` vs execute) when the engine emits it — the `next` directive decides what actually runs next.

## Step 4: Initialize State File via Engine

State creation is deterministic and engine-owned. Run `init` (prefer `python`, fall back to `python3`):

```
python <skill>/scripts/engine.py init
python3 <skill>/scripts/engine.py init
```

`init` creates `aidlc-docs/aidlc-state.md` (if absent) with the engine-owned `<!-- BEGIN ENGINE-STATE -->` region — the stage checklist, Current Status, Unit Progress, and State Digest — and creates the `aidlc-docs/audit.md` header if that file does not exist. If `aidlc-docs/aidlc-state.md` already exists, `init` returns an error JSON; that is the resume path from Step 1, not a new project.

**Then fill the model-owned regions** (the engine leaves them as placeholders). Record the Step 2 findings here:

```markdown
## Project Information
- **Project Type**: [Greenfield/Brownfield]
- **Start Date**: [ISO timestamp]

## Workspace State
- **Existing Code**: [Yes/No]
- **Reverse Engineering Needed**: [Yes/No]
- **Workspace Root**: [Absolute path]

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules
```

**Ownership**: sections inside `<!-- BEGIN ENGINE-STATE -->` / `<!-- END ENGINE-STATE -->` are engine-exclusive — MUST NOT be hand-edited. The model owns and maintains the sections above (plus `## Execution Plan Summary` and later plan overrides). The first user input is still logged by the model in `aidlc-docs/audit.md`; engine transitions are appended by the engine itself.

## Step 5: Present Completion Message

**For Brownfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Brownfield project
• [AI-generated summary of workspace findings in bullet points]
• **Next Step**: Decided by the engine (typically **Reverse Engineering** on brownfield)...
```

**For Greenfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Greenfield project
• **Next Step**: Decided by the engine (typically **Requirements Analysis**)...
```

## Step 6: Report Completion

- **No user approval required** - this stage is informational only
- Run `python <skill>/scripts/engine.py report --stage workspace-detection --result completed` (fall back to `python3` if `python` is unavailable)
- What runs next is decided by the engine's `next` directive in the orchestration loop — not by this file. (The engine emits Reverse Engineering as `conditional: true` on brownfield; judge its Execute-IF/Skip-IF then.)
