#!/usr/bin/env bash
# Install committed backend/agriflow onto local frappe-bench.
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/backend/agriflow"
BENCH_APP="${BENCH_APP:-$HOME/workspace/frappe-bench/apps/agriflow}"

if [[ ! -d "$SRC/agriflow" ]]; then
  echo "Committed app missing: $SRC" >&2
  exit 1
fi

rsync -a --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  "$SRC/" "$BENCH_APP/"

echo "Installed to $BENCH_APP"
echo "Next: cd ~/workspace/frappe-bench && bench --site dev.agriflow.local migrate && bench clear-cache"
