#!/usr/bin/env bash
# should-dream.sh — Check if 24+ hours since last /dream consolidation
# Hook event: Stop
# If overdue, suggests running /dream as a systemMessage

TIMESTAMP_FILE=".planning/last-dream-timestamp"

# If no timestamp file, this is the first session — suggest first dream
if [ ! -f "$TIMESTAMP_FILE" ]; then
  echo '{"systemMessage": "You have never run /dream. Consider running /dream to consolidate session learnings into durable memory."}'
  exit 0
fi

LAST_DREAM=$(cat "$TIMESTAMP_FILE" 2>/dev/null || echo "0")
NOW=$(date +%s)
DIFF=$((NOW - LAST_DREAM))
HOURS=$((DIFF / 3600))

if [ "$HOURS" -ge 24 ]; then
  echo "{\"systemMessage\": \"It has been ${HOURS} hours since your last /dream. Consider running /dream to consolidate session learnings.\"}"
fi

exit 0
