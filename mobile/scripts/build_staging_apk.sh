#!/usr/bin/env bash
set -eu

API_URL="${API_BASE_URL:?Set API_BASE_URL e.g. https://staging.example.com}"
VERSION="${APP_VERSION:-0.24.0}"
OUT_DIR="${OUT_DIR:-build/app/outputs/flutter-apk}"

cd "$(dirname "$0")/.."
flutter pub get
flutter gen-l10n 2>/dev/null || true

flutter build apk --release \
  --dart-define=API_BASE_URL="$API_URL" \
  --dart-define=APP_VERSION="$VERSION" \
  --dart-define=MIN_APP_VERSION="$VERSION" \
  --dart-define=PUSH_DEBUG_STUB=false

echo "APK: $OUT_DIR/app-release.apk"
echo "Install on pilot devices and verify sync against $API_URL"
