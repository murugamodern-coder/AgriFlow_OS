# APK distribution & update workflow (Phase 18)

## Build

```bash
cd mobile/agriflow_mobile
flutter build apk --release \
  --dart-define=API_BASE_URL=https://staging.agriflow.local \
  --dart-define=APP_VERSION=0.18.0 \
  --dart-define=SENTRY_DSN=<dsn> \
  --dart-define=DEVICE_ID=<unique-per-handset>
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

## Host APK

1. Upload to HTTPS path e.g. `https://staging.agriflow.local/files/agriflow-0.18.0.apk`
2. Set site config:
   ```bash
   bench --site staging.agriflow.local set-config agriflow_apk_url "https://..."
   bench --site staging.agriflow.local set-config agriflow_min_app_version "0.18.0"
   ```

## Client check

Mobile calls `readiness.app_release_check` on launch. If `update_required`, show dialog with download link (external browser / intent).

## Upgrade with pending queue

- Drift `sync_queue_entries` and `inventory_queue_entries` persist across upgrades.
- After upgrade: `QueueRepair` on boot → background sync drains queues.
- Officers must open app once on Wi‑Fi after upgrade (background sync is best-effort).

## Rollout waves

| Wave | Max version skew | Action |
|------|------------------|--------|
| Pilot | 2 versions | Block older via `min_app_version` |
| Production | 1 version | Force update before block go-live |
