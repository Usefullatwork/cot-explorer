Pre-merge checklist for the current feature branch.

## Steps

1. **Run all tests** (`pytest` if tests exist, note if no test infrastructure)

2. **Check for debug artifacts:**
   - Search for `print(` in source `.py` files (excluding tests)
   - Search for `TODO`, `FIXME`, `HACK`, `XXX` in source files

3. **Verify lint** (`ruff check .`)

4. **Show summary:**
   - Branch name and commit count vs main
   - Files changed (`git diff --stat main`)
   - Test results (pass/fail counts)
   - Any warnings found in step 2

5. **Present options:**

   Only if ALL tests pass (or no tests exist) and lint succeeds:

   - **A) Squash merge** — `git checkout main && git merge --squash <branch> && git commit`
   - **B) Regular merge** — `git checkout main && git merge <branch>`
   - **C) Push for PR** — `git push -u origin <branch>` then `gh pr create`
   - **D) Keep working** — Stay on branch, list remaining issues

   If tests fail or lint broken:
   - Show failures and suggest fixes
   - Only offer option D
