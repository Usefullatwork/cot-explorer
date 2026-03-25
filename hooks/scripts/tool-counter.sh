#!/usr/bin/env bash
# tool-counter.sh -- Track cumulative tool calls and warn about context degradation
#
# Hook type: PostToolUse (matcher: .*)
# Purpose: Counts every tool call in the session. Warns at configurable thresholds
#          to prompt context management (compact, save state, fresh session).
#
# How it works:
#   - Maintains a counter in /tmp/claude_tool_count_<pid-hash>
#   - Increments on every tool call
#   - At YELLOW_THRESHOLD (40): suggests compacting
#   - At RED_THRESHOLD (60): warns about context degradation
#   - At CRITICAL_THRESHOLD (80): strongly recommends a fresh session
#
# Reset:
#   - Delete the counter file to reset: rm /tmp/claude_tool_count_*
#   - Counter auto-resets when a new session starts (different PID)
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PostToolUse": [{
#         "matcher": ".*",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/tool-counter.sh",
#           "timeout": 2000
#         }]
#       }]
#     }
#   }

set -euo pipefail

# --- Configuration ---
YELLOW_THRESHOLD=40
RED_THRESHOLD=60
CRITICAL_THRESHOLD=80

# --- Counter file (unique per terminal session via PPID) ---
COUNTER_FILE="/tmp/claude_tool_count_${PPID:-default}"

# --- Read current count ---
COUNT=0
if [ -f "$COUNTER_FILE" ]; then
  COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
fi

# --- Increment ---
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# --- Emit warnings at thresholds ---
if [ "$COUNT" -eq "$CRITICAL_THRESHOLD" ]; then
  echo "{\"systemMessage\":\"CRITICAL: ${CRITICAL_THRESHOLD} tool calls reached. Context degradation is very likely. Strongly recommend saving state and starting a fresh session.\"}"
elif [ "$COUNT" -eq "$RED_THRESHOLD" ]; then
  echo "{\"systemMessage\":\"WARNING: ${RED_THRESHOLD} tool calls reached. Context degradation is likely. Consider running /compact or saving state and starting fresh.\"}"
elif [ "$COUNT" -eq "$YELLOW_THRESHOLD" ]; then
  echo "{\"systemMessage\":\"NOTE: ${YELLOW_THRESHOLD} tool calls reached. Consider running /compact to free up context space.\"}"
fi

# --- No output for non-threshold counts (silent operation) ---
