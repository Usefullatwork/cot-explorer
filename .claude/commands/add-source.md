---
description: Add a GitHub repository as a skill source for auto-updates
argument-hint: [GitHub URL or owner/repo]
---

$ARGUMENTS

Add a new skill source to the update registry so that future `node scripts/update.js` calls will check it for updates.

## Steps

1. Parse the argument. Accepts:
   - `owner/repo` format (e.g., `obra/superpowers`)
   - Full GitHub URL (e.g., `https://github.com/obra/superpowers`)

2. If no argument is provided, list all currently tracked sources:
   ```bash
   node scripts/add-skill.js --list
   ```

3. If an argument is provided, add the source:
   ```bash
   node scripts/add-skill.js <argument>
   ```

   The script will:
   - Verify the repo exists on GitHub
   - Analyze the repo structure to detect skills, agents, commands
   - Add the entry to `scripts/skill-registry.json`

4. Ask the user if they want to install files immediately.
   - If yes: `node scripts/add-skill.js <argument> --install`
   - If no: just register for future update checks

5. Report what was added: repo name, detected type, file count.

6. Mention that `node scripts/update.js` will now check this source on every run.

## Optional Flags

- `--type <type>` -- Override detected type (skill, agents, skills+agents, framework, plugin, mcp, npm)
- `--name <name>` -- Override display name
- `--install` -- Download files immediately
