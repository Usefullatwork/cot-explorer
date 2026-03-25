#!/usr/bin/env bash
# i18n-sync-check.sh -- Detect hardcoded user-facing strings in component files
#
# Hook type: PostToolUse (matcher: Write|Edit)
# Purpose: Warns when hardcoded strings are found in JSX/TSX component files that
#          should be using i18n translation keys. Prevents untranslatable strings
#          from reaching production.
#
# How it works:
#   - Receives the edited file path as $1 (from $TOOL_INPUT_FILE)
#   - Only checks .tsx and .jsx files (component files)
#   - Scans for common patterns of hardcoded user-facing strings:
#     - String literals in JSX text content (>Some text<)
#     - String props that look like labels (label="Some text")
#     - String props for titles, placeholders, error messages
#   - Ignores:
#     - CSS class names and HTML attributes
#     - Import paths and module names
#     - Boolean and numeric values
#     - Already-translated strings using t() or i18n functions
#   - If suspicious strings found, injects a warning systemMessage
#
# Configuration:
#   I18N_FUNCTION  -- The translation function name (default: "t")
#   MIN_LENGTH     -- Minimum string length to flag (default: 3)
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PostToolUse": [{
#         "matcher": "Write|Edit",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/i18n-sync-check.sh \"$TOOL_INPUT_FILE\"",
#           "timeout": 5000
#         }]
#       }]
#     }
#   }

set -euo pipefail

FILE="${1:-}"

# --- Configuration ---
I18N_FUNCTION="${I18N_FUNCTION:-t}"
MIN_LENGTH=3

# --- Exit silently if no file provided ---
if [ -z "$FILE" ]; then
  exit 0
fi

# --- Only check TSX/JSX component files ---
case "$FILE" in
  *.tsx|*.jsx) ;;
  *) exit 0 ;;
esac

# --- Check if file exists ---
if [ ! -f "$FILE" ]; then
  exit 0
fi

# --- Skip test files ---
case "$FILE" in
  *.test.*|*.spec.*|*__tests__*|*__mocks__*) exit 0 ;;
esac

# --- Search for hardcoded strings in JSX ---
# Pattern 1: Text content between JSX tags: >Some user-facing text<
# This catches: <h1>Dashboard</h1>, <p>Welcome back</p>, <button>Submit</button>
JSX_TEXT_COUNT=$(grep -cE '>[A-Z][a-zA-Z ]{2,}</' "$FILE" 2>/dev/null || true)

# Pattern 2: Common props that should be translated
# This catches: label="Submit", placeholder="Enter email", title="Settings"
PROP_COUNT=$(grep -cE '(label|placeholder|title|alt|aria-label|errorMessage|helperText|description)="[A-Z][^"]{2,}"' "$FILE" 2>/dev/null || true)

# --- Calculate total suspicious strings ---
TOTAL=0
if [ -n "$JSX_TEXT_COUNT" ]; then
  TOTAL=$((TOTAL + JSX_TEXT_COUNT))
fi
if [ -n "$PROP_COUNT" ]; then
  TOTAL=$((TOTAL + PROP_COUNT))
fi

# --- Check if the file already uses i18n ---
USES_I18N=$(grep -c "${I18N_FUNCTION}(" "$FILE" 2>/dev/null || true)

# --- Emit warning if suspicious strings found and i18n is already in use ---
# Only warn if the file already imports/uses i18n (to avoid false positives on
# intentionally non-i18n components)
if [ "$TOTAL" -gt 0 ] && [ -n "$USES_I18N" ] && [ "$USES_I18N" -gt 0 ]; then
  echo "{\"systemMessage\":\"I18N CHECK: Found ~${TOTAL} potentially hardcoded user-facing string(s) in ${FILE}. This file already uses ${I18N_FUNCTION}() for some strings but has others that appear hardcoded. Ensure all user-visible text uses ${I18N_FUNCTION}('key') for translation support.\"}"
elif [ "$TOTAL" -gt 3 ] && [ "$USES_I18N" -eq 0 ]; then
  # Many hardcoded strings and no i18n at all -- might be intentional, gentle nudge
  echo "{\"systemMessage\":\"I18N NOTICE: ${FILE} contains ${TOTAL}+ hardcoded strings and does not use ${I18N_FUNCTION}(). If this component has user-facing text that needs translation, consider adding i18n support.\"}"
fi
