# Android battery optimization (field devices)

Officers should disable aggressive battery restriction for AgriFlow so background sync and push can run.

## Recommended settings (Tamil Nadu field handsets)

1. **Settings → Apps → AgriFlow → Battery → Unrestricted** (or "Don't optimize")
2. Allow **background data** on mobile data and Wi‑Fi
3. Disable manufacturer "auto-clean" (MIUI, ColorOS, etc.) for AgriFlow

## Expected behavior

- **Headless sync** runs every ~30 minutes when Workmanager is enabled (see `HEADLESS_SYNC_ANDROID_SETUP.md`)
- **Foreground sync** still runs on app open and connectivity restore
- If push delayed, open app once daily on Wi‑Fi

## Support script

"If notifications stop, check battery unrestricted and run Sync from the app."
