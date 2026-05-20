# Phase 16 — Stabilization, QA & Production Hardening Report

**Site:** `dev.agriflow.local` · **Bench:** `~/workspace/frappe-bench`  
**Mobile:** `agriflow_mobile` v0.16.0+1  
**Date:** 2026-05-20

---

## 1. Hardening report

Phase 16 adds **production hardening** without major feature expansion: JWT auth, request/sync tracing, sync retry/backoff, queue repair, structured diagnostics, permission/inventory audits, prod Docker foundation, and Android release build scripts.

| Area | Deliverable |
|------|-------------|
| Auth | JWT access (15m) + refresh (7d) with rotation; `agriflow_auth_mode=jwt` |
| Tracing | `X-Request-Id`, `X-Sync-Correlation-Id`; envelope `sync_correlation_id` on sync APIs |
| Mobile sync | Retry/backoff, correlation per run, queue repair on boot + after errors |
| Telemetry | `Telemetry` foundation; release blocks `DEV_AUTH_STUB` + empty API URL |
| Ops | `docker-compose.prod.yml`, nginx template, `.env.prod.example` |
| Release | `scripts/build_android_release.sh` |

---

## 2. Pre-implementation audit — production gaps (addressed)

| Gap (Phase 15) | Phase 16 action |
|----------------|-----------------|
| Session-only auth | JWT + Bearer in `permissions.ensure_authenticated` |
| No request correlation | `request_context.bind_request_context` hook |
| No queue repair | `QueueRepair.reconcile()` |
| No retry on transient network | `RetryPolicy` on push/pull/notifications |
| No release guards | `Telemetry.assertReleaseAuthSafe()` |
| No prod compose | `infra/docker/docker-compose.prod.yml` |
| No release APK pipeline | `build_android_release.sh` |

---

## 3. Highest operational risks (ranked)

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Offline queue corruption / stuck `syncing` | Queue repair on app start + Sync Status “Repair queue” |
| 2 | Token theft / refresh reuse | JWT rotation + refresh cache `used` flag |
| 3 | Partial sync failure mid-run | Phase-level try/catch + diagnostics JSON in `sync_runs` |
| 4 | Cross-block data leak | Permission audit + `assert_block_scope` |
| 5 | Negative / over-reserved stock | Inventory reconcile rules |
| 6 | Concurrent sync taps | `SyncSingleFlight` (Phase 14, retained) |
| 7 | No crash reporting in prod | `SENTRY_DSN` dart-define hook point |

---

## 4. Telemetry / logging strategy

| Layer | Approach |
|-------|----------|
| **Mobile** | `Telemetry.log` — no PII; `debug` suppressed in release; errors → `recordError` |
| **API** | Envelope always includes `request_id`; sync adds `sync_correlation_id` |
| **Sync runs** | Drift `sync_runs.raw_response_json` stores structured `SyncDiagnostics` JSON |
| **Server** | Frappe `log_error` on auth failures; production logs via bench/nginx |
| **Future** | Wire `SENTRY_DSN` to Sentry SDK when DSN provided |

---

## 5. Deployment topology

```
[Android/iOS] ──HTTPS──► [nginx :8080]
                              │
                         [Frappe bench :8000]
                         /      |      \
                   MariaDB   Redis   MinIO
```

See [infra/docker/README.md](./infra/docker/README.md).

**Bench config (required for JWT):**

```bash
bench --site dev.agriflow.local set-config agriflow_auth_mode jwt
bench --site dev.agriflow.local set-config agriflow_jwt_secret "$(openssl rand -hex 32)"
```

---

## 6. Queue repair strategy

| Step | Action |
|------|--------|
| 1 | Delete rows with invalid/empty `client_mutation_id` or non-JSON `payload_json` |
| 2 | Reset `status=syncing` → `pending` |
| 3 | Dedupe duplicate `client_mutation_id` (keep first) |
| 4 | Log counts via `Telemetry` |

**When:** App bootstrap + after sync error + manual “Repair queue” on Sync Status.

**Authority:** Server wins — repair never mutates server state.

---

## 7. Files created / updated

### Backend (`scripts/` → bench `agriflow/`)

| File | Target |
|------|--------|
| `phase16_jwt.py` | `api/v1/auth_jwt.py` |
| `phase16_request_context.py` | `api/v1/request_context.py` |
| `phase16_response.py` | `api/v1/response.py` |
| `phase16_permissions.py` | `api/v1/permissions.py` |
| `phase16_auth_api.py` | `api/v1/auth.py` |
| `phase16_sync_api.py` | `api/v1/sync.py` |
| `phase16_permission_audit.py` | `install/phase16_permission_audit.py` |
| `phase16_inventory_reconcile.py` | `install/phase16_inventory_reconcile.py` |
| `phase16_verify_hardening.py` | `install/phase16_verify_hardening.py` |
| `hooks.py` | `before_request = [request_context.bind_request_context]` |

### Mobile

| Path |
|------|
| `lib/core/observability/telemetry.dart` |
| `lib/core/observability/sync_diagnostics.dart` |
| `lib/core/network/tracing_interceptor.dart` |
| `lib/core/sync/retry_policy.dart` |
| `lib/core/sync/queue_repair.dart` |
| `lib/core/sync/sync_correlation.dart` |
| `lib/core/sync/sync_orchestrator.dart` (enhanced) |
| `scripts/build_android_release.sh` |

### Tests

| Test | Proof |
|------|-------|
| `queue_repair_test.dart` | Corruption recovery |
| `retry_policy_test.dart` | Backoff |
| `sync_single_flight_test.dart` | Duplicate taps |
| `queue_persistence_test.dart` | Restart |
| `push_result_applier_test.dart` | Replay |

---

## 8. Failure-recovery proof

| Scenario | Proof |
|----------|-------|
| Transient network | `RetryPolicy` unit test (3 attempts) |
| Mid-sync error | Orchestrator `catch` → `repairQueue()` + `SyncDiagnostics` phase `error` |
| Replay | Bench: `replay_status: skipped` |
| Dropped network | Mobile throws `OFFLINE` before push; pending rows remain |

**Bench verify (`phase16_verify_hardening`):**

```json
{
  "jwt_login_ok": true,
  "jwt_refresh_ok": true,
  "replay_status": "skipped",
  "sync_correlation_in_push": true,
  "permission_audit": { "ok": true }
}
```

---

## 9. Queue-repair proof

| Proof | Evidence |
|-------|----------|
| Unit test | `queue_repair_test.dart` — invalid JSON removed, duplicates deduped |
| Bootstrap | `QueueRepair(db).reconcile()` on every cold start |
| UI | Sync Status → **Repair queue** |

---

## 10. Inventory-integrity proof

| Rule | Check |
|------|-------|
| `on_hand >= 0` | `phase16_inventory_reconcile` |
| `reserved >= 0` | same |
| `available = on_hand - reserved >= 0` | same |

Run:

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase16_inventory_reconcile.execute
```

---

## 11. Security audit summary

| Check | Result |
|-------|--------|
| Guest → API | Blocked (`guest_blocked: true`) |
| JWT login | `jwt_login_ok: true` |
| Bearer auth path | `permissions.ensure_authenticated` resolves JWT |
| Inventory guest write | Denied |
| Release `DEV_AUTH_STUB` | Blocked in `Telemetry.assertReleaseAuthSafe` |
| Refresh reuse | Enforced when Redis cache active; bench execute may warn |

Run:

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase16_permission_audit.execute
```

---

## 12. Deployment notes

1. Copy `infra/docker/.env.prod.example` → `.env.prod`
2. `docker compose -f docker-compose.prod.yml --env-file .env.prod up -d`
3. Point nginx upstream to bench host
4. Set `agriflow_jwt_secret` on site (32+ bytes)
5. TLS termination at nginx or load balancer (not in foundation compose)

---

## 13. Release-build notes

```bash
cd mobile/agriflow_mobile
export API_BASE_URL=https://api.your-domain.example
bash scripts/build_android_release.sh
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

**First time:** `flutter create . --project-name agriflow_mobile` if `android/` missing.

**Defines:** `API_BASE_URL` (required), `DEVICE_ID`, `APP_VERSION`, optional `SENTRY_DSN`.

---

## 14. Validation scenario matrix

| Scenario | Coverage |
|----------|----------|
| Dropped network mid-sync | Offline gate + pending queue preserved |
| Duplicate taps | `SyncSingleFlight` |
| Repeated replay | Server idempotency + applier test |
| Stale `doc_version` | Conflict row + `ConflictSheet` |
| Assignment while offline | Pull refreshes after sync |
| Concurrent officers | Server scope + block permissions |
| Partial inventory | Consume validates qty; reconcile rules |
| Interrupted transfer | Phase 13 savepoint (backend); not re-tested here |
| App restart during sync | Queue persistence test + repair resets `syncing` |

---

## 15. Remaining production risks

| Risk | Notes |
|------|-------|
| Refresh reuse in bench execute | Requires Redis cache in prod; verify on staging |
| Full JWT key rotation / revoke all | Only single refresh family implemented |
| Sentry not wired | Hook only; add SDK when DSN available |
| Frappe not in prod compose | Deploy bench separately (Coolify/k8s) |
| 207 partial batch UI | Per-op breakdown still minimal |
| Inventory offline consume queue | Still online-only (by design) |
| Maps / OCR / push | Out of scope |

---

## 16. Verify commands

```bash
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase16_verify_hardening.execute
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase16_permission_audit.execute
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase16_inventory_reconcile.execute
```

```bash
cd mobile/agriflow_mobile && flutter test
```

---

*Phase 16 — reliability + production hardening (no major feature expansion).*
