# Coding Style

## File Limits
- Max 500 lines per file (split if exceeding)
- Max 80 lines per function (extract helpers if exceeding)
- Max 3 levels of nesting (refactor with early returns)

## Naming
- **Variables/functions/methods**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Files/modules**: snake_case (e.g., `fetch_prices.py`)
- **Packages/directories**: snake_case or kebab-case

## Imports
- Group in order: standard library, third-party packages, local modules
- Separate groups with a blank line
- Prefer explicit imports over wildcard (`from module import *` is forbidden)
- Use absolute imports for cross-module references

## Formatting
- Use ruff for formatting (`ruff format .`)
- Follow PEP 8 conventions
- 4 spaces for indentation (no tabs)
- Line length: 88 characters (ruff default)

## Error Handling
- Always catch specific exceptions (no bare `except:`)
- Catch blocks must provide context, not just re-raise
- Never swallow errors silently (`except: pass` is forbidden)
- Use `logging` module for error reporting, not `print()`

## Comments
- Only where logic is non-obvious
- No commented-out code (delete it, git has history)
- TODO format: `# TODO(username): description`
