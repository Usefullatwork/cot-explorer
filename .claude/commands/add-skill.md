---
description: Add a skill from System Basics V2 or a custom GitHub URL
argument-hint: <skill-name or GitHub URL>
---

$ARGUMENTS

Install a skill into the current project from the upstream System Basics V2 repository or a custom GitHub source.

## Steps

1. Parse the argument:
   - If it is a skill name (e.g., `seo-audit`), fetch from `Usefullatwork/system-basics-v2`.
   - If it is a GitHub URL, fetch from that repo.
   - If it is `owner/repo:skill-name`, fetch the specific skill from that repo.

2. If no argument provided, list available skills from the upstream repo:
   ```bash
   git clone --depth 1 https://github.com/Usefullatwork/system-basics-v2 /tmp/sb2-skills
   ls /tmp/sb2-skills/.claude/skills/
   ```

3. Install the skill by copying files:
   ```bash
   cp -r /tmp/sb2-skills/.claude/skills/<skill-name> .claude/skills/
   ```

4. Update `.system-basics.json` to record the newly installed skill.

5. Read the installed skill's SKILL.md:
   ```bash
   cat .claude/skills/<skill-name>/SKILL.md
   ```

6. Report: skill name, files installed, brief description.

## Note

Skills may need adaptation after install if they reference JS/TS tooling that doesn't apply to this Python project. Check for npm, node, package.json references.
