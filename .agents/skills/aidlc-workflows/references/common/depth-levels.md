# Adaptive Depth

**Purpose**: Explain how AI-DLC adapts detail level to problem complexity

## Core Principle

**When a stage executes, ALL its defined artifacts are created. The "depth" refers to the level of detail and rigor within those artifacts, which adapts to the problem's complexity.**

## Stage Selection vs Detail Level

### Stage Selection (Two Layers)
- **Requirements Analysis** selects the **workflow scope** (classic/bugfix/refactor/security-patch/infra/express), which supplies the starting EXECUTE/SKIP/CONDITIONAL plan and the default depth
- **Workflow Planning** takes the scope's baseline, decides CONDITIONAL stages from project context, and fine-tunes individual stages
- The user may add or remove stages at any gate
- **If EXECUTE**: Stage runs and creates ALL its defined artifacts
- **If SKIP**: Stage doesn't run at all

### Detail Level (Adaptive)
- **Simple problems**: Concise artifacts with essential detail
- **Complex problems**: Comprehensive artifacts with extensive detail
- **Model decides**: Based on problem characteristics, not prescriptive rules

## Factors Influencing Detail Level

The model considers these factors when determining appropriate detail:

1. **Request Clarity**: How clear and complete is the user's request?
2. **Problem Complexity**: How intricate is the solution space?
3. **Change footprint**: Single file, component, multiple components, or system-wide?
4. **Risk Level**: What's the impact of errors or omissions?
5. **Available Context**: Greenfield vs brownfield, existing documentation
6. **User Preferences**: Has user expressed preference for brevity or detail?

## Example: Requirements Analysis Artifacts

**All scenarios create the same artifacts**:
- `requirement-verification-questions.md` (if needed)
- `requirements.md`

**Note**: User's initial request is captured in `audit.md` (no separate user-intent.md needed)

**Detail level varies by complexity**:

### Simple Scenario (Bug Fix)
- **requirement-verification-questions.md**: necessary clarifying questions
- **requirements.md**: Concise functional requirement, minimal sections

### Complex Scenario (System Migration)
- **requirement-verification-questions.md**: Multiple rounds, 10+ questions
- **requirements.md**: Comprehensive functional + non-functional requirements, traceability, acceptance criteria

## Example: Application Design Artifacts

**All scenarios create the same artifacts** (the authoritative list is the stage's frontmatter `produces`):
- `application-design-plan.md`
- `components.md`, `component-methods.md`, `services.md`, `component-dependency.md`
- `application-design.md`

**Detail level varies by complexity**:

### Simple Scenario (Single Component)
- **application-design.md**: Basic component description, key methods
- **components.md**: Essential components and their relationships, briefly described

### Complex Scenario (Multi-Component System)
- **application-design.md**: Detailed component responsibilities, all methods with signatures, design patterns, alternatives considered
- **components.md** / **component-dependency.md**: All relationships, data flows, and integration points comprehensively mapped

## Guiding Principle for Model

**"Create exactly the detail needed for the problem at hand - no more, no less."**

- Don't artificially inflate simple problems with unnecessary detail
- Don't shortchange complex problems by omitting critical detail
- Let problem characteristics drive detail level naturally
- All required artifacts are always created when stage executes
