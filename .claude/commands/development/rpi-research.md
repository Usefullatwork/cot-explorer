Research phase of the RPI workflow. Investigates a feature request before any code is written, then gives a GO/NO-GO recommendation.

## Usage

`/development:rpi-research [feature description]`

$ARGUMENTS

## When to Use

Run this as the first step any time you are about to start a non-trivial feature, refactor, or change that touches multiple files. Do not skip this phase — research surfaces blockers and ambiguities before they cost you implementation time.

## How It Works

1. Read `CLAUDE.md` for project context
2. Check `.planning/rpi-research.md` — if it already exists, confirm with the user whether to overwrite or append
3. Spawn 1–3 Explore subagents in parallel (scale to feature complexity) with `run_in_background: true`, each with a focused investigation scope:
   - **Agent A — Existing implementations**: Find any code that already does something similar. Look for related functions, modules, patterns, or prior attempts.
   - **Agent B — Dependencies and impact**: Identify every file, module, or system boundary that would be touched. Check for circular dependencies, third-party constraints, or migration requirements.
   - **Agent C — Test coverage** (spawn only if codebase has tests): Map current test coverage over the affected area. Flag gaps that would make safe implementation harder.
4. Wait for ALL agent results before proceeding
5. Synthesize findings into `.planning/rpi-research.md` using the structure below
6. Evaluate three dimensions and produce a GO/NO-GO verdict:
   - **Feasibility**: Can this be done with the current codebase and dependencies?
   - **Scope clarity**: Is the feature well-defined enough to plan without guessing?
   - **Risk level**: What is the blast radius if something goes wrong?
7. Present the verdict and summary to the user
8. Ask: "Approve to proceed to /development:rpi-plan, or provide feedback to refine?"
9. Wait for user approval before ending — do not auto-advance to the plan phase

## Research Document Structure

Write `.planning/rpi-research.md` with these sections:

```
# RPI Research: [feature name]

## Feature Description
[what was asked for]

## Existing Implementations
[relevant code found, file paths, function names]

## Dependencies and Impact
[files/modules affected, third-party constraints, migration needs]

## Test Coverage
[current coverage over affected area, gaps identified]

## Feasibility Assessment
[can this be done? what are the technical blockers?]

## Scope Clarity Assessment
[is the requirement well-defined? what is still ambiguous?]

## Risk Assessment
[blast radius, rollback difficulty, data migration concerns]

## Verdict
**GO** / **NO-GO** / **GO WITH CONDITIONS**

Reason: [one paragraph]

Conditions (if any):
- [condition 1]
- [condition 2]
```

## Subagent Instructions Template

You are an Explore agent investigating a feature request for the RPI research phase.

Read CLAUDE.md first for project context.

YOUR SCOPE: [A / B / C as described above]

FEATURE: [feature description]

RULES:
- Read files, search the codebase, use Glob and Grep
- Do NOT modify any files
- Do NOT write to .planning/ — the orchestrating agent handles that
- Return structured findings: file paths, function names, patterns found, gaps identified
- Be specific — vague findings are useless for planning

## After Completion

Report: verdict (GO/NO-GO/GO WITH CONDITIONS), key findings per dimension, path to research document.
