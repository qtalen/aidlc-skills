---
slug: nfr-design
phase: construction
execution: CONDITIONAL
condition:
  execute_if: NFR Requirements was executed and NFR patterns need to be incorporated
  skip_if: no NFR requirements, or NFR Requirements was skipped
gate: brief
produces:
  - construction/plans/{unit-name}-nfr-design-plan.md
  - construction/{unit-name}/nfr-design/nfr-design-patterns.md
  - construction/{unit-name}/nfr-design/logical-components.md
consumes:
  - artifact: construction/{unit-name}/nfr-requirements/*
    required: true
requires_stage:
  - nfr-requirements
for_each: unit-of-work
scopes:
  classic: CONDITIONAL
  bugfix: SKIP
  refactor: SKIP
  security-patch: SKIP
  infra: EXECUTE
  express: SKIP
---

# NFR Design

## Prerequisites
- NFR Requirements must be complete for the unit
- NFR requirements artifacts must be available
- Execution plan must indicate NFR Design stage should execute

## Overview
Incorporate NFR requirements into unit design using patterns and logical components.

## Steps to Execute

### Step 1: Analyze NFR Requirements
- Read NFR requirements from `aidlc-docs/construction/{unit-name}/nfr-requirements/`
- Understand scalability, performance, availability, security needs

### Step 2: Create NFR Design Plan
- Generate plan with checkboxes [] for NFR design
- Focus on design patterns and logical components
- Each step should have a checkbox []

### Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the NFR requirements to identify ALL areas where clarification would improve NFR design quality. Be proactive in asking questions to ensure comprehensive non-functional design coverage.

**Evidence-First gate**: resolve anything explorable from the codebase and existing artifacts before asking (Evidence-First Policy, references/common/question-format-guide.md); only preference-driven or exploration-inconclusive items become questions.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect NFR design quality. It's better to ask too many questions than to make incorrect assumptions about non-functional patterns.

**MANDATORY**: Evaluate ALL of the following categories by asking targeted questions about each. For each category, determine applicability based on evidence from the NFR requirements -- do not skip categories without explicit justification:

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve pattern and component decisions
- **When in doubt, ask the question** - overconfidence leads to poor non-functional designs

**Question categories to evaluate** (consider ALL categories):
- **Resilience Patterns** - Ask about fault tolerance approach, retry strategies, and failure recovery expectations
- **Scalability Patterns** - Ask about scaling mechanisms, load boundaries, and growth projections
- **Performance Patterns** - Ask about optimization strategy, latency targets, and throughput requirements
- **Security Patterns** - Ask about security implementation approach, threat model, and compliance constraints
- **Logical Components** - Ask about infrastructure components (queues, caches, circuit breakers, etc.) and their integration patterns

### Step 4: Store Plan
- Save as `aidlc-docs/construction/plans/{unit-name}-nfr-design-plan.md`
- Include all [Answer]: tags for user input

### Step 5: Collect and Analyze Answers
- Collect answers per the Stage Question Posture (brief stage — auto-answer): select the `(Recommended)` option, write back with attribution and rationale per `question-format-guide.md`; escalated questions are asked via the structured question tool
- Review for vague or ambiguous responses
- Add follow-up questions if needed

### Step 6: Generate NFR Design Artifacts
- Create `aidlc-docs/construction/{unit-name}/nfr-design/nfr-design-patterns.md`
- Create `aidlc-docs/construction/{unit-name}/nfr-design/logical-components.md`

### Step 7: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🎨 NFR Design Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of NFR design
        - Format: "NFR design has incorporated [description]:"
        - List key design patterns implemented (bullet points)
        - List logical components and infrastructure elements
        - Mention resilience, scalability, and performance patterns applied
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📢 <u>**COMPLETION BRIEF:**</u>**  
> [unit-name] NFR design complete — artifacts at: `aidlc-docs/construction/[unit-name]/nfr-design/`
> Key decisions: [1-2 key decisions] · Notable risks: [or "none"]
> Brief-gate posture: proceeding without approval — object anytime in natural language.

---
```

### Step 8: Proceed (briefing gate)
- This stage is `gate: brief` (B18): the completion brief requests no approval — present it and proceed in the SAME interaction
- Append the audit entry: the brief summary is the audit record; no approval response exists to record
- Run `python <skill>/scripts/engine.py report --stage nfr-design --result completed` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-state.md` — they are engine-owned.
- **Per-unit note**: this stage is emitted once by the engine for the whole unit loop. Do the design work per unit (informative progress messages are fine), but present the completion brief ONCE and call `report` exactly once — after the LAST unit completes; fold per-unit highlights in (notable deviations only, not a recital)
- **Objection channel**: the user may object to the brief in natural language at any time — handle per the change flow (`references/common/workflow-changes.md`)

### Step 9: Log Interaction
- Log the brief presentation in `aidlc-docs/audit.md` with an ISO 8601 timestamp and the brief content summary
