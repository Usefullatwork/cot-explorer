#!/usr/bin/env bash
# print-debug-check.sh -- Detect debug print() statements in Python source files
#
# Hook type: PostToolUse (matcher: Write|Edit)
# Purpose: Warns when print() is found in source files. Production code should
#          use the logging module, not print(). Allows logging.* calls.
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PostToolUse": [{
#         "matcher": "Write|Edit",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/print-debug-check.sh \"$TOOL_INPUT_FILE\"",
#           "timeout": 3000
#         }]
#       }]
#     }
#   }

set -euo pipefail

FILE="${1:-}"

# --- Exit silently if no file provided ---
if [ -z "$FILE" ]; then
  exit 0
fi

# --- Only check Python source files ---
case "$FILE" in
  *.py) ;;
  *) exit 0 ;;
esac

# --- Skip test files and config ---
case "$FILE" in
  */tests/*|*/test_*|*conftest*|*setup.py|*__init__*) exit 0 ;;
esac

# --- Check if file exists ---
if [ ! -f "$FILE" ]; then
  exit 0
fi

# --- Search for print() calls ---
# Match print( but not in comments
PRINT_COUNT=$(grep -c 'print(' "$FILE" 2>/dev/null || true)

if [ -n "$PRINT_COUNT" ] && [ "$PRINT_COUNT" -gt 0 ]; then
  # Check if any are NOT in comments
  REAL_PRINTS=$(grep -n 'print(' "$FILE" 2>/dev/null | grep -v '^\s*#' | wc -l | tr -d ' ')

  if [ "$REAL_PRINTS" -gt 0 ]; then
    echo "{\"systemMessage\":\"PRINT() DETECTED: Found ${REAL_PRINTS} print() statement(s) in ${FILE}. Production source files should use the logging module instead of print(). Please replace with logging.debug(), logging.info(), or remove if it was for debugging.\"}"
  fi
fi
