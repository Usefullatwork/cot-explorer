Pre-release verification checklist.

## Steps
1. Ensure you're on main branch (or release branch)
2. Run full test suite (`pytest`) — ALL must pass (or note if no tests exist)
3. Run lint (`ruff check .`) — must have no errors
4. Check for uncommitted changes — must be clean
5. Check git log for unreleased commits since last tag
6. Look for any FIXME/TODO tagged as release-blocking
7. Verify `update.sh` runs without errors
8. Verify `data/` directory is populated with recent data

## Output
RELEASE CHECK
Branch: [name] | Clean: [yes/no]
Tests: [pass/fail/none] | Lint: [pass/fail]
Unreleased commits: [count]
Blocking issues: [count or none]
Data populated: [yes/no]
Ready to release: YES/NO
