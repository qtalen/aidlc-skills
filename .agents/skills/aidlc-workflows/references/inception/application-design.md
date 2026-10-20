---
slug: application-design
phase: inception
execution: CONDITIONAL
condition:
  execute_if: new components or services needed, component methods and business rules need definition, service layer design required, component dependencies need clarification
  skip_if: changes within existing component boundaries, no new components or methods, pure implementation changes
gate: brief
produces:
  - inception/plans/application-design-plan.md
  - inception/application-design/components.md
  - inception/application-design/component-methods.md
  - inception/application-design/services.md
  - inception/application-design/component-dependency.md
  - inception/application-design/application-design.md
consumes:
  - artifact: inception/requirements/requirements.md
    required: true
  - artifact: inception/user-stories/stories.md
    required: false
  - artifact: inception/reverse-engineering/*
    required: false
    conditional_on: brownfield
requires_stage:
  - workflow-planning
  - requirements-analysis
scopes:
  classic: CONDITIONAL
  bugfix: SKIP
  refactor: SKIP
  security-patch: SKIP
  infra: SKIP
  express: SKIP
---

# Application Design - Detailed Steps

## Purpose
**High-level component identification and service layer design**

Application Design focuses on:
- Identifying main functional components and their responsibilities
- Defining component interfaces (not detailed business logic)
- Designing service layer for orchestration
- Establishing component dependencies and communication patterns

**Note**: Detailed business logic design happens later in Functional Design (per-unit, CONSTRUCTION phase)

## Prerequisites
- Workspace Detection must be complete
- Requirements Analysis recommended (provides functional context)
- User Stories recommended (user stories guide design decisions)
- Execution plan must indicate Application Design stage should execute

## Step-by-Step Execution

### 1. Analyze Context
- Read `aidlc-docs/inception/requirements/requirements.md` and `aidlc-docs/inception/user-stories/stories.md`
- Identify key business capabilities and functional areas
- Determine design scope and complexity

### 2. Create Application Design Plan
- Generate plan with checkboxes [] for application design
- Focus on components, responsibilities, methods, business rules, and services
- Each step and sub-step should have a checkbox []

### 3. Include Mandatory Design Artifacts in Plan
- **ALWAYS** include these mandatory artifacts in the design plan:
  - [ ] Generate components.md with component definitions and high-level responsibilities
  - [ ] Generate component-methods.md with method signatures (business rules detailed later in Functional Design)
  - [ ] Generate services.md with service definitions and orchestration patterns
  - [ ] Generate component-dependency.md with dependency relationships and communication patterns
  - [ ] Validate design completeness and consistency

### 4. Generate Context-Appropriate Questions
**DIRECTIVE**: Analyze the requirements and stories to generate questions relevant to THIS specific application design. Use the categories below as guidance. Evaluate each category and, when in doubt about applicability, ask the question rather than skipping it — overconfidence leads to poor outcomes.

**Evidence-First gate**: resolve anything explorable from the codebase and existing artifacts before asking (Evidence-First Policy, references/common/question-format-guide.md); only preference-driven or exploration-inconclusive items become questions.

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve design decisions
- **When in doubt, ask the question** - overconfidence leads to poor designs

**Question categories to evaluate** (consider ALL categories):
- **Component Identification** - Ask about component boundaries, organization, and grouping strategies
- **Component Methods** - Ask about method signatures, input/output expectations, and interface contracts (detailed business rules come later)
- **Service Layer Design** - Ask about service orchestration, boundaries, and coordination patterns
- **Component Dependencies** - Ask about communication patterns, dependency management, and coupling concerns
- **Design Patterns** - Ask about architectural style preferences, pattern choices, and design constraints

### 5. Store Application Design Plan
- Save as `aidlc-docs/inception/plans/application-design-plan.md`
- Include all [Answer]: tags for user input
- Ensure plan covers all design aspects

### 6. Request User Input
- Ask user to fill [Answer]: tags directly in the plan document
- Emphasize importance of design decisions
- Provide clear instructions on completing the [Answer]: tags

### 7. Collect Answers
- Collect answers per the Stage Question Posture (brief stage — auto-answer): select the `(Recommended)` option, write back with attribution and rationale per `question-format-guide.md`; escalated questions are asked via the structured question tool
- Do not proceed until ALL [Answer]: tags are filled (auto-answers count) and validated

### 8. ANALYZE ANSWERS (MANDATORY)
Before proceeding, you MUST carefully review all user answers for:
- **Vague or ambiguous responses**: "mix of", "somewhere between", "not sure", "depends"
- **Undefined criteria or terms**: References to concepts without clear definitions
- **Contradictory answers**: Responses that conflict with each other
- **Missing design details**: Answers that lack specific guidance
- **Answers that combine options**: Responses that merge different approaches without clear decision rules

### 9. MANDATORY Follow-up Questions
If the analysis in step 8 reveals ANY ambiguous answers, you MUST:
- Add specific follow-up questions to the plan document using [Answer]: tags
- DO NOT proceed to approval until all ambiguities are resolved
- Examples of required follow-ups:
  - "You mentioned 'mix of A and B' - what specific criteria should determine when to use A vs B?"
  - "You said 'somewhere between A and B' - can you define the exact middle ground approach?"
  - "You indicated 'not sure' - what additional information would help you decide?"
  - "You mentioned 'depends on complexity' - how do you define complexity levels?"

### 10. Generate Application Design Artifacts
- Execute the approved plan to generate design artifacts
- Create `aidlc-docs/inception/application-design/components.md` with:
  - Component name and purpose
  - Component responsibilities
  - Component interfaces
- Create `aidlc-docs/inception/application-design/component-methods.md` with:
  - Method signatures for each component
  - High-level purpose of each method
  - Input/output types
  - Note: Detailed business rules will be defined in Functional Design (per-unit, CONSTRUCTION phase)
- Create `aidlc-docs/inception/application-design/services.md` with:
  - Service definitions
  - Service responsibilities
  - Service interactions and orchestration
- Create `aidlc-docs/inception/application-design/component-dependency.md` with:
  - Dependency matrix showing relationships
  - Communication patterns between components
  - Data flow diagrams
- Create `aidlc-docs/inception/application-design/application-design.md` that consolidates the multiple design docs created above in a single doc.

### 11. Log Brief Presentation
- Log the brief presentation with timestamp in `aidlc-docs/audit.md`
- Include the brief content summary
- Use ISO 8601 timestamp format

### 12. Present Completion Message

```markdown
# 🏗️ Application Design Complete

[AI-generated summary of application design artifacts created in bullet points]

> **📡 <u>**COMPLETION BRIEF:**</u>**  
> Application design complete — artifacts at: `aidlc-docs/inception/application-design/`
> Key decisions: [1-2] · Notable risks: [or "none"] · Units Generation: [included / skipped per plan]
> Brief-gate posture: proceeding without approval — object anytime in natural language (e.g. to add the skipped Units Generation stage).
```

### 13. Proceed (briefing gate)
- This stage is `gate: brief` (B18): the completion brief requests no approval — present it and proceed in the SAME interaction
- Append the audit entry: the brief summary is the audit record; no approval response exists to record

### 14. Objection Channel
- The user may object to the brief in natural language at any time — handle per the change flow (`references/common/workflow-changes.md`)

### 15. Update Progress
- In the SAME interaction as the brief, run `python <skill>/scripts/engine.py report --stage application-design --result completed` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-docs/aidlc-state.md` — they are engine-owned.
- Prepare for transition to next stage
