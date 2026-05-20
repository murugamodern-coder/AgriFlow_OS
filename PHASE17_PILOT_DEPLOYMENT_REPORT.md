# Phase 17 — Pilot Deployment & Operational Feedback Loop

**Site:** `dev.agriflow.local` · **Mobile:** `agriflow_mobile` v0.17.0+1  
**Date:** 2026-05-20

---

## 1. Pre-implementation — deployment readiness audit

| Area | Status (pre-17) | Phase 17 action |
|------|-----------------|-----------------|
| JWT + tracing | Phase 16 | Retained; pilot APIs use same envelope |
| Prod compose / release script | Phase 16 | Staging workflow doc + checklist |
| Crash reporting SDK | Hook only | Diagnostic upload to `Pilot Device Telemetry` |
| Field feedback channel | None | `Pilot Operational Feedback` + mobile form |
| Admin ops visibility | Logs only | `pilot_ops.dashboard` + `/pilot_dashboard` |
| Version drift tracking | `APP_VERSION` define | Heartbeat + `app_versions` matrix |
| Officer onboarding | Ad hoc | Server checklist + first-run screen |

**Remaining gaps (not in scope):** Sentry SDK wiring, dedicated staging hostname, Field Staff role fixtures on all pilot sites, automated Coolify pipeline.

---

## 2. Pilot success metrics

| Metric | Target (pilot week) |
|--------|---------------------|
| Sync failure rate (server mutations) | &lt; 5% of mutations in 7d window |
| Devices with queue_pending &gt; 10 for 24h | 0 |
| Inventory reconcile mismatches | 0 |
| Critical feedback items unresolved 48h | 0 |
| Officers completing onboarding | 100% of pilot cohort |
| App version skew | ≤ 2 active versions |

---

## 3. Telemetry aggregation strategy

| Source | Storage | Aggregation |
|--------|---------|-------------|
| Mobile heartbeat | `Pilot Device Telemetry` | Latest row per `device_id` (24h window in dashboard) |
| Sync sessions | `Sync Session` | Count open/complete, per-officer activity |
| Mutations | `Sync Mutation Log` | Status histogram, failure_rate |
| Diagnostics | `diagnostics_json` on telemetry | Ad hoc; no PII by contract |
| Feedback | `Pilot Operational Feedback` | Count by category, open = `workflow_status=new` |
| Ops events | `Operational Log` | Recent 25 in dashboard |

**Principles:** Lightweight append-only writes; admin reads via `dashboard` API; no OLAP / no maps.

---

## 4. Operational support workflow

1. **Officer** — Uses app offline-first; sends **Pilot feedback** (menu) for UX/sync/inventory issues.
2. **Mobile** — Posts heartbeat after each successful sync; diagnostic bundle on sync errors.
3. **Admin** — Opens `/pilot_dashboard` or `bench execute` dashboard; reviews queue backlog + sync health daily.
4. **Triage** — Feedback DocType `workflow_status`: new → reviewed → resolved.
5. **Escalation** — Critical severity + inventory category → inventory reconcile + block stock check.

---

## 5. Rollout strategy

| Wave | Audience | Duration | Gate |
|------|----------|----------|------|
| **Staging** | 2 internal testers | 3 days | `phase17_verify_pilot` ok |
| **Pilot A** | 5–10 officers, 1 block | 2 weeks | Metrics above |
| **Pilot B** | 30 officers, multi-block | 2 weeks | No queue growth regressions |
| **Production** | Phased by block | — | Sign-off checklist |

---

## 6. Pilot tooling delivered

| # | Feature | Implementation |
|---|---------|----------------|
| 1 | Pilot checklist | [docs/PILOT_DEPLOYMENT_CHECKLIST.md](./docs/PILOT_DEPLOYMENT_CHECKLIST.md) |
| 2 | Staging workflow | [docs/STAGING_DEPLOYMENT_WORKFLOW.md](./docs/STAGING_DEPLOYMENT_WORKFLOW.md) |
| 3 | Officer onboarding | `onboarding_checklist` API + `OnboardingScreen` |
| 4 | Admin telemetry | `pilot_ops.dashboard`, `/pilot_dashboard` |
| 5 | Sync health | `sync_health` + dashboard section |
| 6 | Queue backlog | `queue_backlog` from device telemetry |
| 7 | Inventory mismatch | `inventory_health` (Phase 16 reconcile) |
| 8 | Diagnostic upload | `diagnostic_upload` + `PilotTelemetryService` |
| 9 | Operational logs | `Operational Log` DocType |
| 10 | Release tracking | Heartbeat `app_version` + sync screen label |

**APIs:** `agriflow.api.v1.pilot_ops.*`  
**Deploy:** `scripts/phase17_deploy_to_bench.sh` (use LF line endings on WSL)

---

## 7. Pilot deployment report (bench validation)

**Staging deploy (dev site):**

```bash
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase17_install.execute
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase17_verify_pilot.execute
```

**Verify result:** `ok: true`

| Check | Result |
|-------|--------|
| heartbeat | ok |
| feedback_submit | ok |
| diagnostic_upload | ok |
| onboarding_checklist | ok |
| dashboard | ok |
| jwt_still_ok | ok |

---

## 8. Telemetry overview (sample snapshot)

From verify run after install:

- **Queue devices (24h):** 1 (`phase17-verify`)
- **Open feedback:** 1 (verify submission)
- **Sync health keys:** sessions_opened, mutations_by_status, failure_rate, etc.

Multi-device simulation: `phase17_pilot_simulation.execute` seeds `pilot-sim-01..03` heartbeats for dashboard aggregation tests.

---

## 9. Sync health metrics

Aggregated server-side (`_sync_health_window`, 7 days):

- `sessions_opened` / `sessions_completed`
- `mutations_by_status` (success, skipped, failed, conflict, dependency_failed)
- `failure_rate` = (failed + conflict + dependency_failed) / total

Mobile mirrors queue depth via heartbeat (`queue_pending`, `queue_conflict`, `queue_failed`).

---

## 10. Inventory reconciliation metrics

Reuses Phase 16 `inventory_reconcile`:

- Warehouse `WH-CENTRAL-01`
- Rule: non-negative on_hand, reserved, available
- Exposed in dashboard as `inventory` block

**Bench:** aligned with Phase 16 verify (0 mismatches on demo data).

---

## 11. Operational UX findings (expected pilot themes)

| Theme | Observation | Mitigation |
|-------|-------------|------------|
| Weak network | Retry/backoff helps; long offline increases queue_pending | Heartbeat alerts; officer training on Sync tab |
| Conflicts | Visible on Sync Status + conflict sheet | Refresh-from-server workflow |
| Inventory shortage | Consume fails server-side | Feedback category `inventory`; reconcile daily |
| Stale APK | `app_versions` matrix in dashboard | Force upgrade policy per block |
| Onboarding | First-run checklist | Hive flag `pilot_onboarding_done` |

---

## 12. Remaining deployment risks

| # | Risk | Severity |
|---|------|----------|
| 1 | No Sentry — only structured diagnostic JSON | Medium |
| 2 | Field Staff role may be missing on some sites | High |
| 3 | CRLF on Windows deploy scripts | Low (use WSL cp or dos2unix) |
| 4 | Pilot dashboard requires System Manager login | Low |
| 5 | Flutter not validated in CI on this machine | Medium — run locally |
| 6 | Concurrent sync on same task still last-write-wins | Medium |

---

## 13. Recommended production rollout plan

1. **Week 0** — Staging: deploy Phase 17, run checklist + simulation script.
2. **Week 1** — Pilot A: 5–10 devices, daily dashboard review, feedback triage.
3. **Week 2** — Tune retry/queue thresholds from telemetry; fix top 3 feedback categories.
4. **Week 3–4** — Pilot B scale; enforce max 2 APK versions.
5. **Go-live** — Production site JWT + Redis; disable `DEV_AUTH_STUB`; pin `API_BASE_URL`; ops runbook in [STAGING_DEPLOYMENT_WORKFLOW.md](./docs/STAGING_DEPLOYMENT_WORKFLOW.md).

---

## 14. Mobile validation (local)

```bash
cd mobile/agriflow_mobile
flutter pub get
flutter gen-l10n
flutter test
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 \
  --dart-define=APP_VERSION=0.17.0 \
  --dart-define=DEV_AUTH_STUB=true
```

**Scenarios to run on device:** weak network, 4h offline, upgrade with pending queue, send feedback, complete onboarding.

---

## 15. File map

| Repo path | Bench path |
|-----------|------------|
| `scripts/phase17_pilot_ops_api.py` | `api/v1/pilot_ops.py` |
| `scripts/phase17_install.py` | `install/phase17_install.py` |
| `scripts/phase17_verify_pilot.py` | `install/phase17_verify_pilot.py` |
| `scripts/phase17_pilot_simulation.py` | `install/phase17_pilot_simulation.py` |
| `scripts/phase17_doctypes/*` | `project_lifecycle/doctype/*` |
| `mobile/.../features/pilot_ops/` | — |
