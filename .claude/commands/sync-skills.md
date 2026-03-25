---
description: Check for and apply skill updates from registered sources
---

Check for updates across registered skill sources.

**NOTE:** This command uses the same update system as `/update`. For the full experience, use `/update` instead.

## Steps

1. Read `.system-basics.json` to get the current version and registered sources.

2. For each registered source, check if newer versions are available:
   ```bash
   git ls-remote --tags <source-url> | tail -5
   ```

3. Show the user what updates are available.

4. If user confirms, fetch and apply updates manually:
   - Clone source to temp directory
   - Compare files with local versions
   - Copy updated files, preserving local adaptations

5. Update `.system-basics.json` with sync timestamp.

6. Suggest reviewing any new or changed skills by reading their SKILL.md files.
