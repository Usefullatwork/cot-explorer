Scan for technical debt in the codebase.

## Steps
1. Search for TODO/FIXME/HACK/XXX comments
2. Check for files over 500 lines
3. Check for functions over 80 lines
4. Look for debug `print()` statements in source (not test) `.py` files
5. Check for any `pytest.mark.skip` tests
6. Look for commented-out code blocks
7. Check for unused imports or variables

## Output Format
TECH DEBT REPORT
TODOs: [count] | FIXMEs: [count] | HACKs: [count]
Large files (>500 lines): [list]
Large functions (>80 lines): [list]
Debug prints: [count]
Skipped tests: [count]
Commented code blocks: [count]
