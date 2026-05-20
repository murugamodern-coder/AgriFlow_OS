#!/usr/bin/env bash
# Start Cloudflare quick tunnel to local bench (WSL). LF endings.
set -eu

BENCH_PORT="${BENCH_PORT:-8000}"
TARGET="http://127.0.0.1:${BENCH_PORT}"
STATE_DIR="${STATE_DIR:-/tmp/agriflow-tunnel}"
PID_FILE="$STATE_DIR/cloudflared.pid"
URL_FILE="$STATE_DIR/public_url.txt"
LOG_FILE="$STATE_DIR/cloudflared.log"
CLOUDFLARED="${CLOUDFLARED:-$HOME/bin/cloudflared}"

mkdir -p "$STATE_DIR"

if [ ! -x "$CLOUDFLARED" ]; then
  mkdir -p "$HOME/bin"
  curl -fsSL -o "$CLOUDFLARED" \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod +x "$CLOUDFLARED"
fi

# Health check
if ! curl -fsS -o /dev/null "$TARGET"; then
  echo "ERROR: $TARGET not reachable. Run: cd ~/workspace/frappe-bench && bench start"
  exit 1
fi

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Tunnel already running (pid $(cat "$PID_FILE"))"
  cat "$URL_FILE" 2>/dev/null || true
  exit 0
fi

echo "Starting Cloudflare quick tunnel -> $TARGET"
nohup "$CLOUDFLARED" tunnel --url "$TARGET" >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

echo "Waiting for public URL..."
for _ in $(seq 1 30); do
  if grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG_FILE" | head -1 >"$URL_FILE"; then
    break
  fi
  sleep 1
done

if [ ! -s "$URL_FILE" ]; then
  echo "Failed to obtain URL. See $LOG_FILE"
  exit 1
fi

PUBLIC_URL=$(cat "$URL_FILE")
echo ""
echo "============================================"
echo "  PUBLIC DEMO URL: $PUBLIC_URL"
echo "============================================"
echo ""
echo "Configure bench: bash scripts/demo/configure_demo_site.sh"
echo "Stop tunnel:     bash scripts/demo/stop_demo_tunnel.sh"
