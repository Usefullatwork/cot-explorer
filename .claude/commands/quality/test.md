Run the project's test suite and report results.

$ARGUMENTS

## Steps
1. Check for `conftest.py` or `tests/` directory to confirm pytest is available
2. If $ARGUMENTS specified, run tests matching that pattern: `pytest -k "$ARGUMENTS"`
3. Otherwise run full suite: `pytest`
4. Report: total, passed, failed, skipped
5. If failures: show first 3 failure details
6. If no tests exist yet: report "No test infrastructure found. Consider creating tests/ directory with conftest.py."
