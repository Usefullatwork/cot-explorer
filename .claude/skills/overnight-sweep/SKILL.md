---
name: overnight-sweep
description: >
  Comprehensive multi-pass quality sweep of a Python codebase. Covers security,
  PII, tests, coverage, data quality, code quality, and pipeline integrity. Use
  when user says "overnight sweep", "full quality scan", "codebase audit",
  "run all checks", or "quality sweep".
user-invocable: true
model: opus
effort: high
context: fork
argument-hint: "[scope: security|pii|tests|all]"
---

# Overnight Sweep

Comprehensive 8-pass quality sweep of a Python codebase. Run periodically or before releases.
Adapt paths and commands to the specific project.

## Pass 1: Security Audit

- Scan all `.py` files for hardcoded secrets, API keys, or credentials
- Check for bare `except:` clauses (mask errors, potential security risk)
- Check for dangerous functions: `eval()`, `exec()`, `pickle.loads()`, `os.system()`
- Verify API keys are sourced from environment variables, not hardcoded
- Pure stdlib project — no dependency audit needed (no pip packages)

## Pass 2: PII Leak Detection

- Scan all source files for PII patterns (emails, phones, API keys in strings)
- Verify `print()` statements do not expose API keys or tokens
- Check that `.env` files are in `.gitignore`
- Check JSON output files for accidental key/credential inclusion

## Pass 3: Secret Exposure

- Grep for API key patterns in committed files
- Verify `.gitignore` covers `.env`, `*.key`, `*.pem`
- Check `update.sh` for hardcoded credentials
- Verify environment variable usage is consistent across all scripts

## Pass 4: Test Results

```bash
pytest -v 2>&1 | tail -30
```

Report: total tests, pass/fail, duration

## Pass 5: Coverage Gaps

Analyze test files vs source files:

- List source files without corresponding test files
- Identify critical paths without tests (price fetching, scoring, setup generation)
- Check assertion quality (not just `assert True`)

## Pass 6: Data Quality

- Validate `data/macro/latest.json` schema (all 12 instruments present)
- Check for NaN, null, or zero prices in output
- Verify COT data freshness (should be from current week)
- Check that all API fallback chains work (TwelveData → Stooq → Yahoo)

## Pass 7: Code Quality

Scan for:

- Functions >80 lines (complexity risk)
- Files >500 lines (splitting needed)
- Duplicated code blocks (DRY violations)
- TODO/FIXME/HACK comments (tech debt)
- `print()` statements that should use `logging`
- Bare `except:` clauses (should catch specific exceptions)
- Missing docstrings on public functions

```bash
ruff check .
```

## Pass 8: Pipeline Integrity

- Verify `update.sh` stages run in correct order
- Check crontab schedule is active and correct
- Verify `git push` in `update.sh` targets correct remote/branch
- Check that `data/` directory has recent timestamps (pipeline is running)
- Verify `push_signals.py` has valid env var checks before sending

## Output

Generate report at: `reports/sweep-YYYY-MM-DD.md`

```markdown
# Sweep Report -- YYYY-MM-DD

## Summary

| Pass          | Status    | Findings       |
| ------------- | --------- | -------------- |
| Security      | PASS/FAIL | N issues       |
| PII           | PASS/FAIL | N issues       |
| Secrets       | PASS/FAIL | N issues       |
| Tests         | PASS/FAIL | N/M passed     |
| Coverage      | INFO      | N gaps         |
| Data Quality  | PASS/FAIL | N issues       |
| Code Quality  | INFO      | N items        |
| Pipeline      | PASS/FAIL | N issues       |

## Details

[Detailed findings per pass...]
```
