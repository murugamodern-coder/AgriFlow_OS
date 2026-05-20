#!/usr/bin/env bash
# Fallback: ngrok HTTP tunnel to local bench.
set -eu

BENCH_PORT="${BENCH_PORT:-8000}"
STATE_DIR="${STATE_DIR:-/tmp/agriflow-tunnel}"
PID_FILE="$STATE_DIR/ngrok.pid"
URL_FILE="$STATE_DIR/public_url.txt"

if ! command -v ngrok >/dev/null 2>&1; then
  echo "Install ngrok: https://ngrok.com/download then: ngrok config add-authtoken <token>"
  exit 1
fi

if ! curl -fsS -o /dev/null "http://127.0.0.1:${BENCH_PORT}"; then
  echo "ERROR: bench not running on port $BENCH_PORT"
  exit 1
fi

mkdir -p "$STATE_DIR"
nohup ngrok http "$BENCH_PORT" --log=stdout >"$STATE_DIR/ngrok.log" 2>&1 &
echo $! >"$PID_FILE"

sleep 3
PUBLIC_URL=$(curl -fsS http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
for t in d.get('tunnels',[]):
  if t.get('proto')=='https':
    print(t['public_url']); break
" 2>/dev/null || true)

if [ -z "$PUBLIC_URL" ]; then
  echo "Could not read ngrok URL. Open http://127.0.0.1:4040"
  exit 1
fi

echo "$PUBLIC_URL" >"$URL_FILE"
echo "PUBLIC DEMO URL: $PUBLIC_URL"
echo "Configure: bash scripts/demo/configure_demo_site.sh"
