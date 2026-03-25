---
description: Run a structured two-stage code review by spawning the code-reviewer agent with the code-review skill preloaded. Pass a file path, directory, or branch name to audit.
argument-hint: "[file-or-directory-or-branch]"
---

# Code Audit

Run a comprehensive two-stage code review on the specified target.

## What Happens

1. This command spawns the `code-reviewer` agent
2. The agent has the `code-review` skill preloaded via its `skills: [code-review]` frontmatter field
3. The skill provides the two-stage review methodology (spec compliance then code quality)
4. The agent reviews the target and returns a structured report

## Instructions

Use the Agent tool to spawn the `code-reviewer` subagent with this prompt:

"Review the following target: $ARGUMENTS

Follow the code-review skill methodology:
- Stage 1: Check spec compliance (blocking gate — if this fails, skip Stage 2)
- Stage 2: Check code quality (only runs if Stage 1 passes)

Report findings with severity levels (critical/warning/info) and file:line references."

After the agent returns, summarize the key findings for the user:
- PASS/FAIL verdict for each stage
- Critical issues requiring immediate attention (if any)
- Top 3 suggested improvements
- Overall quality assessment
