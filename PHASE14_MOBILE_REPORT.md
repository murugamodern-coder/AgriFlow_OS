# Phase 14 — Flutter Mobile Foundation Report

**Package:** `mobile/agriflow_mobile` · **Version:** `0.14.0+1`  
**Status:** Implemented · **Backend:** Unchanged (WSL `~/workspace/frappe-bench`)

---

## 1. Mobile architecture report

| Layer | Responsibility |
|-------|----------------|
| **Presentation** | Screens + Riverpod providers (`features/*/presentation`) |
| **Domain** | Immutable models (`TaskSummary`, `TimelineEvent`, `AuthSession`) |
| **Data** | Repositories, remotes, DTO mapping from projection JSON |
| **Core** | Dio envelope client, Drift store, Hive metadata, sync orchestrator |

**Invariants (Phase 14)**

- Server remains authoritative; Hive/Drift are **derived projections only**.
- All field writes go through **`MutationQueue`** → `sync.push` (no direct mutation APIs from UI).
- `syncNow()` uses **`SyncSingleFlight`** — no concurrent sync runs.
- `kDevAuthStub` only when `kDebugMode` **and** `--dart-define=DEV_AUTH_STUB=true`; never in release.
- API base URL only via `--dart-define=API_BASE_URL` (no hardcoded hosts).

**Stack:** Flutter 3.24 · Riverpod · go_router · Dio · Drift (SQL) · Hive · flutter_secure_storage · connectivity_plus

---

## 2. Folder structure

```
mobile/agriflow_mobile/
├── lib/
│   ├── main.dart
│   ├── l10n/                    # app_en.arb, app_ta.arb (default ta)
│   ├── app/
│   │   ├── bootstrap.dart
│   │   ├── app.dart
│   │   └── router/
│   ├── core/
│   │   ├── config/              # env, api_config
│   │   ├── design_tokens/
│   │   ├── network/             # dio, api_client, envelope
│   │   ├── database/            # AppDatabase (Drift executor + SQL)
│   │   ├── sync/                # orchestrator, queue, single-flight
│   │   ├── storage/             # Hive, secure tokens
│   │   └── providers/
│   ├── features/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── project_lifecycle/   # timeline feed
│   │   ├── tasks/
│   │   ├── notifications/
│   │   └── sync/
│   └── shared/widgets/
├── test/sync/                   # lock, replay, offline proofs
├── assets/design_tokens/
├── pubspec.yaml
└── README.md
```

---

## 3. Offline queue explanation

| Column / concept | Purpose |
|------------------|---------|
| `client_mutation_id` | UUID v4 — replay key (matches Phase 11 server) |
| `entity` / `op_type` | `task`/`timeline` + `complete`/`note`/… |
| `payload_json` | Exact push operation body |
| `status` | `pending` → `syncing` → `synced` / `failed` / `conflict` |
| `server_response_json` | Raw envelope fragment from push |
| `server_request_id` | Frappe `request_id` for diagnostics |
| `idempotency_map` | Local cache of server result per `client_mutation_id` |

**UI path:** Task complete → `MutationQueue.enqueueTaskComplete()` → user syncs → `PushResultApplier` updates row.

---

## 4. Sync orchestration notes

```
syncNow() [single-flight]
  1. connectivity check
  2. sync.push (pending queue batch)
  3. sync.pull (timeline, task, farmer_project + watermarks)
  4. notification.list → Drift cache
  5. sync_runs diagnostics rows
```

- Notifications **not** in `sync.pull` (Phase 12) — dedicated APIs after pull.
- Timeline feed: cross-project via **`sync.pull` entity `timeline`**, filtered by **Hive `permissions.blocks`**.
- Pull watermarks stored in Hive `sync_meta` (`wm:timeline`, `wm:task`, …).
- Cursors in Hive `cursors` (`pull:task`, …).

---

## 5. Hive schema notes

| Box | Keys | Content |
|-----|------|---------|
| `app_prefs` | `locale` | User locale override |
| `permissions` | `manifest` | roles, blocks[], districts[], user display |
| `sync_meta` | `wm:{entity}` | ISO watermarks post-pull |
| `cursors` | `{feed}` | Keyset cursors |
| `masters` | `blocks`, … | Master snapshots (Phase 15+) |

**JWT:** `flutter_secure_storage` only (`agriflow_access_token`, `agriflow_refresh_token`).

---

## 6. Build/run instructions

See [mobile/agriflow_mobile/README.md](./mobile/agriflow_mobile/README.md).

```bash
cd mobile/agriflow_mobile
flutter create . --project-name agriflow_mobile   # first time only
flutter pub get
flutter gen-l10n
flutter test
flutter run --dart-define=DEV_AUTH_STUB=true      # offline UI
```

**WSL API (example):**

```bash
flutter run \
  --dart-define=API_BASE_URL=http://10.0.2.2:8000 \
  --dart-define=DEVICE_ID=phase14-dev-001
```

---

## 7. Future scalability notes

| Area | Phase 15+ direction |
|------|---------------------|
| Drift codegen | Optional `build_runner` + `@DriftDatabase` tables for typed DAOs |
| Background sync | Workmanager / foreground service (explicitly out of Phase 14) |
| Push | FCM + `notification.unread_count` wake |
| Maps / OCR | Separate features per PRD |
| Full Drift entities | Split `projection_cache` into per-entity tables if needed |
| Conflict UI | Wire `ConflictSheet` to real `conflict` rows from queue |
| Auth | Require live `auth.login` on bench; stub remains debug-only |

---

## 8. Sync-lock proof

**Implementation:** `lib/core/sync/sync_single_flight.dart` — concurrent `execute()` callers await the **same** `Future`.

**Test:** `test/sync/sync_single_flight_test.dart`

- Two parallel `execute()` calls → `runs == 1`
- `isRunning == true` during flight

---

## 9. Replay queue proof

**Implementation:** `PushResultApplier` — `success` / `skipped` → `synced` + `idempotency_map`; stores `server_response_json` + `server_request_id`.

**Test:** `test/sync/push_result_applier_test.dart`

- `skipped` replay → queue empty, idempotency row present
- `conflict` → status `conflict`, raw JSON + `request_id` persisted

---

## 10. Offline-read proof

**Test:** `test/sync/offline_read_test.dart`

- Seed `projection_cache` rows (task + timeline)
- `TaskRepository.readCachedInbox()` / `TimelineRepository.readCachedFeed()` return data **without** network

---

## Screens delivered

| Screen | Route |
|--------|-------|
| Login | `/login` |
| Dashboard shell | bottom nav |
| Timeline feed | `/timeline` |
| My Tasks | `/tasks` |
| Notifications | `/notifications` |
| Sync Status | `/sync` |

---

## Out of scope (confirmed not implemented)

Maps/GPS · Camera/OCR · FCM push · Background sync daemon · Inventory/MIMIS UI · `project.transition` UI

---

## Verification checklist (local)

| Step | Command |
|------|---------|
| Unit tests | `cd mobile/agriflow_mobile && flutter test` |
| Dev UI | `flutter run --dart-define=DEV_AUTH_STUB=true` |
| API smoke | Login + sync against `dev.agriflow.local` when `auth.*` live on bench |

---

*Generated: Phase 14 implementation — AgriFlow OS.*
