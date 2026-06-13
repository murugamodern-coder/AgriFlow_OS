# AgriFlow OS — Product Standard 360° Audit

**Audit date:** 2026-06-06  
**Auditor mode:** Read-only (live DB + repo evidence)  
**Site:** `dev.agriflow.local`  
**Bench:** `/home/muruga/workspace/frappe-bench` (`./env/bin/bench`)  
**Repo:** `C:\AgriFlow_OS\AgriFlow_Main` / branch `stabilization-v1`  
**Backend:** 🟢 LIVE — Desk HTTP 301 → `/app`; operational console routes HTTP 200  

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Project location** | `C:\AgriFlow_OS\AgriFlow_Main` |
| **Backend** | 🟢 LIVE (Frappe Desk + MariaDB populated) |
| **DocTypes implemented (Agriflow modules)** | **33** in DB (33 JSON in repo) |
| **DocTypes planned in DOCTYPES.md (incl. P1)** | **~50+** spec rows — **~66% schema breadth** |
| **API `@frappe.whitelist` decorators (bench app)** | **156** occurrences (~**70+** distinct mobile/ops methods in `api/v1/`) |
| **API contracts documented (`API_CONTRACTS.md`)** | **39** named API sections |
| **Mobile feature folders** | **10** (`auth`, `dashboard`, `farmer`, `project_lifecycle`, `tasks`, `notifications`, `sync`, `inventory` data-only, `commercial`, `pilot_ops`, `readiness`) |
| **Mobile `*_screen.dart` files** | **11** screens |
| **PRD-expected mobile screens (8)** | **6 built**, **1 skeleton**, **1 missing** |
| **Live row counts (key tables)** | Farmers **2**, Projects **2**, Tasks **13**, Notifications **19**, Timeline **51**, Sync Sessions **21** |
| **Geography** | District **1**, Blocks **12**, Cluster **1**, Village **1** — partial vs 12-block ops model |
| **12-stage master** | **12/12** `Project Stage` rows loaded |
| **Frappe Workflow on Farmer Project** | **None** — lifecycle is **custom Python service** |
| **Localization (mobile demo path)** | **~98%** Tamil on 9 demo screens per `docs/I18N_COVERAGE.md`; **~120+** ARB keys |
| **Backend automated tests** | **0** Python test files under `backend/` |
| **Mobile tests** | **13** Dart test files (mostly sync/config) |
| **Overall maturity** | **MVP+ / PILOT-DEV** (strong spine, weak PRD breadth & production hardening) |
| **Confidence score** | **62 / 100** |

---

## What This Product Is RIGHT NOW

AgriFlow OS is a **working Frappe v15 backend** with a **custom 12-stage subsidy lifecycle** centered on `Farmer Project`, backed by real data on `dev.agriflow.local` (2 farmers, 2 projects, 13 tasks, 51 timeline events, 19 notifications). The **hero workflow is implemented in code** (`ProjectLifecycleService`) with sequential stage enforcement, MIMIS gate fields, timeline emission, task engine, sync sessions, inventory ledger primitives, and notification fanout — not as a Frappe Workflow document.

The **mobile app** is a **partial offline-first client**: login, dashboard shell, farmer list, project timeline (12 stages UI), task inbox/detail, notifications, and sync status are built with Tamil-first i18n on demo paths. **Inventory, billing, MIMIS import, service/AMC, profit reports, and farmer registration** are largely **backend-spec or API-only** — not end-user complete.

Operations maturity is **ahead of core dealer features**: observability, pilot, GA, and enterprise **web consoles return HTTP 200**, and **156 whitelisted endpoints** exist (many admin/ops). **Role model on key DocTypes is still thin** (System Manager only in JSON permissions; only **Field Staff** custom role observed in DB sample query).

---

## What This Product Is NOT (Yet)

- **Not production-ready** for 15 daily users across 12 blocks with strict RBAC, LGD geography, and billing.
- **Not a complete PRD delivery** — missing DocTypes: `Expense Entry`, `Service Visit`, `Sales Invoice`, `MIMIS Import Batch`, `Lead`, `Farmer Document`, etc. (spec-only in `DOCTYPES.md`).
- **Not MIMIS-integrated** — gate fields exist; **no upload/reconciliation API or DocTypes** in repo.
- **Not offline-complete on mobile** — no farmer create/edit screen; inventory/commercial UIs absent.
- **Not ERPNext** — custom agriflow modules only; no stock/accounting module parity.
- **Not validated by backend test suite** — zero `test_*.py` in backend.

---

## Area-by-Area Findings

### Area 1: Backend DocType Inventory

**Evidence:** Live DB query via `bench --site dev.agriflow.local mariadb` + repo `find …/doctype/*.json` → **33** files.

| DocType | Module | Submittable | Repo path |
|---------|--------|-------------|-----------|
| Farmer | Farmer Registry | No | `backend/agriflow/agriflow/farmer_registry/doctype/farmer/farmer.json` |
| Farmer Land Parcel | Farmer Registry | No | `…/farmer_land_parcel/farmer_land_parcel.json` |
| District | Officer Network | No | `…/officer_network/doctype/district/district.json` |
| Block | Officer Network | No | `…/block/block.json` |
| Cluster | Officer Network | No | `…/cluster/cluster.json` |
| Village | Officer Network | No | `…/village/village.json` |
| Officer | Officer Network | No | `…/officer/officer.json` |
| Officer Assignment History | Officer Network | No | `…/officer_assignment_history/officer_assignment_history.json` |
| Farmer Project | Project Lifecycle | No | `…/project_lifecycle/doctype/farmer_project/farmer_project.json` |
| Project Stage | Project Lifecycle | No | `…/project_stage/project_stage.json` |
| Project Stage History | Project Lifecycle | No | `…/project_stage_history/project_stage_history.json` |
| Timeline Event | Project Lifecycle | No | `…/timeline_event/timeline_event.json` |
| Project Task | Task Engine | No | `…/task_engine/doctype/project_task/project_task.json` |
| Project Task Assignment History | Task Engine | No | `…/project_task_assignment_history/…` |
| Warehouse | Inventory | No | `…/inventory/doctype/warehouse/warehouse.json` |
| Inventory Item | Inventory | No | `…/inventory_item/inventory_item.json` |
| Stock Ledger Entry | Inventory | No | `…/stock_ledger_entry/stock_ledger_entry.json` |
| Project Material Allocation | Inventory | No | `…/project_material_allocation/…` |
| Notification | Notification Engine | No | `…/notification_engine/doctype/notification/notification.json` |
| Notification Delivery Log | Notification Engine | No | `…/notification_delivery_log/…` |
| Notification Preference | Notification Engine | No | `…/notification_preference/…` |
| Sync Session | Sync Engine | No | `…/sync_engine/doctype/sync_session/sync_session.json` |
| Sync Mutation Log | Sync Engine | No | `…/sync_mutation_log/…` |
| Customer Onboarding | Project Lifecycle | No | `…/customer_onboarding/…` |
| Support Ticket | Project Lifecycle | No | `…/support_ticket/…` |
| Operational Incident / Log | Project Lifecycle | No | `…/operational_incident/…`, `operational_log/…` |
| Pilot Device Telemetry / Feedback | Project Lifecycle | No | `…/pilot_device_telemetry/…`, `pilot_operational_feedback/…` |
| Device Push Token / Push Delivery Log | Project Lifecycle | No | `…/device_push_token/…`, `push_delivery_log/…` |
| GA Release Signoff / Tenant Ops Record | Project Lifecycle | No | `…/ga_release_signoff/…`, `tenant_ops_record/…` |

**PRD module mapping:** Core **P0 spine** (Farmer, Project, Task, Geography, Sync, Notify, Inventory ledger) is present. **P1/P2** entities in `DOCTYPES.md` are largely **absent**.

**Note:** `module LIKE '%griflow%'` returned empty — Frappe stores modules as **"Farmer Registry"**, **"Officer Network"**, etc., not the string `Agriflow`.

---

### Area 2: Module Coverage vs PRD

| PRD Module | Required (PRD/DOCTYPES) | Found | Status | Evidence |
|------------|---------------------------|-------|--------|----------|
| **M1 Farmer Registry** | Farmer, FarmerLand, FarmerDocument, FarmerTag, LeadSource | Farmer, Farmer Land Parcel only | 🟡 Partial | Missing Lead/Document/Tag DocTypes |
| **M2 Inventory** | Item, ItemVariant, Warehouse, StockEntry, StockReservation | Inventory Item, Warehouse, Stock Ledger Entry, Project Material Allocation | 🟡 Partial | No `Stock Entry` DocType; API `stock_entry_create` in `inventory.py` |
| **M3 Dual Billing** | SalesInvoice + `sale_mode` | No Sales Invoice DocType | ❌ Missing | `commercial.py` ops dashboards only |
| **M4 MIMIS Sync** | Upload batch, reconciliation rows | MIMIS fields on Farmer Project only | 🟡 Partial | `farmer_project.json` mimis_*; no `mimis.*` API in `backend/agriflow/agriflow/api/` |
| **M5 12-Stage Lifecycle** | FarmerProject + 12 states | Farmer Project + 12 Project Stage fixtures | ✅ Full | DB: 12 stages; `lifecycle.py` sequential transitions |
| **M6 Task Engine** | Task + GPS fields | Project Task | 🟡 Partial | No gps/lat/lng in `project_task.json` |
| **M7 Service/AMC** | ServiceVisit | None | ❌ Missing | No DocType JSON |
| **M8 Officer Network** | Officer, Assignment, ExpenseEntry | Officer, Assignment History; no Expense Entry | 🟡 Partial | **0** assignment rows in DB |
| **M9 Profit View** | Reports endpoints | Ops/GA/commercial APIs, no P&L DocType | 🟡 Partial | `commercial.py`, `ga.py` — not dealer profit dashboard |

---

### Area 3: API Surface

**Evidence:** `grep -r '@frappe.whitelist' apps/agriflow` → **156** hits on live bench.

**Core mobile spine (`backend/agriflow/agriflow/api/v1/`):**

| Module file | Whitelisted methods (sample) |
|-------------|------------------------------|
| `auth.py` | `login`, `refresh`, `logout`, `permissions` |
| `farmer.py` | `list`, `get` |
| `project.py` | `timeline`, `timeline_since`, `transition` |
| `task.py` | `list`, `get`, `create`, `update`, `complete` |
| `sync.py` | `pull`, `push` |
| `notification.py` | `list`, `unread_count`, `mark_read`, `mark_all_read` |
| `inventory.py` | `items`, `warehouses`, `stock_on_hand`, `ledger_list`, movements, allocations, `stock_entry_create` |
| `push.py` | `register_token`, `delivery_metrics`, `process_queue` |

**Documented but not in `api/v1/`:** `master.districts`, `master.blocks`, `master.villages`, `master.clusters`, `mimis.upload_excel`, `mimis.batch_status` (`API_CONTRACTS.md` §19–20) — **spec-only**.

**Ops / phase deliverables (heavy surface):** `observability.py` (11), `enterprise.py` (14), `ga.py` (16), `pilot_ops.py` (9), `pilot.py` (8), `commercial.py` (10), `readiness.py` (4).

**Count vs PRD:** Auth ✅, Sync ✅, Task ✅, Project ✅, Farmer (read) ✅, Notifications ✅, Inventory API ✅, **MIMIS ❌**, **master geography pull ❌**, **WhatsApp ❌**, **dealer profit dashboard ❌**.

---

### Area 4: Data Population

**Evidence:** Live MariaDB counts (`bench --site dev.agriflow.local mariadb`), 2026-06-06.

| DocType | Row count | Interpretation |
|---------|-----------|----------------|
| Farmer | **2** | Matches user-visible "Farmer 2 Active" |
| Farmer Project | **2** | Partial demo (stages: 1× `lead_captured`, 1× `material_dispatched`) |
| Project Task | **13** | Task engine exercised |
| Officer | **1** | Minimal |
| Officer Assignment History | **0** | ⚠️ Officer cluster assignment not seeded |
| District | **1** | TVM fixture |
| Block | **12** | Phase 6 fixtures |
| Cluster | **1** | Under-seeded vs 12 blocks |
| Village | **1** | Under-seeded |
| Warehouse | **2** | Fixtures |
| Inventory Item | **2** | Fixtures |
| Stock Ledger Entry | **10** | Some inventory movement history |
| Project Stage | **12** | Complete |
| Timeline Event | **51** | Lifecycle/timeline active |
| Notification | **19** | Notification engine active |
| Sync Session | **21** | Sync engine used |
| User (enabled, non-system) | **1** | Below "15 users planned" |
| Role | **28** | Mostly Frappe defaults + Field Staff |
| Customer Onboarding | **0** | |
| Support Ticket | **0** | |

**Verdict:** **Not empty** — seed/demo scripts have run — but **geography and users are pilot-thin**, not district-scale.

---

### Area 5: 12-Stage Workflow

**1. Frappe Workflow attached to Farmer Project?**  
**No.** DB: `tabWorkflow` query returned **no rows** for Farmer Project. No workflow JSON under `apps/agriflow/**/workflow*`.

**2. Twelve states present?** ✅ **Yes** — `tabProject Stage`:

| Seq | stage_key |
|-----|-----------|
| 1 | lead_captured |
| 2 | eligibility_check |
| 3 | documents_collected |
| 4 | mimis_registered |
| 5 | field_survey |
| 6 | quotation_generated |
| 7 | pre_inspection_approval |
| 8 | work_order_received |
| 9 | material_dispatched |
| 10 | installation_done |
| 11 | post_inspection_approval |
| 12 | subsidy_released |

**3. PRD label alignment:** Matches PRD stage names (snake_case keys).

**4. Sequential vs skip:**  
**Sequential by default.** `ProjectLifecycleService.transition()` requires `target_stage == get_next_stage_key(current)` unless `is_correction` (`lifecycle.py` L129–133). **Skipping is blocked** (verified by `phase8_verify.py` intent). Role matrix in `fixtures/project_stage_role_matrix.json` gates who may transition.

**Implementation type:** Custom service + `Project Stage History` child table — **not** Frappe Workflow UI.

---

### Area 6: Mobile App Reality

**Feature directories:** `auth`, `dashboard`, `farmer`, `project_lifecycle`, `tasks`, `notifications`, `sync`, `inventory` (data only), `commercial`, `pilot_ops`, `readiness`.

| PRD screen | Status | Evidence |
|------------|--------|----------|
| Login + Dashboard | ✅ Built | `login_screen.dart`, `home_dashboard_screen.dart` |
| Farmer registration form | ❌ Missing | No `farmer_*form*` / create screen |
| Farmer list + profile | 🟡 Partial | `farmer_list_screen.dart`; no profile/detail screen |
| 12-stage Timeline UI | ✅ Built | `project_timeline_screen.dart`, `project_stages.dart` |
| Task feed + detail | ✅ Built | `task_inbox_screen.dart`, `task_detail_screen.dart` |
| Notification panel | ✅ Built | `notification_inbox_screen.dart` |
| Sync status | ✅ Built | `sync_status_screen.dart` |
| Settings + language toggle | 🟡 Skeleton | i18n via ARB; no dedicated settings screen found |

**Extra (ops):** `onboarding_screen.dart`, `feedback_screen.dart` (pilot_ops).

---

### Area 7: Roles & Permissions

**Live DB:** 28 roles; sample query found **Field Staff** + **System Manager** among agriflow-relevant names. **Only 1** enabled non-system user.

**DocType permissions (live DB `tabDocPerm`):**

| DocType | Roles with create |
|---------|-------------------|
| Farmer | System Manager only |
| Farmer Project | System Manager only |

**Gap:** PRD roles (Owner, Office Manager, Office Staff, Store Keeper, etc.) are **documented** but **not wired** in Farmer/Farmer Project JSON permissions. API uses **User Permission on Block** (`permissions.py`) — requires manual setup per user.

---

### Area 8: Operational Consoles

**Evidence:** `curl -H 'Host: dev.agriflow.local' http://127.0.0.1:8000/<route>`

| Route | HTTP |
|-------|------|
| `/observability_console` | **200** |
| `/pilot_ops_dashboard` | **200** |
| `/ga_ops_console` | **200** |
| `/enterprise_ops_console` | **200** |

**Verdict:** Phase 17–24 **web consoles are wired** on live site. These are **admin/ops** surfaces, not dealer staff workflows.

---

### Area 9: Background Jobs & Schedulers

**Evidence:** `backend/agriflow/agriflow/hooks.py`

**`scheduler_events`:**
- **daily:** `agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications`

**`doc_events`:**
- **Officer Assignment History** → `after_insert` / `on_update` → sync `Officer.current_cluster`

**Gap:** No scheduled MIMIS, backup, or sync reconciliation jobs in hooks (those live in `infra/scripts/` externally).

---

### Area 10: I18N Coverage

**Evidence:** `mobile/agriflow_mobile/lib/l10n/app_en.arb` (~363 lines), `app_ta.arb`, `docs/I18N_COVERAGE.md`

| Metric | Value |
|--------|-------|
| Demo-path screens localized | 9/9 claimed **100%** |
| Overall demo Tamil coverage | **~98%** (doc claim) |
| ARB keys | **~120+** |
| Backend Tamil CSV translations | **None found** in agriflow app |

**Settings/language toggle UI:** Not a dedicated screen — locale via app config / ARB.

---

### Area 11: Standard Assessment

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Architecture quality | **8/10** | Clear modules, aggregate root, sync/timeline separation; ops APIs sprawl |
| Code quality | **7/10** | Typed services, validation helpers; 156 whitelists, some phase script duplication |
| Test coverage | **3/10** | 0 backend tests; 13 mobile tests (sync-focused) |
| Documentation | **8/10** | 30+ docs, `API_CONTRACTS.md`, `ARCHITECTURE.md`, prior audits |
| Security | **6/10** | `.env` gitignored; JWT in code; permissions thin on DocTypes; dev secrets pattern in seed docs |
| Deployment readiness | **6/10** | `infra/docker/*`, scripts, checklists — not proven on production Hetzner in this audit |
| Observability | **7/10** | Observability console 200, telemetry DocTypes, SLA scan scheduler |
| Mobile UX polish | **6/10** | Hero timeline + tasks built; no farmer CRUD UI; inventory UI missing |
| Business logic completeness | **5/10** | 12-stage core strong; MIMIS/billing/service/profit missing |
| Demo readiness | **6/10** | Desk + partial mobile path; data exists but geography thin |

**Overall standard label:** **MVP+ moving toward PILOT-DEV** — not production-ready.

---

### Area 12: Industry Comparison

| vs | Stronger | Weaker |
|----|----------|--------|
| **Zoho CRM** | Subsidy **stage discipline**, offline sync design, Tamil mobile | CRM breadth, email campaigns, mature RBAC, reporting |
| **ERPNext default** | Agriculture workflow specificity, timeline/task coupling | Accounting, HR, full stock/AR/AP, established permissions |
| **Custom in-house** | Documentation depth, modular Frappe base, ops consoles | Fewer bespoke dealer reports; incomplete billing/MIMIS |
| **SaaS pilots** | Comparable to **late alpha / early beta** vertical SaaS — core loop demoable, not multi-tenant hardened |

---

## Module Implementation Matrix (Master Table)

| PRD Module | Backend | API | Mobile UI | Data | Workflow | Overall |
|------------|---------|-----|-----------|------|----------|---------|
| M1 Farmer | 55% | 40% (list/get) | 35% (list only) | 2 rows | N/A | **40%** |
| M2 Inventory | 70% | 75% | 10% (remote only) | 14 ledger rows | N/A | **45%** |
| M3 Dual Billing | 10% | 30% (commercial ops) | 0% | 0 invoices | N/A | **15%** |
| M4 MIMIS | 25% (fields) | 0% | 0% | 0 batches | Gate in stage 4 | **15%** |
| M5 Lifecycle | 90% | 80% | 85% timeline | 2 projects | 12/12 stages | **80%** |
| M6 Task Engine | 75% | 80% | 75% | 13 tasks | SLA daily job | **70%** |
| M7 Service/AMC | 0% | 0% | 0% | 0 | N/A | **5%** |
| M8 Officer Network | 65% | 50% | 0% | 1 officer, 0 assignments | Assignment hook | **40%** |
| M9 Profit View | 15% | 40% (ops/commercial) | 0% | N/A | N/A | **20%** |

**Weighted platform completion (rough):** **~48%** of PRD module intent in shippable form.

---

## Top 10 Strengths (Evidence-Based)

1. **Live backend with real data** — Farmers 2, Projects 2, Tasks 13, Timeline 51 (DB counts).
2. **12-stage master fully loaded** — All PRD stages in `tabProject Stage`.
3. **Sequential lifecycle enforcement** — `ProjectLifecycleService.transition()` blocks skips.
4. **Sync engine exercised** — 21 Sync Sessions; `sync.pull` / `sync.push` implemented.
5. **Notification pipeline active** — 19 notifications; fanout + API list/mark-read.
6. **Mobile hero screens exist** — Timeline, tasks, notifications, sync (11 screen files).
7. **Tamil-first mobile demo path** — `docs/I18N_COVERAGE.md` ~98% on 9 screens.
8. **Inventory ledger foundation** — Stock Ledger Entry + allocation API + warehouse fixtures.
9. **Ops consoles deployed** — All four console URLs HTTP 200 on live site.
10. **Architecture documentation** — `ARCHITECTURE.md`, `API_CONTRACTS.md`, `DOCTYPES.md`, 30+ runbooks.

---

## Top 10 Gaps (Evidence-Based)

1. **MIMIS module missing** — No batch DocType/API; impact: **high**; fix-effort: **large**.
2. **Sales / dual billing missing** — No Sales Invoice; impact: **high**; effort: **large**.
3. **Service/AMC missing** — No Service Visit; impact: **medium**; effort: **medium**.
4. **Farmer mobile registration absent** — Field staff cannot enroll farmers offline; impact: **high**; effort: **medium**.
5. **Geography under-seeded** — 1 village / 1 cluster vs 12 blocks; impact: **high** for district demo; effort: **small** (data + RFC codes).
6. **RBAC not production-grade** — DocPerm System Manager only on Farmer/Project; impact: **high**; effort: **medium**.
7. **master.* geography APIs not implemented** — Mobile cannot pull village masters per spec; impact: **medium**; effort: **medium**.
8. **Zero backend tests** — Regression risk; impact: **high**; effort: **ongoing**.
9. **No GPS on tasks** — PRD field survey evidence weak; impact: **medium**; effort: **small**.
10. **Officer assignments empty** — 0 rows; officer filter broken for realistic ops; impact: **medium**; effort: **small** (seed).

---

## Demo Readiness Verdict

**Can demo today (Desk, Administrator):**

- Farmer Registry → 2 farmers  
- Officer Network → District/Blocks/Village masters  
- Project Lifecycle → Farmer Project with stage history / timeline  
- Task Engine → 13 tasks  
- Notification Engine → inbox rows  
- Inventory → warehouses, items, ledger  
- Ops consoles → observability / pilot / GA / enterprise (HTTP 200)

**Can demo today (Mobile, with configured API user + block permission):**

- Login → Home → Farmer list (read)  
- Project timeline (12 stages) for existing project ID  
- Task inbox / detail  
- Notifications  
- Sync status  

**Cannot demo end-to-end as PRD describes:**

- New farmer registration on mobile  
- MIMIS Excel reconciliation  
- Cash & carry invoice  
- Service visit scheduling  
- Owner profit dashboard  
- 12-block officer-filtered operations with full geography  

---

## What "Complete" Would Look Like

| Criterion | Done when |
|-----------|-----------|
| Geography | All 12 blocks + villages seeded; RFC or legacy consistent codes |
| Users | 15 users with Role + User Permission per block |
| MIMIS | Import batch DocType + API + match report |
| Billing | Sales Invoice + sale_mode + desk/mobile capture |
| Mobile | Farmer create/edit offline + master sync |
| RBAC | All PRD roles on DocTypes + API enforcement tested |
| Tests | Backend integration tests for lifecycle + sync + permissions |
| Production | Staging deploy verified, backups drilled, secrets rotated |

**Distance:** ~**52%** remaining to PRD-complete by module matrix above.

---

## Recommended Roadmap to Production

**Week 1 (foundation):**
- Seed RFC E2E geography lane or full 12-block village roster  
- Wire DocType permissions for Owner, Office Manager, Field Staff  
- Create 15 users + User Permissions on blocks  
- Implement `master.blocks` / `master.villages` minimum API  

**Week 2 (mobile dealer path):**
- Farmer registration screen + offline queue  
- Master data sync to Hive  
- End-to-end test: create farmer → project → task on device  

**Month 2 (PRD P1):**
- MIMIS Import Batch + reconciliation API  
- Expense Entry DocType  
- Sales Invoice / commercial flow  
- Backend pytest for lifecycle transitions  
- Service Visit module (M7)  

---

## Risks & Anti-Patterns Detected

1. **Ops/API surface >> dealer features** — 156 whitelists vs 2 farmers; risk of maintaining admin code over core UX.  
2. **Permissions JSON = System Manager only** — Production deployment without DocPerm expansion will fail RBAC audit.  
3. **Dual geography naming** (BLK03 vs TVM-BLK03 vs demo `BLK-CHETP`) — Data confusion without RFC adoption.  
4. **No Frappe Workflow** — Stage logic only in Python; desk users cannot configure transitions without code.  
5. **Zero backend tests** — Lifecycle regressions likely on refactor.  
6. **Spec drift** — `API_CONTRACTS.md` documents APIs not present in `api/v1/`.  

---

## Final Verdict

**This product is currently at the MVP+ / PILOT-DEV standard** — the **subsidy lifecycle spine is real and running on a live site**, with meaningful timeline, task, sync, and notification data. It is **not production-ready** for a 15-user Tiruvannamalai dealer operation because **MIMIS, billing, service, profit, mobile farmer capture, RBAC, and full geography** remain incomplete or unseeded.

**With approximately 4–8 weeks of focused work** (permissions + geography seed + mobile farmer flow + MIMIS/billing P1 + backend tests), it can reach **PILOT-READY** for a controlled block-level rollout. **Production-ready** likely requires **3+ months** including UAT, backup/DR proof, and Tamil desk translations.

**Specific path:** Complete **M5/M6 demo loop on mobile with real masters** → add **M4 MIMIS** and **M3 billing** → harden **RBAC and tests** → district geography at scale.

---

*Audit commands run against live `dev.agriflow.local` on 2026-06-06. No code or data modified during audit.*
