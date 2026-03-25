#!/usr/bin/env bash
# branch-guard.sh -- Prevent file edits on protected branches
#
# Hook type: PreToolUse (matcher: Edit|Write)
# Purpose: Blocks file modifications when the current git branch is a protected
#          branch (main, master, production, staging). Forces Claude to create
#          a feature branch first.
#
# How it works:
#   - Checks the current git branch name
#   - If it matches a protected branch, outputs a systemMessage warning
#   - Does NOT block the edit (Claude Code handles that) -- just warns loudly
#   - If not in a git repo, exits silently
#
# Protected branches (customize below):
#   main, master, production, staging, release
#
# Usage in settings.json:
#   {
#     "hooks": {
#       "PreToolUse": [{
#         "matcher": "Edit|Write",
#         "hooks": [{
#           "type": "command",
#           "command": "bash hooks/scripts/branch-guard.sh",
#           "timeout": 2000
#         }]
#       }]
#     }
#   }

set -euo pipefail

# --- Configuration ---
PROTECTED_BRANCHES=("main" "master" "production" "staging" "release")

# --- Check if we are in a git repo ---
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || true)

if [ -z "$CURRENT_BRANCH" ]; then
  # Not in a git repo or detached HEAD -- exit silently
  exit 0
fi

# --- Check if current branch is protected ---
for BRANCH in "${PROTECTED_BRANCHES[@]}"; do
  if [ "$CURRENT_BRANCH" = "$BRANCH" ]; then
    echo "{\"systemMessage\":\"BRANCH GUARD: You are on the protected branch '${CURRENT_BRANCH}'. Do NOT edit files directly on this branch. Create a feature branch first: git checkout -b feature/your-feature-name\"}"
    exit 0
  fi
done

# --- Not a protected branch -- exit silently ---
