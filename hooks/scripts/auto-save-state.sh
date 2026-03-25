#!/usr/bin/env bash
# auto-save-state.sh — Save session state before /compact
# Called by PreCompact hook in settings-templates/full.json

PLANNING_DIR="${PROJECT_DIR:-.}/.planning"
SNAPSHOT_DIR="$PLANNING_DIR/snapshots"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$SNAPSHOT_DIR"

{
  echo "# Pre-Compact Snapshot — $TIMESTAMP"
  echo ""
  echo "## Branch"
  git branch --show-current 2>/dev/null || echo "(not a git repo)"
  echo ""
  echo "## Uncommitted Changes"
  git status -s 2>/dev/null || echo "(no git)"
  echo ""
  echo "## Recent Commits"
  git log --oneline -5 2>/dev/null || echo "(no git)"
  echo ""
  echo "## Active Plan"
  if [ -f "$PLANNING_DIR/task_plan.md" ]; then
    head -30 "$PLANNING_DIR/task_plan.md"
  else
    echo "(no active plan)"
  fi
} > "$SNAPSHOT_DIR/snapshot-$TIMESTAMP.md"

echo "Snapshot saved to $SNAPSHOT_DIR/snapshot-$TIMESTAMP.md"
