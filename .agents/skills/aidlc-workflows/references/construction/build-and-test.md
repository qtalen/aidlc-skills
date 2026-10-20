---
slug: build-and-test
phase: construction
execution: ALWAYS
condition: Always executes after all units complete — generates comprehensive build and test instructions for all units
gate: brief
review_class: code-quality
produces:
  - construction/build-and-test/build-instructions.md
  - construction/build-and-test/unit-test-instructions.md
  - construction/build-and-test/integration-test-instructions.md
  - construction/build-and-test/performance-test-instructions.md
  - construction/build-and-test/contract-test-instructions.md
  - construction/build-and-test/security-test-instructions.md
  - construction/build-and-test/e2e-test-instructions.md
  - construction/build-and-test/build-and-test-summary.md
consumes:
  - artifact: construction/{unit-name}/code/*
    required: true
requires_stage:
  - code-generation
scopes:
  classic: EXECUTE
  bugfix: EXECUTE
  refactor: EXECUTE
  security-patch: EXECUTE
  infra: EXECUTE
  express: EXECUTE
---

# Build and Test

**Purpose**: Build all units and execute comprehensive testing strategy

## Prerequisites
- Code Generation must be complete for all units
- All code artifacts must be generated
- Project is ready for build and testing

---

## Step 1: Analyze Testing Requirements

Analyze the project to determine appropriate testing strategy:
- **Unit tests**: Already generated per unit during code generation
- **Integration tests**: Test interactions between units/services
- **Performance tests**: Load, stress, and scalability testing
- **End-to-end tests**: Complete user workflows
- **Contract tests**: API contract validation between services
- **Security tests**: Vulnerability scanning, penetration testing

---

## Step 2: Generate Build Instructions

Create `aidlc-docs/construction/build-and-test/build-instructions.md`:

```markdown
# Build Instructions

## Prerequisites
- **Build Tool**: [Tool name and version]
- **Dependencies**: [List all required dependencies]
- **Environment Variables**: [List required env vars]
- **System Requirements**: [OS, memory, disk space]

## Build Steps

### 1. Install Dependencies
\`\`\`bash
[Command to install dependencies]
# Example: npm install, mvn dependency:resolve, pip install -r requirements.txt
\`\`\`

### 2. Configure Environment
\`\`\`bash
[Commands to set up environment]
# Example: export variables, configure credentials
\`\`\`

### 3. Build All Units
\`\`\`bash
[Command to build all units]
# Example: mvn clean install, npm run build, brazil-build
\`\`\`

### 4. Verify Build Success
- **Expected Output**: [Describe successful build output]
- **Build Artifacts**: [List generated artifacts and locations]
- **Common Warnings**: [Note any acceptable warnings]

## Troubleshooting

### Build Fails with Dependency Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]

### Build Fails with Compilation Errors
- **Cause**: [Common causes]
- **Solution**: [Step-by-step fix]
```

---

## Step 3: Generate Unit Test Execution Instructions

Create `aidlc-docs/construction/build-and-test/unit-test-instructions.md`:

```markdown
# Unit Test Execution

## Run Unit Tests

### 1. Execute All Unit Tests
\`\`\`bash
[Command to run all unit tests]
# Example: mvn test, npm test, pytest tests/unit
\`\`\`

### 2. Review Test Results
- **Expected**: [X] tests pass, 0 failures
- **Test Coverage**: [Expected coverage percentage]
- **Test Report Location**: [Path to test reports]

### 3. Fix Failing Tests
If tests fail:
1. Review test output in [location]
2. Identify failing test cases
3. Fix code issues
4. Rerun tests until all pass
```

---

## Step 4: Generate Integration Test Instructions

Create `aidlc-docs/construction/build-and-test/integration-test-instructions.md`:

```markdown
# Integration Test Instructions

## Purpose
Test interactions between units/services to ensure they work together correctly.

## Test Scenarios

### Scenario 1: [Unit A] → [Unit B] Integration
- **Description**: [What is being tested]
- **Setup**: [Required test environment setup]
- **Test Steps**: [Step-by-step test execution]
- **Expected Results**: [What should happen]
- **Cleanup**: [How to clean up after test]

### Scenario 2: [Unit B] → [Unit C] Integration
[Similar structure]

## Setup Integration Test Environment

### 1. Start Required Services
\`\`\`bash
[Commands to start services]
# Example: docker-compose up, start test database
\`\`\`

### 2. Configure Service Endpoints
\`\`\`bash
[Commands to configure endpoints]
# Example: export API_URL=http://localhost:8080
\`\`\`

## Run Integration Tests

### 1. Execute Integration Test Suite
\`\`\`bash
[Command to run integration tests]
# Example: mvn integration-test, npm run test:integration
\`\`\`

### 2. Verify Service Interactions
- **Test Scenarios**: [List key integration test scenarios]
- **Expected Results**: [Describe expected outcomes]
- **Logs Location**: [Where to check logs]

### 3. Cleanup
\`\`\`bash
[Commands to clean up test environment]
# Example: docker-compose down, stop test services
\`\`\`
```

---

## Step 5: Generate Performance Test Instructions (If Applicable)

Create `aidlc-docs/construction/build-and-test/performance-test-instructions.md`:

```markdown
# Performance Test Instructions

## Purpose
Validate system performance under load to ensure it meets requirements.

## Performance Requirements
- **Response Time**: < [X]ms for [Y]% of requests
- **Throughput**: [X] requests/second
- **Concurrent Users**: Support [X] concurrent users
- **Error Rate**: < [X]%

## Setup Performance Test Environment

### 1. Prepare Test Environment
\`\`\`bash
[Commands to set up performance testing]
# Example: scale services, configure load balancers
\`\`\`

### 2. Configure Test Parameters
- **Test Duration**: [X] minutes
- **Ramp-up Time**: [X] seconds
- **Virtual Users**: [X] users

## Run Performance Tests

### 1. Execute Load Tests
\`\`\`bash
[Command to run load tests]
# Example: jmeter -n -t test.jmx, k6 run script.js
\`\`\`

### 2. Execute Stress Tests
\`\`\`bash
[Command to run stress tests]
# Example: gradually increase load until failure
\`\`\`

### 3. Analyze Performance Results
- **Response Time**: [Actual vs Expected]
- **Throughput**: [Actual vs Expected]
- **Error Rate**: [Actual vs Expected]
- **Bottlenecks**: [Identified bottlenecks]
- **Results Location**: [Path to performance reports]

## Performance Optimization

If performance doesn't meet requirements:
1. Identify bottlenecks from test results
2. Optimize code/queries/configurations
3. Rerun tests to validate improvements
```

---

## Step 6: Generate Additional Test Instructions (As Needed)

Based on project requirements, generate additional test instruction files:

### Contract Tests (For Microservices)
Create `aidlc-docs/construction/build-and-test/contract-test-instructions.md`:
- API contract validation between services
- Consumer-driven contract testing
- Schema validation

### Security Tests
Create `aidlc-docs/construction/build-and-test/security-test-instructions.md`:
- Vulnerability scanning
- Dependency security checks
- Authentication/authorization testing
- Input validation testing

### End-to-End Tests
Create `aidlc-docs/construction/build-and-test/e2e-test-instructions.md`:
- Complete user workflow testing
- Cross-service scenarios
- UI testing (if applicable)

---

## Step 7: Generate Test Summary

Create `aidlc-docs/construction/build-and-test/build-and-test-summary.md`:

```markdown
# Build and Test Summary

## Build Status
- **Build Tool**: [Tool name]
- **Build Status**: [Success/Failed]
- **Build Artifacts**: [List artifacts]
- **Build Time**: [Duration]

## Test Execution Summary

### Unit Tests
- **Total Tests**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Coverage**: [X]%
- **Status**: [Pass/Fail]

### Integration Tests
- **Test Scenarios**: [X]
- **Passed**: [X]
- **Failed**: [X]
- **Status**: [Pass/Fail]

### Performance Tests
- **Response Time**: [Actual] (Target: [Expected])
- **Throughput**: [Actual] (Target: [Expected])
- **Error Rate**: [Actual] (Target: [Expected])
- **Status**: [Pass/Fail]

### Additional Tests
- **Contract Tests**: [Pass/Fail/N/A]
- **Security Tests**: [Pass/Fail/N/A]
- **E2E Tests**: [Pass/Fail/N/A]

## Overall Status
- **Build**: [Success/Failed]
- **All Tests**: [Pass/Fail]
- **Ready for Operations**: [Yes/No]

## Next Steps
[If all pass]: Build and test verified; the engine's `next` directive decides what follows (Operations applies only in scopes/plans that include it)
[If failures]: Address failing tests and rebuild
```

---

## Step 8: Update State Tracking

Stage progress is engine-owned. In the SAME interaction as the completion brief (Step 9) and the commit-authorization answer, run `python <skill>/scripts/engine.py report --stage build-and-test --result completed` (fall back to `python3` if `python` is unavailable). Never hand-edit the Stage Progress / Current Status sections of `aidlc-docs/aidlc-state.md` — they are engine-owned.

---

## Step 9: Present Results to User

**Pre-brief review (mandatory, `review_class: code-quality`)**: before presenting the completion message below — i.e., before the commit plan and the authorization question — delegate a code-quality review per `references/common/review-delegation.md` (RV-01 completion verification) over the code produced this round (paths per the RV-02 anchor table: this round's unit plans or the diff; the design/requirements artifacts are the comparison surface). Code changes resulting from review findings must re-run the affected tests and update `build-and-test-summary.md` (DOC-03) BEFORE the brief is presented — otherwise the review line renders `unreviewed-after-fix` (RV-06 fix re-feed).

Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔨 Build and Test Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of build and test results
        - Format: "Build and test has completed with the following results:"
        - List build status and artifacts
        - List test results by category (unit, integration, performance, etc.)
        - List generated instruction files
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📡 <u>**COMPLETION BRIEF:**</u>**  
> Build and test complete — summary at: `aidlc-docs/construction/build-and-test/build-and-test-summary.md`
> Key results: [tests X/Y green — 1-2 highlights] · Notable risks: [or "none"]
> Brief-gate posture: proceeding without approval — the commit plan below asks its own authorization question.
> Review (code-quality): [one line per RV-08 — status + content, e.g. `zero blocking (rubric code-quality)` or `reviewed (tier ②, L1) — 1 blocking fixed + diff-verified (see reviews.md R-007)`]

---
```

### Commit Protocol

Timing is fixed: the completion brief presents the commit plan in its body → the commit-authorization question is asked via the structured question tool in the SAME interaction (execute the commit plan / the user handles commits manually / no git writes now) → only then run `python <skill>/scripts/engine.py report --stage build-and-test --result completed` (per Step 8) → execute the commit plan per the answer. The plan is never presented after the question is answered, and no git write happens before `report completed`.

- The commit authorization is a genuine human-only fork (history writes) — an escalated question under the brief-gate posture (workflow-conventions Group 5, BRF-01), never an automatic action. **Never commit automatically** (unconditional discipline, owned by the Completion Ritual): the message always lists the pending-to-commit inventory and the user decides.
- **"User handles commits manually" or "no git writes now" answers** → execute NO git write operations.

Protocol:

1. **Dirty-file triage**: classify every dirty workspace path by whether this session's tool calls actually wrote it. First class: artifacts produced by this workflow. Every other dirty file is second class — list it, NEVER stage it silently.
2. **One-shot commit plan presentation**: list first-class files grouped by their owning stage and unit; list second-class files as a plain inventory (never staged automatically). `aidlc-docs/reviews.md` rides the commit batch as workflow bookkeeping owned by no stage (RV-07) — list it as its own line so it is never dropped as an orphan.
3. **Products with an iteration roadmap (iteration-boundary batch)**: the commit batch includes `aidlc-docs/inception/product-design/product-design.md` with the current iteration marked `shipped` and its Shipped Log rollup line already written — the marking happens at this ship transition moment (see `workflow-changes.md`, Iteration Completion Ritual), which the completion brief's commit batch anchors. This applies to ANY product carrying an iteration roadmap, including a single-iteration one (N=1 marks its only row; its completion ritual takes Branch 2). Non-git workspaces: the git protocol is skipped per rule 5; the shipped marking (a workflow action) still happens.
4. **No amend, no push** — unless the user explicitly asks.
5. **Non-git workspace**: align with the AUD-02 precedent — no git → mark commit information `unknown`, do not block the flow, and skip this entire protocol.
6. **Audit**: write the commit plan and its confirmation outcome to `audit.md`; record the resulting commit hashes in `build-and-test-summary.md`.
7. **Commit order**: commit work results first; IF any archival/handoff pending items exist at that point, commit them afterward (conditional — at build-and-test time these typically do not exist).

---

## Step 10: Log Interaction

**MANDATORY**: Log the stage completion in `aidlc-docs/audit.md`:

```markdown
## Build and Test Stage
**Timestamp**: [ISO timestamp]
**Build Status**: [Success/Failed]
**Test Status**: [Pass/Fail]
**Files Generated**:
- build-instructions.md
- unit-test-instructions.md
- integration-test-instructions.md
- performance-test-instructions.md
- build-and-test-summary.md

---
```
