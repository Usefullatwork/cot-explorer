# Permission Mode Rules

## Default Mode: bypassPermissions

This project runs with `bypassPermissions` as the default session mode (set in `.claude/settings.json`).
Claude should NOT downgrade to `acceptEdits` or `default` mode during a session.

## When to use plan mode

Switch to `plan` mode ONLY when:
- A multi-file refactor needs design review
- An architectural decision needs user input
- A security concern needs explicit approval

## When NOT to switch modes

Do NOT switch to `acceptEdits` or `default` for:
- Standard file edits (Edit/Write)
- Running tests (pytest, ruff)
- Git operations (add, commit, status, diff)
- File operations (rm, cp, mv, mkdir)
- Any Bash command in the allow list

## Agent permission modes

- Implementation agents (backend-dev, overnight-worker, scraper): `bypassPermissions`
- Review agents (code-reviewer, compliance-scanner, test-analyzer): `plan`
- Coordination agents (chief-of-staff, research-lead, parallel-dispatcher): `plan`
