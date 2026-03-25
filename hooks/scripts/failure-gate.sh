#!/usr/bin/env bash
# failure-gate.sh -- Track consecutive Bash failures and warn after 3 strikes
#
# Hook type: PostToolUse (matcher: .*)
# Purpose: Detects when Claude is stuck in a failure loop (3+ consecutive Bash
#          errors). Injects a warning to stop, re-plan, and try a different approach.
#
# How it works:
#   - Reads the exit code of the last tool call from $TOOL_EXIT_CODE
#   - If the last tool was Bash and it failed, increments the failure counter
#   - If any tool succeeds, resets the counter to 0
#   - At 3 consecutive failures, injects a systemMessage to re-plan
#   - At 5 consecutive failures, injects a stronger warning
#
# Environment variables used:
#   TOOL_EXIT_CODE  -- Exit code of the last tool call (set by Claude Code)
#   TOOL_NAME       -- Name of the last tool (set by Claude Code)
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PostToolUse": [{
#         "matcher": ".*",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/failure-gate.sh",
#           "timeout": 2000
#         }]
#       }]
#     }
#   }

set -euo pipefail

# --- Counter file ---
FAILURE_FILE="/tmp/claude_failure_count_${PPID:-default}"

# --- Read current failure count ---
FAILURES=0
if [ -f "$FAILURE_FILE" ]; then
  FAILURES=$(cat "$FAILURE_FILE" 2>/dev/null || echo 0)
fi

# --- Check last tool result ---
EXIT_CODE="${TOOL_EXIT_CODE:-0}"
TOOL="${TOOL_NAME:-unknown}"

if [ "$EXIT_CODE" != "0" ] && [ "$TOOL" = "Bash" ]; then
  # Bash command failed -- increment counter
  FAILURES=$((FAILURES + 1))
  echo "$FAILURES" > "$FAILURE_FILE"

  if [ "$FAILURES" -ge 5 ]; then
    echo "{\"systemMessage\":\"FAILURE GATE: 5 consecutive Bash failures. STOP. You are stuck in a loop. Switch to plan mode, explain what you are trying to do, and ask the user for guidance. Do NOT try another command.\"}"
  elif [ "$FAILURES" -ge 3 ]; then
    echo "{\"systemMessage\":\"FAILURE GATE: 3 consecutive Bash failures detected. Stop and re-plan. The current approach is not working. Consider: (1) re-reading the error messages carefully, (2) trying a completely different approach, (3) asking the user for help.\"}"
  fi
else
  # Success or non-Bash tool -- reset counter
  if [ "$FAILURES" -gt 0 ]; then
    echo "0" > "$FAILURE_FILE"
  fi
fi
