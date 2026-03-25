---
description: Add a GitHub repository as a skill source for manual updates
argument-hint: [GitHub URL or owner/repo]
---

$ARGUMENTS

Register a GitHub repository as a source for skills, agents, or commands.

## Steps

1. Parse the argument. Accepts:
   - `owner/repo` format (e.g., `obra/superpowers`)
   - Full GitHub URL (e.g., `https://github.com/obra/superpowers`)

2. If no argument provided, list currently tracked sources by reading `.system-basics.json`.

3. Verify the repo exists:
   ```bash
   git ls-remote https://github.com/<owner>/<repo> HEAD
   ```

4. Analyze the repo structure:
   - Check for `.claude/agents/`, `.claude/skills/`, `.claude/commands/`
   - Report what components are available

5. If user wants to install, clone and copy files:
   ```bash
   git clone --depth 1 https://github.com/<owner>/<repo> /tmp/sb2-source
   ```
   Then copy desired files into `.claude/` directories.

6. Update `.system-basics.json` to record the new source.

## Note

Source tracking is manual. Use `/update` to check for newer versions from registered sources.
