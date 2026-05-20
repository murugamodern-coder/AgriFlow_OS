#!/usr/bin/env bash
# Copy generated Frappe app from bench into monorepo backend/ (Option A).
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BENCH_APP="${BENCH_APP:-$HOME/workspace/frappe-bench/apps/agriflow}"
DEST="$REPO_ROOT/backend/agriflow"
# Maps to frappe-bench/apps/agriflow (app root; Python package is agriflow/)

if [[ ! -d "$BENCH_APP" ]]; then
  echo "Bench app not found: $BENCH_APP" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/backend"
rsync -a --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  "$BENCH_APP/" "$DEST/"

python3 "$REPO_ROOT/scripts/demo_day1_api_extensions.py"
echo "Copied to $DEST"
