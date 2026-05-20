# Phase 18 — Production Readiness & Reliability Completion

**Site:** `dev.agriflow.local` (staging-shaped) · **Mobile:** `agriflow_mobile` v0.18.0+1  
**Date:** 2026-05-20

---

## 1. Pre-implementation — production gap audit

| Gap (post Phase 17) | Phase 18 |
|---------------------|----------|
| No real staging stack | `docker-compose.staging.yml` + HTTPS nginx template |
| Sentry hook only | `sentry_flutter` + `SentryBootstrap.init` |
| No push foundation | `Device Push Token`, `Push Delivery Log`, `push.register_token` |
| No background sync | `BackgroundSyncCoordinator` (resume / connectivity / 15m) |
| Inventory direct API only | `inventory_queue_entries` + replay after `sync.push` |
| Long offline watermark drift | Full pull when `last_success_at` &gt; 72h |
| No APK update path | `readiness.app_release_check` + rollout doc |
| Permission audit not pilot-focused | `phase18_permission_audit` |
| No queue alerts | `readiness.queue_alerts` |

**Still out of scope:** FCM HTTP send (requires `agriflow_fcm_server_key`), Workmanager isolate (needs `flutter create` android/), Coolify automation, maps/OCR/AI.

---

## 2. Push architecture

```
[Notification fanout server] ──► fanout_push_stub()
                                      │
                                      ▼
                            Push Delivery Log (metrics)
                                      │
                    (future) FCM HTTP ◄── Device Push Token
                                      │
                                      ▼
                            [Android] flutter_local_notifications
                            deep_link → go_router (tasks/timeline)
```

- **Register:** `push.register_token` on app launch (debug token when `PUSH_DEBUG_STUB`).
- **Delivery:** Stub logs `queued` or `skipped_offline` until FCM key configured.
- **Offline:** Push stored server-side; inbox pull on next sync (existing Phase 12 path).

---

## 3. Background sync strategy

| Trigger | Action |
|---------|--------|
| App resume | `syncNow()` |
| Connectivity restored | `syncNow()` |
| Every 15 minutes (app process alive) | `syncNow()` |
| JWT expiry mid-sync | Dio refresh interceptor → retry |

Not a true OS background worker until `workmanager` is wired post-`flutter create`. Field practice: officers open app daily on Wi‑Fi; coordinator covers intermittent connectivity.

---

## 4. Offline inventory replay flow

1. Officer taps consume while offline → `InventoryQueue.enqueueConsume()` → Drift `inventory_queue_entries`.
2. On next successful connectivity sync: `sync.push` → `pull` → `InventoryQueue.replayPending()` via `inventory.allocation_consume`.
3. Conflicts → row `status=conflict`, officer refreshes task allocations.

---

## 5. APK distribution / update plan

See [docs/APK_ROLLOUT_WORKFLOW.md](./docs/APK_ROLLOUT_WORKFLOW.md).

- Build with `APP_VERSION` + `SENTRY_DSN`.
- Host APK on HTTPS; set `agriflow_apk_url` + `agriflow_min_app_version` on site.
- Mobile `readiness.app_release_check` on dashboard load.

---

## 6. Long-offline recovery model

| Duration | Behavior |
|----------|----------|
| &lt; 72h | Incremental pull via Hive watermarks |
| ≥ 72h | Empty `modified_since` → full entity catch-up pull |
| Any | Queue + inventory queue persist in SQLite across reboot/upgrade |
| Return | JWT login → replay `sync.push` (skipped idempotency) → inventory replay |

Validated: `phase18_offline_survivability.execute`.

---

## 7. Task list delivered

### Infra
- [x] Staging compose + HTTPS nginx template
- [x] Secrets doc + backup script
- [x] `phase18_deploy_staging.sh`

### Backend
- [x] `api/v1/push.py`, `api/v1/readiness.py`
- [x] DocTypes: Device Push Token, Push Delivery Log
- [x] `phase18_verify_production`, permission audit, offline survivability

### Mobile
- [x] Sentry bootstrap
- [x] Background sync coordinator
- [x] Inventory queue + replay
- [x] Push service + deep links
- [x] Release check dialog
- [x] Sync failure categories → diagnostics JSON

---

## 8. Validation results (bench)

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase18_verify_production.execute
```

Expected: `ok: true` — push register, fanout log, release check, queue alerts, permission audit, offline survivability, production dashboard.

---

## 9. Production readiness report

| Area | Status |
|------|--------|
| Staging topology | Documented + compose ready |
| HTTPS | Template requires real certs in `infra/docker/nginx/certs/` |
| JWT + Redis | Phase 16 — enable Redis on staging |
| Pilot ops dashboard | Phase 17 — retained |
| Production dashboard | `readiness.production_dashboard` |
| Mobile offline | Queue + inventory queue + 72h full pull |
| Crash telemetry | Sentry when DSN set; else diagnostic upload |

---

## 10. Push delivery report

| Metric | Source |
|--------|--------|
| `active_tokens` | `push.delivery_metrics` |
| `by_status` | Push Delivery Log |
| FCM | `fcm_configured: false` until site key set |

Stub fanout creates log rows per device token for pilot metrics.

---

## 11. Background sync report

- Coordinator started in `bootstrap()`.
- Errors → `SentryBootstrap.capture` + `Telemetry`.
- **Limitation:** No headless Android sync without native project + Workmanager.

---

## 12. Offline survivability proof

- **Server:** `phase18_offline_survivability` — JWT login after “offline”, replay skipped, full pull ok.
- **Mobile:** `inventory_queue_test`, queue persistence tests (Phase 14/16), schema v2 `inventory_queue_entries`.
- **72h rule:** `_resolvePullWatermarks()` in `SyncOrchestrator`.

---

## 13. APK rollout workflow

Documented in [docs/APK_ROLLOUT_WORKFLOW.md](./docs/APK_ROLLOUT_WORKFLOW.md). Site `agriflow_min_app_version=0.18.0` set on dev bench.

---

## 14. Security audit summary

| Check | Result |
|-------|--------|
| Guest auth blocked | Phase 16 audit (base) |
| Officer push register | Phase 18 audit |
| Field Staff role | Warn if missing |
| Block scope | Demo officer check |
| Inventory guest denied | Phase 16 |
| Secrets in git | `.env.*.example` only |

---

## 15. Remaining production risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | No FCM HTTP yet | Configure `agriflow_fcm_server_key`; worker job |
| 2 | Background sync needs app foreground | Daily sync SOP; future Workmanager |
| 3 | Self-signed TLS on staging | Use Let’s Encrypt before pilot |
| 4 | Flutter android/ not generated | Run `flutter create .` before release APK |
| 5 | Demo sync failure rate high on bench | Pilot on clean block data |
| 6 | Field Staff role missing on some sites | Fixture before Pilot B |

---

## 16. Recommended production rollout strategy

1. **Week 1** — Bring up staging compose + TLS + `phase18_verify_production`.
2. **Week 2** — 5-device pilot with Sentry DSN + APK 0.18.0; daily `production_dashboard`.
3. **Week 3** — Enable FCM; validate push deep links on assignment notifications.
4. **Week 4** — Block go-live: `agriflow_min_app_version` enforce, Redis required, backup drill.
5. **Scale** — Pilot B (30 officers) → production hostname per IMPLEMENTATION_PLAN.

---

## 17. Mobile local validation

```bash
cd mobile/agriflow_mobile
flutter pub get
flutter gen-l10n
flutter test
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 \
  --dart-define=APP_VERSION=0.18.0 \
  --dart-define=DEV_AUTH_STUB=true
```

Optional: `--dart-define=SENTRY_DSN=<dsn>` for crash telemetry.

---

## 18. Deploy commands

```bash
# WSL
bash scripts/phase18_deploy_staging.sh
# or manual cp + bench execute (see script)

# Staging stack (optional)
cd infra/docker
cp .env.staging.example .env.staging
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d
```
