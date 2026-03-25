Implement phase of the RPI workflow. Executes the approved plan file-by-file, running tests after each change and tracking progress.

## Usage

`/development:rpi-implement`

Requires `.planning/rpi-plan.md` to exist. Run `/development:rpi-plan` first.

## When to Use

After the plan has been approved by the user. This command is the only point in the RPI workflow where code is written. Never skip straight to this command — the research and plan phases exist to make this phase safe and predictable.

## How It Works

1. Read `CLAUDE.md` for project context
2. Check for `.planning/rpi-plan.md` — if missing, stop and print:
   `ERROR: .planning/rpi-plan.md not found. Run /development:rpi-plan first.`
3. Read the plan document in full
4. Read `.planning/rpi-progress.md` if it exists — resume from the last completed step rather than restarting
5. Resolve execution order from the plan's "Execution Order" section
6. For each file in order:
   a. Read the file before making any changes
   b. Apply the change specified in the plan's "Change Specifications" section
   c. Run the relevant tests (unit tests for the changed file, integration tests if specified in the plan)
   d. If tests pass: update `.planning/rpi-progress.md` (mark step complete, record files changed)
   e. If tests fail: STOP immediately — do not proceed to the next file. Present the failure to the user and ask how to proceed. Do not attempt a second fix without user input.
7. After all files are complete, run the full test suite once
8. Verify the acceptance criteria from the plan are met
9. Report completion: files changed, tests passing, acceptance criteria status

## Progress Document Structure

Write/update `.planning/rpi-progress.md` after each step:

```
# RPI Progress: [feature name]

## Status
IN PROGRESS / COMPLETE / BLOCKED

## Steps

| # | File | Status | Notes |
|---|------|--------|-------|
| 1 | src/foo.py | DONE | Tests: 12 pass |
| 2 | src/bar.py | IN PROGRESS | |
| 3 | tests/test_foo.py | PENDING | |

## Blocked On
[If status is BLOCKED: describe the test failure or blocker, what was tried, what user input is needed]

## Completed At
[Timestamp when all steps reach DONE]
```

## Stopping Rules

Stop and ask the user before continuing if ANY of the following occur:
- A test fails after a file change
- A file specified in the plan does not exist and needs to be created (confirm path)
- A change spec in the plan is ambiguous enough to require a design decision
- Applying a change would require modifying files NOT listed in the plan

## Subagent Instructions Template

You are an implementation subagent executing one step of an RPI plan.

Read CLAUDE.md first for project context.
Read .planning/rpi-plan.md for the full plan.
Read .planning/rpi-progress.md to confirm which step you are executing.

YOUR STEP: [step number and file path]

RULES:
- Read the target file before editing
- Apply ONLY the change described in the plan for this file
- Do NOT modify files outside your assigned step
- Run tests after your change: `pytest`
- Report: file changed, test result (pass/fail + count), any unexpected issues

## After Completion

Report: all steps completed (or which step blocked and why), final test suite result, acceptance criteria met (yes/no per criterion).
