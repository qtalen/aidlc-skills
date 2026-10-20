---
slug: nfr-requirements
phase: construction
execution: CONDITIONAL
condition:
  execute_if: performance, security, or scalability requirements exist, monitoring or observability is needed, tech stack selection is required
  skip_if: no NFR requirements, tech stack already determined, existing NFR setup sufficient, simple changes with no NFR impact
gate: brief
produces:
  - construction/plans/{unit-name}-nfr-requirements-plan.md
  - construction/{unit-name}/nfr-requirements/nfr-requirements.md
  - construction/{unit-name}/nfr-requirements/tech-stack-decisions.md
consumes:
  - artifact: inception/requirements/requirements.md
    required: true
  - artifact: inception/application-design/unit-of-work.md
    required: true
  - artifact: construction/{unit-name}/functional-design/*
    required: true
requires_stage:
  - functional-design
  - requirements-analysis
  - units-generation
for_each: unit-of-work
scopes:
  classic: CONDITIONAL
  bugfix: SKIP
  refactor: SKIP
  security-patch: EXECUTE
  infra: EXECUTE
  express: SKIP
---

# NFR Requirements

## Prerequisites
- Units Generation must be complete, **or** the execution plan has no Units Generation stage — in that case this stage runs exactly once for the whole task as an implicit single unit (see `workflow-planning.md` Step 3.0), using `aidlc-docs/inception/requirements/requirements.md` and (brownfield) `aidlc-docs/inception/reverse-engineering/` artifacts as its inputs in place of unit artifacts
- Functional Design must be complete for the unit and its artifacts available, **or** the execution plan has no Functional Design stage — in that case work from `aidlc-docs/inception/requirements/requirements.md` and (brownfield) `aidlc-docs/inception/reverse-engineering/` artifacts instead
- Execution plan must indicate NFR Requirements stage should execute

## Overview
Determine non-functional requirements for the unit and make tech stack choices.

## Steps to Execute

### Step 1: Analyze Functional Design
- Read functional design artifacts from `aidlc-docs/construction/{unit-name}/functional-design/` (if the plan includes Functional Design)
- Understand business logic complexity and requirements

### Step 2: Create NFR Requirements Plan
- Generate plan with checkboxes [] for NFR assessment
- Focus on scalability, performance, availability, security
- Each step should have a checkbox []

### Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the functional design to identify ALL areas where NFR clarification would improve system quality and architecture decisions. Be proactive in asking questions to ensure comprehensive NFR coverage.

**Evidence-First gate**: resolve anything explorable from the codebase and existing artifacts before asking (Evidence-First Policy, references/common/question-format-guide.md); only preference-driven or exploration-inconclusive items become questions.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect system quality. It's better to ask too many questions than to make incorrect NFR assumptions.

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve NFR and tech stack decisions
- **When in doubt, ask the question** - overconfidence leads to poor system quality

**Question categories to evaluate** (consider ALL categories):
- **Scalability Requirements** - Ask about expected load, growth patterns, scaling triggers, and capacity planning
- **Performance Requirements** - Ask about response times, throughput, latency, and performance benchmarks
- **Availability Requirements** - Ask about uptime expectations, disaster recovery, failover, and business continuity
- **Security Requirements** - Ask about data protection, compliance, authentication, authorization, and threat models
- **Tech Stack Selection** - Ask about technology preferences, constraints, existing systems, and integration requirements
- **Reliability Requirements** - Ask about error handling, fault tolerance, monitoring, and alerting needs
- **Maintainability Requirements** - Ask about code quality, documentation, testing, and operational requirements
- **Usability Requirements** - Ask about user experience, accessibility, and interface requirements

### Step 4: Store Plan
- Save as `aidlc-docs/construction/plans/{unit-name}-nfr-requirements-plan.md`
- Include all [Answer]: tags for user input

### Step 5: Collect and Analyze Answers
- Collect answers per the Stage Question Posture (brief stage — auto-answer): select the `(Recommended)` option, write back with attribution and rationale per `question-format-guide.md`; escalated questions are asked via the structured question tool
- **MANDATORY**: Carefully review ALL responses for vague or ambiguous answers
- **CRITICAL**: Add follow-up questions for ANY unclear responses - do not proceed with ambiguity
- Look for responses like "depends", "maybe", "not sure", "mix of", "somewhere between", "standard", "typical"
- Create clarification questions file if ANY ambiguities are detected
- **Do not proceed until ALL ambiguities are resolved**

### Step 6: Generate NFR Requirements Artifacts
- Create `aidlc-docs/construction/{unit-name}/nfr-requirements/nfr-requirements.md`
- Create `aidlc-docs/construction/{unit-name}/nfr-requirements/tech-stack-decisions.md`

### Step 7: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 📊 NFR Requirements Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of NFR requirements
        - Format: "NFR requirements assessment has identified [description]:"
        - List key scalability, performance, availability requirements (bullet points)
        - List security and compliance requirements identified
        - Mention tech stack decisions and rationale
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📢 <u>**COMPLETION BRIEF:**</u>**  
> [unit-name] NFR requirements complete — artifacts at: `aidlc-docs/construction/[unit-name]/nfr-requirements/`
> Key decisions: [1-2 key decisions] · Notable risks: [or "none"]
> Brief-gate posture: proceeding without approval — object anytime in natural language.

---
```

### Step 8: Proceed (briefing gate)
- This stage is `gate: brief` (B18): the completion brief requests no approval — present it and proceed in the SAME interaction
- Append the audit entry: the brief summary is the audit record; no approval response exists to record
- Run `python <skill>/scripts/engine.py report --stage nfr-requirements --result completed` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-state.md` — they are engine-owned.
- **Per-unit note**: this stage is emitted once by the engine for the whole unit loop. Do the design work per unit (informative progress messages are fine), but present the completion brief ONCE and call `report` exactly once — after the LAST unit completes; fold per-unit highlights in (notable deviations only, not a recital)
- **Objection channel**: the user may object to the brief in natural language at any time — handle per the change flow (`references/common/workflow-changes.md`)

### Step 9: Log Interaction
- Log the brief presentation in `aidlc-docs/audit.md` with an ISO 8601 timestamp and the brief content summary
