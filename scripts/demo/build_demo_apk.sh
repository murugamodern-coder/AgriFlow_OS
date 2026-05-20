#!/usr/bin/env bash
set -eu

URL_FILE="${URL_FILE:-/tmp/agriflow-tunnel/public_url.txt}"
if [ ! -f "$URL_FILE" ]; then
  echo "Start tunnel first."
  exit 1
fi

API_BASE_URL=$(cat "$URL_FILE" | tr -d '\r\n')
cd "$(dirname "$0")/../../mobile/agriflow_mobile"

flutter pub get
flutter build apk --debug \
  --dart-define=API_BASE_URL="$API_BASE_URL" \
  --dart-define=APP_VERSION=0.24.0 \
  --dart-define=PUSH_DEBUG_STUB=true

echo "Install: build/app/outputs/flutter-apk/app-debug.apk"
echo "API: $API_BASE_URL"
