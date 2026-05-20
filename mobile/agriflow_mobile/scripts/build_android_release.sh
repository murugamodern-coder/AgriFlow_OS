#!/usr/bin/env bash
# Phase 16 — Android release APK/AAB (run from mobile/agriflow_mobile)
set -euo pipefail
cd "$(dirname "$0")/.."

: "${API_BASE_URL:?Set API_BASE_URL e.g. https://api.agriflow.example}"
DEVICE_ID="${DEVICE_ID:-agriflow-prod-android}"
APP_VERSION="${APP_VERSION:-0.16.0}"

flutter pub get
flutter gen-l10n
flutter test

flutter build apk --release \
  --dart-define=API_BASE_URL="${API_BASE_URL}" \
  --dart-define=DEVICE_ID="${DEVICE_ID}" \
  --dart-define=APP_VERSION="${APP_VERSION}"

echo "APK: build/app/outputs/flutter-apk/app-release.apk"
