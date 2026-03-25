Quick system health check for the current project.

## Steps
1. Run `git status` — check branch and uncommitted changes
2. Check if tests pass (run `pytest` as specified in CLAUDE.md)
3. Check if build succeeds (if applicable)
4. Count files in `.planning/` — is there an active plan?
5. Check tool call counter at `/tmp/claude_tc`

## Output Format
HEALTH CHECK
Branch: [name] | Changes: [count]
Tests: PASS/FAIL | Build: PASS/FAIL/N/A
Plan: [active/none] | Tool calls: [count]
