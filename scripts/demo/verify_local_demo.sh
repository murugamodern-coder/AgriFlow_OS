#!/usr/bin/env bash
set -eu

URL_FILE="${URL_FILE:-/tmp/agriflow-tunnel/public_url.txt}"
BENCH_PORT="${BENCH_PORT:-8000}"
FAIL=0

check() { if "$@"; then echo "OK  $*"; else echo "FAIL $*"; FAIL=1; fi }

echo "=== Local bench ==="
check curl -fsS -o /dev/null "http://127.0.0.1:${BENCH_PORT}"
check pgrep -f "frappe serve" >/dev/null
check pgrep -f "frappe schedule" >/dev/null || pgrep -f "bench schedule" >/dev/null

if [ -f "$URL_FILE" ]; then
  BASE=$(cat "$URL_FILE")
  echo "=== Public tunnel: $BASE ==="
  check curl -fsSk -o /dev/null "$BASE"
  check curl -fsSk -o /dev/null "$BASE/observability_console"
  check curl -fsSk -o /dev/null "$BASE/pilot_ops_dashboard"
else
  echo "SKIP public checks (no tunnel URL file)"
fi

[ "$FAIL" -eq 0 ] && echo "=== PASSED ===" || { echo "=== FAILED ==="; exit 1; }
