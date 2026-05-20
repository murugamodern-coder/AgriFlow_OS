# Audit Pass 1: Roadmap-vs-Reality

**Date:** 2026-05-20  
**Auditor mode:** Report only — no fixes applied  
**Scope:** Documented roadmap (PRD, ARCHITECTURE, DOCTYPES, IMPLEMENTATION_PLAN, PHASE11–24 reports) vs repository + deploy scripts  

---

## Overall Status

| Metric | Value |
|--------|--------|
| **Score** | **42 / 100** |
| **Verdict** | **MAJOR GAPS** |

**Executive summary:** The project has a **strong backend spine** (geography, farmer registry, 12-stage Farmer Project lifecycle, timeline, tasks, sync, notifications, inventory ledger) delivered via **phase bootstrap scripts** copied to a WSL Frappe bench. Phases 17–24 added **operational/commercial/GA/enterprise/observability** layers that are **not** the nine PRD product modules. Against the **full Phase 1 product roadmap** (9 modules, billing, MIMIS Excel, owner profit, Tamil-first field UX), the **mobile app and several P1 DocTypes/APIs are largely missing**. A **pilot demo** of timeline + tasks + sync is feasible on bench; a **client submission** claiming full AgriFlow OS per PRD would be **misleading**.

**Repository layout caveat:** There is **no committed `backend/agriflow/` tree** in this repo. Frappe artifacts are generated from `scripts/phase*_bootstrap.py` into `~/workspace/frappe-bench/apps/agriflow/`. This audit inspected **repo sources** (`scripts/`, `mobile/`, `infra/`) and phase reports; bench runtime was not re-executed in this pass.

---

## ✅ What Works (Verified)

### Backend spine (scripts → bench pattern)

| Area | Evidence | Notes |
|------|----------|--------|
| Geography hierarchy | `scripts/phase6_geography_bootstrap.py` | District, Block, Cluster, Village, Officer, **Officer Assignment History** |
| Farmer registry | `scripts/phase7_farmer_bootstrap.py` | Farmer + **Farmer Land Parcel** child; `aadhaar_last4` validation (last 4 only) |
| Farmer Project + 12 stages | `scripts/phase8_project_bootstrap.py` | `STAGES` list (1–12), sequential `stage_sequence` guard in lifecycle service |
| Timeline engine | `scripts/phase9_timeline_bootstrap.py`, `phase9b_api_bootstrap.py` | Timeline events, MIMIS gate events (not Excel import) |
| Task engine | `scripts/phase10_task_bootstrap.py`, `phase10b_task_api_bootstrap.py` | **Project Task** (not generic `Task` DocType name) |
| Offline sync | `scripts/phase11_sync_bootstrap.py`, `phase11_sync_api.py` | `sync.pull` / `sync.push` with auth checks |
| Notifications | `scripts/phase12_notification_bootstrap.py` | Notification preference + delivery log patterns |
| Inventory ledger | `scripts/phase13_inventory_bootstrap.py`, `phase13_inventory_api.py` | Inventory Item, Warehouse (`legacy_godown_key`), Stock Ledger Entry, Project Material Allocation; reserve/consume verified in `phase13_verify_inventory.py` |
| Auth (JWT) | `scripts/phase16_auth_api.py` | Username/password login, JWT pair + refresh rotation (not OTP) |
| Block-scoped API access | `scripts/phase16_permissions.py` | `assert_block_scope`, `assert_project_access` |
| Phase verify reports | `PHASE11_SYNC_REPORT.md` … `PHASE24_PERFORMANCE_OBSERVABILITY_REPORT.md` | Bench `execute` verifiers claim `ok: true` for phased scope |

### Mobile (partial vertical slice)

| Area | Evidence | Notes |
|------|----------|--------|
| Feature-first + Riverpod + go_router | `mobile/agriflow_mobile/lib/features/`, `lib/app/router/app_router.dart` | No `Navigator.push` in feature routes |
| Auth + secure tokens | `lib/features/auth/`, `lib/core/storage/secure_token_store.dart` | Password login; JWT in secure storage |
| Timeline feed (online/offline sync) | `lib/features/project_lifecycle/presentation/timeline_feed_screen.dart` | Event list + pull-to-refresh + offline note queue |
| Tasks inbox + detail | `lib/features/tasks/` | Task complete via `MutationQueue` |
| Sync status + conflicts | `lib/features/sync/presentation/sync_status_screen.dart` | Queue repair / conflict UX (Phase 20+) |
| Notifications inbox | `lib/features/notifications/` | |
| Offline queue (Drift) | `lib/core/sync/mutation_queue.dart` | Entities: `task`, `timeline` (+ inventory consume path) |
| Hive watermarks | `lib/core/sync/sync_orchestrator.dart`, `lib/core/storage/hive_boxes.dart` | Sync meta + watermarks (not full entity cache per PRD) |
| Tamil i18n (partial) | `lib/l10n/app_ta.arb`, `app_en.arb` | Core nav/login/sync strings translated |
| Design tokens | `lib/core/design_tokens/color_tokens.dart` | Centralized colors (not scattered `Color(0x…)` in widgets) |

### Infrastructure & docs

| Area | Evidence |
|------|----------|
| Staging/prod Docker templates | `infra/docker/docker-compose.staging.yml`, `.env.*.example` |
| Ops/deployment guides | `docs/STAGING_DEPLOYMENT_WORKFLOW.md`, `docs/BACKUP_RESTORE_GUIDE.md`, `docs/LOCAL_LIVE_DEMO.md` |
| README bootstrap | `README.md` (bench + Flutter paths; demo credentials in phase reports) |

---

## ⚠️ Partial Implementations

### A. DocTypes (Backend)

| DocType (audit list) | Status | Gap |
|---------------------|--------|-----|
| District, Block, Village, Cluster | ✅ Bootstrap | Permissions: **System Manager only** in bootstrap (`PERMS_SM`) — not full 8-role matrix |
| Officer, Officer Assignment History | ✅ Bootstrap | Historical transfer logic in phase6 service code; not re-verified on bench here |
| Farmer, Farmer Land | ✅ Bootstrap | **Farmer Document**, **Farmer Tag** not found in scripts |
| Farmer Project + 12-stage machine | ✅ Service-level | Not Frappe **Workflow** doc; custom `lifecycle.py`. Stage history child exists in phase8 |
| Lead Source | ❌ Not in scripts | — |
| Item / Item Variant | ⚠️ Renamed | **Inventory Item** (not ERPNext Item + Variant) |
| Warehouse, Stock Entry | ⚠️ Different model | **Stock Ledger Entry** + **Project Material Allocation** (not `Stock Entry` / `Stock Reservation` DocTypes from checklist) |
| Sales Invoice (`sale_mode`) | ❌ | No bootstrap or API |
| Task (GPS check-in) | ⚠️ **Project Task** | GPS/photo fields not confirmed in bootstrap skim; name differs from audit list |
| Service Visit | ❌ | — |
| Expense Entry (safe labels) | ❌ | Specified in DOCTYPES.md / IMPLEMENTATION_PLAN Phase 14 — **no `phase14_*` scripts** |
| Supplier (Phase 2) | ❌ | Expected deferred |
| MIMIS Import Batch / Reconciliation Row | ❌ | Only `mimis_gate_status` on project + timeline `mimis_gate_updated` events |

**Permissions (CRITICAL partial):** DocType JSON in phase6–8 bootstraps sets `"permissions": [System Manager only]`. Runtime protection relies heavily on **custom API** (`phase16_permissions.py`), not documented per-role DocType permissions for Owner, Field Staff, Store Keeper, etc.

### B. APIs (Backend)

| API (audit list) | Status | Evidence |
|------------------|--------|----------|
| Auth OTP send/verify | ❌ | `phase16_auth_api.py` — password + JWT only |
| JWT refresh | ✅ | `phase16_auth_api.py` + `auth_jwt` module referenced |
| CRUD per DocType | ⚠️ | Domain APIs for project/timeline/task/farmer/master/inventory; not full CRUD surface for all entities |
| `/api/sync/bulk` | ⚠️ | `agriflow.api.v1.sync.push` / `pull` (Frappe method paths), not REST `/api/sync/bulk` |
| MIMIS upload-excel + reconciliation | ❌ | Only in `API_CONTRACTS.md`; no `phase*mimis*` API script |
| Owner dashboard profit + alerts | ❌ PRD sense | Enterprise/GA/observability dashboards (`phase20`–`phase24`) — **not** owner P&L per PRD M9 |
| `/api/reports/*` | ❌ | Not found in scripts |
| WhatsApp send-invoice | ❌ | Not found |
| Rate limiting | ❌ | No matches in `scripts/` |
| CORS for Flutter | ⚠️ | Documented for local demo (`docs/LOCAL_LIVE_DEMO.md`); not a committed secure production CORS policy |

### C. Flutter App (`lib/features/`)

| Feature folder (audit) | Present? |
|------------------------|----------|
| `auth/` | ✅ |
| `farmer/` | ❌ |
| `catalog/` | ❌ |
| `billing/` | ❌ |
| `project/` (12-stage timeline UI) | ❌ — only `project_lifecycle/` **event feed** |
| `task/` | ✅ (`tasks/`) |
| `service/` | ❌ |
| `officer/` | ❌ |
| `expense/` | ❌ |
| `dashboard/` | ⚠️ Shell only (`dashboard_shell.dart` — nav tabs, not owner profit) |
| `sync/` | ✅ |
| Extra (not in audit checklist) | `pilot_ops/`, `commercial/`, `readiness/`, `notifications/`, `inventory/` (remote only) |

**Router proof** — only login, onboarding, feedback, timeline, tasks, notifications, sync:

```29:87:mobile/agriflow_mobile/lib/app/router/app_router.dart
    routes: [
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      // ... timeline, tasks, notifications, sync branches only
```

### D. Critical Behaviors

| Behavior | Status | Finding |
|----------|--------|---------|
| Officer transfer preserves history | ⚠️ Backend | `Officer Assignment History` in phase6; mobile does not surface history |
| Expense NOT linked to `officer_name` | ⚠️ N/A | **Expense Entry DocType not implemented** — cannot verify safe-label rule |
| Stock auto-reserve at Work Order Received | ❌ Auto | Manual `allocation_reserve` API (`phase13`); **no lifecycle hook** found tying stage 8 → reserve |
| Workflow: no stage skip | ✅ Backend | `target_seq != stage_sequence + 1` in `phase8_project_bootstrap.py` lifecycle service |
| Field Staff cluster isolation | ⚠️ Block only | `get_allowed_blocks()` — **cluster-level** filter not implemented in `phase16_permissions.py` |
| Offline bill → Hive queue | ❌ | No billing; queue supports task/timeline/inventory consume only |
| Two-godown isolation | ⚠️ | Separate warehouses via `legacy_godown_key`; **not** named Main Godown / Office Store enforcement in code |
| 12-stage timeline **screen** | ❌ | `TimelineFeedScreen` = chronological **events**, not 12-stage stepper UI |
| WhatsApp invoice PDF server-side | ❌ | — |
| MIMIS Excel reconciliation preview | ❌ | — |

### E. Documentation

| Item | Status |
|------|--------|
| README setup | ✅ Extensive — but §1 still says app dirs “will appear” (stale vs scripts/mobile reality) |
| `.env.example` at repo root | ❌ | Only `infra/docker/.env.*.example` |
| Zoho migration scripts | ❌ | Mentioned in IMPLEMENTATION_PLAN only |
| Tamil i18n | ⚠️ ~**63%** key parity | `app_en.arb` ~103 lines vs `app_ta.arb` ~65 lines; hardcoded `'Note'` in `timeline_feed_screen.dart` ~80 |

---

## ❌ Missing Entirely

| Item | Severity | Notes |
|------|----------|-------|
| Mobile M1 Farmer registration/list/search | **CRITICAL** | No `lib/features/farmer/` |
| Mobile M3 Billing (cash & carry, project sale, print, WhatsApp) | **CRITICAL** | — |
| Mobile M4 MIMIS Excel upload UI | **CRITICAL** | — |
| Mobile M7 Service / AMC | **HIGH** | — |
| Mobile M8 Officer hierarchy filter UI | **HIGH** | — |
| Mobile M9 Owner profit dashboard | **CRITICAL** | — |
| Expense Entry DocType + APIs | **HIGH** | Phase 14 in plan, no code |
| MIMIS Import Batch + reconciliation APIs | **HIGH** | — |
| Sales Invoice + `sale_mode` | **HIGH** | — |
| Service Visit DocType | **HIGH** | — |
| OTP authentication | **MEDIUM** | Contract vs implementation mismatch |
| API rate limiting | **MEDIUM** | — |
| WhatsApp / Evolution invoice integration | **MEDIUM** | — |
| Reports API (`/api/reports/*`) | **MEDIUM** | — |
| Committed `backend/` Frappe app in monorepo | **MEDIUM** | Deployment reproducibility risk |
| Root `.env.example` | **LOW** | — |
| Zoho import migration (even stub) | **LOW** | — |

---

## 🐛 Implementation Issues

| Issue | Location | Severity |
|-------|----------|----------|
| DocType permissions default to System Manager only | `scripts/phase7_farmer_bootstrap.py`, `phase8_project_bootstrap.py` (`PERMS_SM`) | **CRITICAL** — desk/mobile bypass if raw Frappe CRUD enabled |
| README claims scaffolding-only repo | `README.md` L59–62 | **MEDIUM** — misleads auditors/clients |
| Timeline note label not i18n | `mobile/.../timeline_feed_screen.dart` ~80 (`labelText: 'Note'`) | **MEDIUM** — violates .cursorrules |
| Audit checklist DocType names ≠ implementation | Task vs Project Task; Stock Entry vs Stock Ledger Entry | **MEDIUM** — integration/docs drift |
| Sync push path limited on mobile | `mutation_queue.dart` — only `task`, `timeline` | **HIGH** — farmer/project creates not offline-queued |
| PRD “reads: Hive local cache” | Primary entity store is **Drift** (`app_database.dart`); Hive for meta/telemetry | **LOW** — architecture drift |
| Phase reports vs product scope | PHASE20–24 “production ready” for **ops**; PRD modules 1–9 largely absent on mobile | **HIGH** — AI confidence trap risk |

---

## 📊 Module-by-Module Score

| Module | PRD intent | Implemented % | Issues |
|--------|------------|---------------|--------|
| **M1 Farmer** | Registry, land, tags, mobile CRUD | **35%** | Backend bootstrap; no mobile farmer feature; tags/docs missing |
| **M2 Inventory** | 2 godowns, billing stock | **50%** | Ledger + reserve/consume API; no catalog/barcode mobile; godown names not enforced |
| **M3 Billing** | Cash & carry + project sale | **0%** | Entire module absent |
| **M4 MIMIS** | Excel reconciliation | **10%** | Gate status/events only; no import batch/upload/preview |
| **M5 Project lifecycle** | 12-stage workflow + timeline UX | **55%** | Strong backend transitions; mobile = event feed not stage UI |
| **M6 Task engine** | Follow-ups, GPS, photos | **65%** | Inbox/detail/sync; GPS/photo proof not verified in mobile |
| **M7 Service / AMC** | 3-year service | **0%** | — |
| **M8 Officer network** | Hierarchy + safe expense | **30%** | Assignment history backend; no filter UI; no Expense Entry |
| **M9 Profit dashboard** | Owner visibility | **5%** | Ops/GA dashboards only; no P&L cards for owner |

**Phases 17–24 (extra):** Commercial/pilot/GA/enterprise/observability — **~80% of stated phase goals** per their reports, but **orthogonal** to PRD module completion above.

---

## 🚨 Top 5 Things to Fix Before Submission

1. **Ship PRD-critical mobile modules (minimum demo path)** — Farmer registration (offline), 12-stage project screen with guarded transitions, owner dashboard skeleton. *Impact: client expects 9 modules; currently ~3 surfaces.*  
2. **MIMIS Excel reconciliation (backend + owner UI)** — `upload_excel`, preview, apply per `API_CONTRACTS.md` §20. *Impact: core differentiator for subsidy dealer.*  
3. **DocType role permissions matrix** — Replace System-Manager-only bootstraps with Owner / Office Manager / Field Staff / Store Keeper etc. per DOCTYPES.md. *Impact: security + demo credibility.*  
4. **Billing + inventory godown rules (M2+M3)** — Sales flow, Office Store deduction, two-warehouse isolation. *Impact: daily operations revenue path.*  
5. **Align claims documentation** — Update README + phase reports to separate **“pilot slice ready”** vs **“PRD Phase 1 complete”**; add root `.env.example`. *Impact: prevents submission trust failure.*

---

## Checklist Summary (Audit Pack)

| Section | Pass | Fail | Partial |
|---------|------|------|---------|
| A. DocTypes | 10 | 8 | 6 |
| B. APIs | 3 | 7 | 4 |
| C. Flutter features | 4 | 7 | 1 |
| D. Critical behaviors | 1 | 6 | 4 |
| E. Documentation | 2 | 3 | 2 |

---

## Honest Verdict for Stakeholders

| Audience | Recommendation |
|----------|----------------|
| **Internal pilot** | Proceed with **timeline + tasks + sync** demo on bench/tunnel; set expectations. |
| **Client submission (full PRD)** | **Not ready** — MAJOR GAPS; 3–7+ weeks focused product work (per audit pack estimate) for minimum credible scope. |
| **Phase 17–24 ops maturity** | Substantial **engineering ops** work exists; do not conflate with **product module completion**. |

---

## DO NOT FIX ANYTHING NOW.

This report is evidence for Pass 2–5 and `docs/FINAL_AUDIT_SUMMARY.md` synthesis.

*Generated by Audit Pass 1 — Roadmap-vs-Reality Gap Analysis.*
