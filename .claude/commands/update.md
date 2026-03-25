---
description: Check all connected skill repos, plugins, MCPs, and npm packages for updates and apply them
---

Run the unified System Basics V2 updater to check ALL connected sources for updates.

## Steps

1. Run the unified update checker to see what is available:
   ```bash
   node scripts/update.js --check --verbose
   ```

2. Show the update table to the user. The table groups sources by status:
   - **UPDATE** -- newer version available
   - **NEW** -- source not yet installed locally
   - **OK** -- up to date
   - **ERROR** -- could not check (network, rate limit, etc.)

3. Ask the user which updates to apply:
   - "all" -- apply everything
   - Specific source names -- only those
   - "none" -- cancel

4. Apply the selected updates:
   - For "all": `node scripts/update.js --force`
   - For specific types: `node scripts/update.js --force skills` (or agents, plugins, npm)
   - For npm packages: show the user the npm install commands to run manually
   - For plugins: show the user the `claude plugins update` commands to run manually

5. After applying, verify the update succeeded:
   ```bash
   node scripts/update.js --check
   ```

6. Report summary: how many updated, how many new, any errors.

## Source Types

The updater checks these source categories:
- **GitHub repos** -- skills, agents, commands from tracked repositories
- **Claude Code plugins** -- from ~/.claude/plugins/installed_plugins.json
- **npm packages** -- MCP servers and CLI tools
- **Local skills** -- skills with their own package.json

## Environment

Set `GITHUB_TOKEN` for higher API rate limits (5000/hr vs 60/hr unauthenticated).
