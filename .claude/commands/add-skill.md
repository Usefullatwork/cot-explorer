---
description: Add a skill from the System Basics V2 repository or a custom GitHub URL
argument-hint: <skill-name or GitHub URL>
---

$ARGUMENTS

Install a skill into the current project from the upstream System Basics V2 repository or a custom GitHub source.

## Steps

1. Parse the argument:
   - If it is a skill name (e.g., `seo-audit`), fetch from the configured upstream repo (default: `Usefullatwork/system-basics-v2`).
   - If it is a GitHub URL (e.g., `https://github.com/someone/custom-skill`), fetch from that repo.
   - If it is a `owner/repo:skill-name` format, fetch the specific skill from that repo.

2. If no argument is provided, list available skills:
   ```bash
   node scripts/add-skill.js --list
   ```

3. Install the skill:
   ```bash
   node scripts/add-skill.js <argument>
   ```

4. The skill files will be copied to `.claude/skills/<skill-name>/`.

5. Update `.system-basics.json` to record the newly installed skill.

6. After installation, read the skill's SKILL.md to understand what it does:
   ```bash
   cat .claude/skills/<skill-name>/SKILL.md
   ```

7. Report success: skill name, number of files installed, and a brief description of the skill's purpose.
