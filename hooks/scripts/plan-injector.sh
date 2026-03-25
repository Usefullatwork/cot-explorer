#!/usr/bin/env bash
# plan-injector.sh -- Inject the active plan into Claude's context before file edits
#
# Hook type: PreToolUse (matcher: Edit|Write)
# Purpose: Reminds Claude of the current task plan before every file modification,
#          reducing drift and keeping edits aligned with the original goal.
#
# How it works:
#   - Checks for a plan file at .planning/task_plan.md
#   - If found, reads the first 30 lines and injects them as a systemMessage
#   - If no plan file exists, does nothing (silent no-op)
#
# Plan file location:
#   .planning/task_plan.md (create this before starting a complex task)
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PreToolUse": [{
#         "matcher": "Edit|Write",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/plan-injector.sh",
#           "timeout": 3000
#         }]
#       }]
#     }
#   }

set -euo pipefail

PLAN_FILE=".planning/task_plan.md"

# Exit silently if no plan file exists
if [ ! -f "$PLAN_FILE" ]; then
  exit 0
fi

# Read the first 30 lines of the plan
CONTENT=$(head -30 "$PLAN_FILE" 2>/dev/null || true)

# Exit silently if plan is empty
if [ -z "$CONTENT" ]; then
  exit 0
fi

# Escape for JSON: replace backslashes, double quotes, newlines, tabs
ESCAPED=$(echo "$CONTENT" | \
  sed 's/\\/\\\\/g' | \
  sed 's/"/\\"/g' | \
  sed ':a;N;$!ba;s/\n/\\n/g' | \
  sed 's/\t/\\t/g')

# Output as JSON systemMessage
echo "{\"systemMessage\":\"ACTIVE PLAN (stay on track):\\n${ESCAPED}\"}"
