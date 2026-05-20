#!/usr/bin/env bash
# Stop Cloudflare/ngrok demo tunnels.
set -eu

STATE_DIR="${STATE_DIR:-/tmp/agriflow-tunnel}"

for f in cloudflared ngrok; do
  PF="$STATE_DIR/${f}.pid"
  if [ -f "$PF" ]; then
    kill "$(cat "$PF")" 2>/dev/null || true
    rm -f "$PF"
    echo "Stopped $f"
  fi
done

pkill -f "cloudflared tunnel --url" 2>/dev/null || true
pkill -f "ngrok http" 2>/dev/null || true

rm -f "$STATE_DIR/public_url.txt"
echo "Tunnel stopped. Public URL no longer works."
echo "Optional: restore local host_name:"
echo "  bench --site dev.agriflow.local set-config host_name http://127.0.0.1:8000"
