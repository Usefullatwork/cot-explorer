---
name: rpi-workflow
description: Research-Plan-Implement development methodology for structured feature development. Loaded as background knowledge for development agents.
user-invocable: false
disable-model-invocation: true
---

# Research → Plan → Implement (RPI) Workflow

A three-phase development methodology that prevents wrong-approach rework by ensuring full context before any code changes. Each phase has a hard gate — the next phase cannot start until the current phase is approved.

---

## Phase 1: Research

**Goal**: Understand what exists before proposing anything new.

### What to Investigate
1. **Existing implementations** — Search codebase for similar features, patterns, utilities that can be reused
2. **Dependencies** — Map what the new feature touches: other modules, shared state, external APIs, database tables
3. **Test coverage** — Identify existing tests that will need updating and areas with no coverage
4. **Conventions** — Note coding patterns, naming conventions, and architectural decisions already in place
5. **Constraints** — Performance budgets, security requirements, backward compatibility, deployment considerations

### How to Research
- Spawn 1-3 Explore agents with focused search queries (one per concern area)
- Read relevant files directly — don't guess from filenames
- Check git history for recent changes in affected areas (`git log --oneline -20 -- path/to/area`)
- Read related test files to understand expected behavior

### Research Output
Write findings to `.planning/rpi-research.md`:

```markdown
# Research Findings: [Feature Name]

## Existing Implementations
- [file:line] — [what it does, how it relates]

## Dependencies
- [module/table/API] — [impact of our change]

## Test Coverage
- [area] — [covered/not covered, what tests exist]

## Conventions
- [pattern] — [where used, how to follow]

## Constraints
- [constraint] — [source of constraint, how it limits our approach]

## GO / NO-GO Recommendation
- Feasibility: [high/medium/low]
- Scope clarity: [clear/needs refinement/unclear]
- Risk: [low/medium/high — with specific risks listed]
- Recommendation: [GO / GO WITH CONDITIONS / NO-GO — with reason]
```

### Gate 1: User Approval
Present the research findings and GO/NO-GO recommendation. Wait for explicit approval before proceeding to Plan phase. If NO-GO, explain what additional research or scope changes are needed.

---

## Phase 2: Plan

**Goal**: Design the implementation before writing code.

### Multi-Perspective Analysis
Analyze the feature from three viewpoints:
1. **Product perspective** — User value, acceptance criteria, edge cases users will hit
2. **Engineering perspective** — Complexity, reusable code, testing strategy, performance implications
3. **Architecture perspective** — System impact, scalability, consistency with existing patterns, tech debt implications

### Plan Output
Write plan to `.planning/rpi-plan.md`:

```markdown
# Implementation Plan: [Feature Name]

## Acceptance Criteria
1. [Specific, testable criterion]

## Files to Modify
| File | Change | Reason | Tests Affected |
|------|--------|--------|----------------|
| path/to/file.ts | Add X method | Implements Y | test-file.test.ts |

## Execution Order
1. [file] — [why first: dependency/foundation]
2. [file] — [why second: depends on step 1]

## Test Plan
- [ ] Unit: [what to test]
- [ ] Integration: [what to test]
- [ ] Edge cases: [specific scenarios]

## Rollback Plan
If implementation fails: [specific revert steps]

## Out of Scope
- [Explicitly listed items NOT included in this implementation]
```

### Gate 2: User Approval
Present the plan. Wait for explicit approval. If changes requested, update plan and re-present. No code changes until approved.

---

## Phase 3: Implement

**Goal**: Execute the approved plan with verification after every step.

### Execution Rules
1. Follow the plan's execution order exactly
2. Read each file before modifying it
3. Run relevant tests after each file change
4. Write progress to `.planning/rpi-progress.md` after each step
5. If a test fails — STOP. Do not continue to the next file. Diagnose and fix, or ask user.
6. If you need to modify a file NOT in the plan — STOP. Ask user to approve the scope expansion.

### Progress Tracking
Update `.planning/rpi-progress.md` after each step:

```markdown
# Implementation Progress

## Step 1: [file] — DONE ✓
- Change: [what was done]
- Tests: 5/5 passing

## Step 2: [file] — IN PROGRESS
- Change: [what is being done]
- Tests: pending
```

### Post-Implementation
After all steps complete:
1. Run full test suite for affected area
2. Compare result against the plan's acceptance criteria
3. Report any deviations from the approved plan
4. Suggest follow-up work (if any) for a separate RPI cycle

---

## Agent Assignments

| Phase | Agent Type | Purpose |
|-------|-----------|---------|
| Research | Explore (1-3) | Codebase investigation, pattern discovery |
| Research | research-lead | Synthesis and GO/NO-GO recommendation |
| Plan | Plan | Multi-perspective design |
| Implement | backend-dev / frontend-dev | Code changes |
| Implement | test-analyzer | Test verification |
| All | chief-of-staff | Cross-project coordination (if multi-project) |

---

## When to Use RPI vs. Simpler Workflows

| Scenario | Workflow |
|----------|---------|
| Single file change | Direct edit (no RPI needed) |
| 2-3 file change | design-first skill (lighter gate) |
| New feature (3+ files) | Full RPI |
| Bug fix | TDD (write failing test → fix → verify) |
| Refactor | RPI with extra emphasis on test coverage in Research phase |
