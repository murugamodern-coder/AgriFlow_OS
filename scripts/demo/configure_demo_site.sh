#!/usr/bin/env bash
# Point Frappe site at the tunnel URL (required for login/API from mobile).
set -eu

BENCH="${FRAPPE_BENCH:-$HOME/workspace/frappe-bench}"
SITE="${FRAPPE_SITE:-dev.agriflow.local}"
URL_FILE="${URL_FILE:-/tmp/agriflow-tunnel/public_url.txt}"

if [ ! -f "$URL_FILE" ]; then
  echo "Missing $URL_FILE — start tunnel first."
  exit 1
fi

PUBLIC_URL=$(tr -d '\r\n' < "$URL_FILE")
SITE_CONFIG="$BENCH/sites/$SITE/site_config.json"

python3 - "$SITE_CONFIG" "$PUBLIC_URL" <<'PY'
import json, sys
path, url = sys.argv[1], sys.argv[2]
cfg = json.loads(open(path).read())
cfg["host_name"] = url
cfg["allow_cors"] = "*"
cfg["ignore_csrf"] = 1
open(path, "w").write(json.dumps(cfg, indent=1))
print("Updated", path, "host_name ->", url)
PY

cd "$BENCH"
bench --site "$SITE" clear-cache
echo "Mobile API_BASE_URL=$PUBLIC_URL"
