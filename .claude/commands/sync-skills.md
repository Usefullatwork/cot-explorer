---
description: Check for and apply skill updates from ALL connected sources (GitHub repos, plugins, MCPs, npm)
---

Check for updates across all connected skill sources using the unified updater.

**NOTE:** This command now uses the unified update system. For the full experience,
use `/update` instead, which provides the same functionality with a richer table view.

## Steps

1. First, check what updates are available across all sources:
   ```bash
   node scripts/update.js --check --verbose
   ```
2. Review the update table with the user (shows GitHub repos, plugins, npm packages, MCPs).
3. If updates are available, show what will change by source type.
4. If the user confirms, apply updates:
   ```bash
   node scripts/update.js --force
   ```
5. After syncing, report:
   - How many sources were updated
   - How many new sources available
   - Any npm/plugin commands the user needs to run manually
6. The `.system-basics.json` config tracks sync state and update history.
7. Suggest reviewing any new or changed skills by reading their SKILL.md files.
