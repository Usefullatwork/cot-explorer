---
description: Check for updates from System Basics V2 upstream and apply them manually
---

Check for upstream updates from the System Basics V2 repository.

## Steps

1. Check the current installed version:
   ```bash
   cat .system-basics.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))"
   ```

2. Check the latest upstream version:
   ```bash
   git ls-remote --tags https://github.com/Usefullatwork/system-basics-v2 | tail -5
   ```

3. Compare versions. If upstream is newer, show what changed:
   - New agents, skills, or commands added
   - Existing files updated

4. If user wants to update:
   - Clone or pull the upstream repo to a temp location
   - Compare files and show diffs
   - Copy updated files manually, preserving local adaptations
   - Update `.system-basics.json` with new version

5. **Important**: Do NOT overwrite locally adapted files (compliance-scanner, overnight-worker, overnight-sweep, parallel-dispatcher) without confirming with user first.

## Note

SB2 skill management is manual for this project. There is no automated `node scripts/update.js` — use git operations to sync from upstream.
