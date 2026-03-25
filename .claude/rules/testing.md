# Testing Rules

## When Tests Are Required
- Every new function or endpoint gets at least one test
- Every bug fix gets a regression test BEFORE the fix (TDD)
- Every route handling user data gets auth tests

## Test Conventions (pytest)
- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_` prefix (e.g., `test_should_return_error_when_api_key_missing`)
- Test classes: `Test` prefix (e.g., `TestFetchPrices`)
- Shared fixtures: `conftest.py`
- Decorators: `@pytest.fixture`, `@pytest.mark.parametrize`, `@pytest.mark.skip(reason="...")`

## Test Quality
- Test behavior, not implementation (assert outputs, not internal calls)
- One assertion concept per test (multiple asserts are fine if testing one behavior)
- Test names describe the scenario: `test_should_return_empty_when_no_data`
- No `pytest.mark.skip` without a reason string explaining why

## Known Limitations
- No test infrastructure exists yet — first task should be creating `tests/` with `conftest.py`
- Document any known test infrastructure limitations in this file
- Expected failures should be noted so they're not confused with regressions
