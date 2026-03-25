#!/usr/bin/env bash
# System Basics V2 — Auto-sync check on session start
#
# This hook runs at SessionStart and checks if skill updates are available.
# Only runs if .system-basics.json exists and autoSync is enabled.
#
# Hook output format: JSON with systemMessage field for Claude Code to display.

CONFIG=".system-basics.json"

# Exit silently if no config file
if [ ! -f "$CONFIG" ]; then
  exit 0
fi

# Check if autoSync is enabled
AUTO=$(node -p "try{JSON.parse(require('fs').readFileSync('$CONFIG','utf8')).autoSync}catch(e){'false'}" 2>/dev/null)
if [ "$AUTO" != "true" ]; then
  exit 0
fi

# Check if enough time has passed since last sync (based on syncInterval)
LAST_SYNC=$(node -p "try{JSON.parse(require('fs').readFileSync('$CONFIG','utf8')).lastSync||''}catch(e){''}" 2>/dev/null)
INTERVAL=$(node -p "try{JSON.parse(require('fs').readFileSync('$CONFIG','utf8')).syncInterval||'weekly'}catch(e){'weekly'}" 2>/dev/null)

if [ -n "$LAST_SYNC" ]; then
  # Calculate time since last sync in seconds
  LAST_EPOCH=$(node -p "Math.floor(new Date('$LAST_SYNC').getTime()/1000)" 2>/dev/null)
  NOW_EPOCH=$(node -p "Math.floor(Date.now()/1000)" 2>/dev/null)

  if [ -n "$LAST_EPOCH" ] && [ -n "$NOW_EPOCH" ]; then
    DIFF=$((NOW_EPOCH - LAST_EPOCH))

    case "$INTERVAL" in
      daily)   THRESHOLD=86400 ;;      # 24 hours
      weekly)  THRESHOLD=604800 ;;     # 7 days
      monthly) THRESHOLD=2592000 ;;    # 30 days
      *)       THRESHOLD=604800 ;;     # default: weekly
    esac

    if [ "$DIFF" -lt "$THRESHOLD" ]; then
      # Not enough time has passed — skip check
      exit 0
    fi
  fi
fi

# Run the check (lightweight — no downloads)
# check-updates.js exits 0 if up to date, 1 if updates available, 2 on error
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)/scripts"
if [ ! -f "$SCRIPT_DIR/check-updates.js" ]; then
  # Try relative to project root
  SCRIPT_DIR="scripts"
fi

if [ ! -f "$SCRIPT_DIR/check-updates.js" ]; then
  # Script not found — this project may not have the sync scripts installed
  exit 0
fi

RESULT=$(node "$SCRIPT_DIR/check-updates.js" --json 2>/dev/null)
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 1 ]; then
  # Updates available — extract count
  COUNT=$(echo "$RESULT" | node -p "try{JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).updatesAvailable}catch(e){0}" 2>/dev/null)
  if [ -z "$COUNT" ] || [ "$COUNT" = "0" ]; then
    COUNT="some"
  fi
  echo "{\"systemMessage\":\"System Basics: ${COUNT} skill update(s) available from upstream. Run /sync-skills to review and apply.\"}"
fi

# Exit 0 regardless — hook should not block session start
exit 0
