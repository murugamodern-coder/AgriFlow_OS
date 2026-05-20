# agriflow_mobile

AgriFlow OS Phase 14–15 — offline-first mobile + E2E field validation.

## Prerequisites

- Flutter **3.24.x** (stable)
- Dart **3.5+**

## First-time setup

```bash
cd mobile/agriflow_mobile

# Generate platform folders if missing
flutter create . --project-name agriflow_mobile

flutter pub get
flutter gen-l10n
```

## Run (dev)

**Debug with dev auth stub (no backend):**

```bash
flutter run \
  --dart-define=DEV_AUTH_STUB=true
```

**Against WSL bench** (adjust host for emulator vs device):

```bash
# Seed demo officer (WSL):
# bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase15_seed_demo.execute

flutter run \
  --dart-define=API_BASE_URL=http://10.0.2.2:8000 \
  --dart-define=DEVICE_ID=tablet-dev-001
```

**Demo login:** `field.officer@agriflow.local` / `AgriFlow@2026` (after seed).

| Target | Typical `API_BASE_URL` |
|--------|-------------------------|
| Android emulator | `http://10.0.2.2:8000` |
| Windows desktop / Chrome | `http://127.0.0.1:8000` |
| Physical device | LAN IP of WSL/host |

## Tests

```bash
flutter test
```

Proof tests:

- `test/sync/sync_single_flight_test.dart` — sync lock
- `test/sync/push_result_applier_test.dart` — replay + conflict persistence
- `test/sync/offline_read_test.dart` — offline Drift reads

## Architecture

- **Server** = authoritative truth
- **Drift** = projections + sync queue + diagnostics
- **Hive** = permissions, watermarks, cursors, masters
- **Writes** = `MutationQueue` → `sync.push` only (Phase 14)

See [PHASE14_MOBILE_REPORT.md](../../PHASE14_MOBILE_REPORT.md) and [PHASE15_E2E_VALIDATION_REPORT.md](../../PHASE15_E2E_VALIDATION_REPORT.md) at repo root.
