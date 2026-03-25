Plan phase of the RPI workflow. Turns research findings into a concrete, reviewable implementation plan before any code is touched.

## Usage

`/development:rpi-plan`

Requires `.planning/rpi-research.md` to exist. Run `/development:rpi-research [feature]` first.

## When to Use

After research is complete and the user has approved a GO verdict. Do not skip this phase — a written plan prevents scope creep, ensures the right execution order, and gives you a rollback reference if implementation goes wrong.

## How It Works

1. Read `CLAUDE.md` for project context
2. Check for `.planning/rpi-research.md` — if missing, stop and print:
   `ERROR: .planning/rpi-research.md not found. Run /development:rpi-research [feature] first.`
3. Read the research document in full
4. Analyze the feature from three perspectives in parallel using subagents with `run_in_background: true`:
   - **Product agent**: User value, acceptance criteria, edge cases, definition of done
   - **Engineering agent**: Implementation complexity, test strategy, execution order, technical risks
   - **Architecture agent**: System impact, interface changes, data model changes, performance considerations
5. Wait for ALL agent results before proceeding
6. Synthesize into `.planning/rpi-plan.md` using the structure below
7. Present the plan to the user as a numbered task list with estimated scope per task
8. Ask: "Approve this plan to proceed to /development:rpi-implement, or request changes?"
9. Wait for explicit user approval — do not auto-advance to implementation

## Plan Document Structure

Write `.planning/rpi-plan.md` with these sections:

```
# RPI Plan: [feature name]

## Acceptance Criteria
- [ ] [criterion 1 — observable, testable]
- [ ] [criterion 2]

## Files to Change
| File | Change Type | Description |
|------|-------------|-------------|
| src/foo.py | modify | Add X function |
| src/bar.py | create | New module for Y |
| tests/test_foo.py | modify | Add tests for X |

## Change Specifications

### [file path]
[Describe exactly what changes: function signatures, new exports, modified logic. Be precise enough that implementation requires no guessing.]

## Test Plan
- Unit: [what to unit test and where]
- Integration: [what to integration test]
- Manual: [anything requiring manual verification]

## Execution Order
1. [file/step] — reason for this position in the order
2. [file/step]
3. ...

## Rollback Plan
[How to revert if implementation goes wrong. Git commands, data cleanup steps, feature flag if applicable.]

## Out of Scope
[Explicitly list what this plan does NOT cover, to prevent scope creep.]
```

## Subagent Instructions Template

You are a planning agent contributing one perspective to an RPI plan.

Read CLAUDE.md first for project context.
Read .planning/rpi-research.md for the research findings.

YOUR PERSPECTIVE: [Product / Engineering / Architecture]

RULES:
- Read files, do NOT modify anything
- Return structured analysis focused on your assigned perspective
- Flag conflicts or gaps you notice in the research
- Be concrete — "add a validate_email() function to src/utils/validation.py" not "add validation"

## After Completion

Report: plan document path, task count, any open questions that need user decision before implementation starts.
