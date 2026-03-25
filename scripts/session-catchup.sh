#!/usr/bin/env bash
# session-catchup.sh — Quick project health snapshot for session resume
set -euo pipefail

echo "=== COT Explorer Health Check ==="
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'no git')"
echo "Uncommitted: $(git status -s 2>/dev/null | wc -l | tr -d ' ') files"
echo "Last commit: $(git log --oneline -1 2>/dev/null || echo 'none')"
echo ""
echo "--- Data freshness ---"
if [ -f data/macro/latest.json ]; then
  echo "macro/latest.json: $(stat -c '%y' data/macro/latest.json 2>/dev/null || stat -f '%Sm' data/macro/latest.json 2>/dev/null || echo 'unknown')"
else
  echo "macro/latest.json: MISSING"
fi
if [ -f data/combined/latest.json ]; then
  echo "combined/latest.json: $(stat -c '%y' data/combined/latest.json 2>/dev/null || stat -f '%Sm' data/combined/latest.json 2>/dev/null || echo 'unknown')"
else
  echo "combined/latest.json: MISSING"
fi
echo ""
echo "--- Python environment ---"
python3 --version 2>/dev/null || echo "python3: not found"
command -v pytest >/dev/null 2>&1 && echo "pytest: $(pytest --version 2>&1 | head -1)" || echo "pytest: not installed"
command -v ruff >/dev/null 2>&1 && echo "ruff: $(ruff version 2>&1)" || echo "ruff: not installed"
echo ""
echo "--- File counts ---"
echo "Python scripts: $(ls -1 *.py 2>/dev/null | wc -l | tr -d ' ')"
echo "Data directories: $(ls -1d data/*/ 2>/dev/null | wc -l | tr -d ' ')"
