---
name: overnight-sweep
description: >
  Comprehensive multi-pass quality sweep of a codebase. Covers security, PII,
  GDPR, tests, coverage, accessibility, code quality, and i18n. Use when user
  says "overnight sweep", "full quality scan", "codebase audit", "run all checks",
  or "quality sweep".
user-invocable: true
model: opus
effort: high
context: fork
argument-hint: "[scope: security|pii|tests|all]"
---

# Overnight Sweep

Comprehensive 8-pass quality sweep of a codebase. Run periodically or before releases.
Adapt paths and commands to the specific project.

## Pass 1: Security Audit

```bash
npm audit --omit=dev
```

- Report critical and high vulnerabilities
- Check for known CVEs in dependencies
- Verify no `*` versions in package.json

## Pass 2: PII Leak Detection

- Scan all source files for PII patterns (emails, phones, SSNs, API keys)
- Check database queries for over-fetching sensitive fields
- Verify logging does not expose sensitive data
- Check API responses for password/token leaks

## Pass 3: GDPR Compliance

- Verify account deletion cascade works
- Check data export endpoints exist
- Verify consent mechanisms
- Check data retention policies

## Pass 4: Test Results

```bash
# Adapt commands to project structure
npm test 2>&1 | tail -20
```

Report: total tests, pass/fail, duration per workspace

## Pass 5: Coverage Gaps

Analyze test files vs source files:

- List source files without corresponding test files
- Identify critical paths without tests (auth, payment, upload)
- Check assertion quality (not just `toBeTruthy`)

## Pass 6: Accessibility Violations

- Run axe-core tests if available
- Check ARIA attributes on interactive components
- Verify keyboard navigation paths
- Check color contrast values

## Pass 7: Code Quality

Scan for:

- Functions >80 lines (complexity risk)
- Duplicated code blocks (DRY violations)
- TODO/FIXME/HACK comments (tech debt)
- Dead code (unreachable branches, unused exports)
- TypeScript `any` usage (type safety gaps)
- `console.log` in production code

## Pass 8: i18n Consistency

- Compare locale JSON files across all supported languages
- Report missing keys in any language
- Check for hardcoded strings in components (should use `t()`)
- Verify `lang` attribute correctness on pages

## Output

Generate report at: `reports/sweep-YYYY-MM-DD.md`

```markdown
# Sweep Report -- YYYY-MM-DD

## Summary

| Pass          | Status    | Findings       |
| ------------- | --------- | -------------- |
| Security      | PASS/FAIL | N issues       |
| PII           | PASS/FAIL | N issues       |
| GDPR          | PASS/FAIL | N issues       |
| Tests         | PASS/FAIL | N/M passed     |
| Coverage      | INFO      | N gaps         |
| Accessibility | PASS/FAIL | N issues       |
| Code Quality  | INFO      | N items        |
| i18n          | PASS/FAIL | N missing keys |

## Details

[Detailed findings per pass...]
```