# AgriFlow OS — Production Readiness Roadmap

**Document version:** 1.0  
**Created:** 2026-06-12  
**Branch:** `stabilization-v1`  
**Authoring context:** Senior engineering manager plan — evidence from live audits + git history  
**Baseline maturity:** **89 / 100** (MVP+, post–Week 3 sprint)  
**Target maturity:** **95 / 100** (Pilot-Ready) → **98 / 100** (Production-Ready)

---

## Section 1: Current State Summary

### 1.1 Maturity Score

| Date | Source | Score | Label |
|------|--------|-------|-------|
| 2026-06-06 | `docs/PRODUCT_STANDARD_360_AUDIT.md` | **62 / 100** | MVP+ / pilot-dev (pre-billing sprint) |
| 2026-06-12 | This roadmap (post-sprint delta) | **89 / 100** | MVP+ approaching pilot-ready spine |

**What moved the score (+27 points, evidence-based):**

| Delta | Evidence | Points |
|-------|----------|--------|
| M3 billing backend live | `903e50e`, `billing.py`, ERPNext Sales Invoice + 5 APIs, `test_billing_api.py` smoke pass | +8 |
| Mobile Cash & Carry POS | `aa01e63`, `lib/features/billing/` | +5 |
| Role-based unified app UX | `4c04d4d`, 8 role dashboards, `user_role_provider.dart` | +4 |
| Auth bootstrap + API URL fixes | `f8eb1b6`, dev-stub purge, `ApiConfig.methodUrl` on remotes | +3 |
| Geography real data + cascading | `826d088`, `f81dc1f`, `farmer_create_screen.dart` | +4 |
| Frappe Workflow on Farmer Project | `b86fed8`, 12 sequential stages | +2 |
| Backend workspace repair | `f8eb1b6`, module workspaces + fixtures | +1 |

**What still caps the score below 95:** zero pytest suite, MIMIS/service/profit modules missing, no thermal/WhatsApp billing, thin RBAC on DocTypes, pilot-scale seed data only (2 farmers, 2 projects per June 6 DB audit — must re-verify after seed scripts).

### 1.2 Module Status (9 PRD Modules)

Percentages reflect **shippable end-user capability** (backend + mobile + data), not code volume alone.

| Module | PRD | Current % | Evidence (2026-06-12) | Pilot Target | Prod Target |
|--------|-----|-----------|------------------------|--------------|---------------|
| **M1** Farmer Registry | M1 | **95%** | `farmer.json`, `farmer.py` list/get, `farmer_create_screen.dart`, geography cascading (`geography_remote.dart`, validation fixes `f81dc1f`) | 100% | 100% |
| **M2** Inventory | M2 | **70%** | DocTypes + `inventory.py` (11 whitelisted methods); mobile `inventory_remote.dart` only — **no inventory screen** | 90% | 100% |
| **M3** Dual Billing | M3 | **60%** | ERPNext SI + custom fields (`903e50e`), Cash & Carry POS (`aa01e63`); **no** project-sale mobile, print, WhatsApp | 95% | 100% |
| **M4** MIMIS Sync | M4 | **10%** | `mimis_*` fields on `farmer_project.json`; **no** batch DocType, upload API, or mobile UI | 80% | 95% |
| **M5** 12-Stage Lifecycle | M5 | **90%** | `ProjectLifecycleService`, 12 stages in DB, timeline mobile (`project_timeline_screen.dart`), workflow attach `b86fed8` | 100% | 100% |
| **M6** Task Engine | M6 | **60%** | `project_task.json`, task inbox/detail screens, 13 tasks in demo DB; GPS fields absent; RBAC thin | 90% | 100% |
| **M7** Service / AMC | M7 | **0%** | Listed in `modules.txt`; **no** Service Visit DocType or mobile screen | 70% | 95% |
| **M8** Officer Network | M8 | **30%** | Officer, geography, assignment history DocTypes; **0** assignment rows in June audit; no expense mobile | 80% | 95% |
| **M9** Profit View | M9 | **0%** | `commercial.py` / ops dashboards only — **no** dealer P&L mobile | 70% | 95% |

**Weighted platform completion:** ~**58%** of full PRD intent → ~**72%** after billing + UX sprint (functional spine strong; dealer reports/MIMIS/service weak).

### 1.3 Live Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| **Frappe bench** | 🟢 Operational when started | `dev.agriflow.local`; product audit confirmed Desk HTTP 301 + ops consoles HTTP 200 |
| **MariaDB / Redis** | 🟢 Services active | June 6 audits |
| **ERPNext** | 🟢 Required dependency | `hooks.py`: `required_apps = ["erpnext"]`; billing bootstrap scripts |
| **Mobile Flutter** | 🟢 Builds + runs | v0.24.0; requires `--dart-define=API_BASE_URL=...` |
| **Production hosting** | 🔴 Not deployed | `infra/docker/` exists; Hetzner migration not proven |
| **CI/CD** | 🟡 Partial | `backend/agriflow/.github/workflows/ci.yml` — not full mobile + staging pipeline |

**Connectivity caveat:** Windows Flutter → WSL bench requires correct host IP or Cloudflare tunnel (`docs/CONNECTION_DIAGNOSIS.md`, `docs/LOCAL_LIVE_DEMO.md`).

### 1.4 Strengths to Preserve

1. **12-stage sequential lifecycle** — `backend/agriflow/agriflow/project_lifecycle/services/lifecycle.py`; mobile timeline is hero UX.
2. **Offline-first sync spine** — Drift queue, `sync_orchestrator.dart`, 21 sync sessions in demo DB.
3. **Tamil-first mobile** — ~98% on demo path per `docs/I18N_COVERAGE.md`; ARB pipeline working.
4. **Single-app UX** — Role dashboards (`docs/UNIFIED_APP_EXPERIENCE_REPORT.md`); Frappe Desk = admin only.
5. **Billing foundation** — ERPNext Sales Invoice + Agriflow custom fields + Cash & Carry POS (Week 3.1–3.2).
6. **Ops maturity ahead of dealer features** — observability/pilot/GA consoles (156 whitelisted methods — keep separate from end-user scope).

### 1.5 Critical Gaps to Fix (Honest)

| Gap | Impact | Blocks |
|-----|--------|--------|
| **0 automated backend pytest** | Regression risk on every billing/MIMIS change | Production |
| **MIMIS Excel format unknown** | Reconciliation may need rework | Pilot M4 |
| **DocType RBAC thin** | Farmer/Project create = System Manager only in JSON | Multi-user pilot |
| **No project-sale mobile flow** | Dual billing incomplete | Pilot billing demo |
| **No print / WhatsApp invoice** | Dealer daily ops incomplete | Pilot acceptance |
| **Seed data scale** | 2 farmers / 2 projects — not credible demo | Client pilot |
| **M7/M9 absent** | PRD promise gap | Full pilot checklist |

### 1.6 Recent Commits Trail

```
f8eb1b6 chore: auth bootstrap polish + backend workspace updates
4c04d4d feat(dashboard): role-based home screens for unified one-app experience
6fb3c22 chore(l10n): regenerate localizations for billing POS strings
aa01e63 feat(billing): Phase 3.2 mobile Cash & Carry POS screen
903e50e feat(billing): Week 3 Phase 3.1 - Sales Invoice custom fields + APIs
b86fed8 feat(workflow): attach Frappe Workflow with 12 sequential stages
f81dc1f fix(geography): cascading filters Block by District, Village by Block
7b6bd65 fix(geography): merge TVM into LGD 593, delete orphan blocks
826d088 feat(geography): real TN govt data + cascading UX
21e4dbd docs: complete product standard 360 audit
```

---

## Section 2: Two-Tier Target Definition

### Tier A: Pilot-Ready (4–6 weeks)

| Attribute | Definition |
|-----------|------------|
| **Score target** | **95 / 100** |
| **Timeline** | Weeks 3–7 (remaining billing) + Weeks 8–12 (one client pilot) |
| **Users** | 1 dealer client, ~4–15 users (Owner, Office Manager, Field Staff, Installer) |
| **Acceptable risk** | Known bugs with weekly fix cadence; manual backup; single-site Frappe |
| **Infrastructure** | Staging VPS acceptable; WSL dev bench OK for build; not multi-tenant |

**Exact criteria (all mandatory for Tier A sign-off):**

- All **12/12** end-to-end acceptance tests pass (Section 11)
- M3 billing: Cash & Carry + Project Sale + print OR WhatsApp (print mandatory, WhatsApp optional with fallback)
- M4 MIMIS: sample Excel upload + reconciliation UI (80% — perfect match to real MIMIS format not required if sample validated with client)
- M7 service visits schedulable + completable on mobile (70% — full 3-year AMC automation optional)
- M9 profit dashboard with **realistic seeded numbers** (not live accounting audit)
- Tamil i18n **100%** on all pilot screens (billing, MIMIS, service, profit added)
- Backend tests: **≥50%** coverage on core modules (billing, workflow, geography, farmer, project)
- Seed: 50 farmers, 25 projects, 100 tasks, 50 invoices (Tiruvannamalai context)
- 1 client onboarded with training session documented

### Tier B: Production-Ready (12–16 weeks total)

| Attribute | Definition |
|-----------|------------|
| **Score target** | **98 / 100** |
| **Timeline** | Weeks 13–20 (after pilot iteration) |
| **Users** | Multi-client capable (one Frappe site per customer per architecture) |
| **Acceptable risk** | Zero-downtime deploys, tested DR, security scan clean |

**Exact criteria (Section 11 production block +):**

- Backend test coverage **≥70%**
- Load test: 15 concurrent users, p95 **<2s** on core APIs
- 24h uptime on staging/production VPS
- Backup restore drill successful
- Security: 0 critical findings (SQLi scan, auth review, permission audit, secret rotation)
- CI/CD: GitHub Actions on PR + staging auto-deploy
- Monitoring: GlitchTip/Sentry + uptime + resource alerts
- Documentation: Tamil user manual, admin guide, API doc, DR runbook
- Disaster recovery drill completed

---

## Section 3: Week-by-Week Sprint Plan (Pilot-Ready Path)

**Assumption:** Solo developer (~6–8 focused hours/day) + AI assist; add **25% buffer** for debugging.

---

### Week 3 Remaining (Days 1–3): M3 Billing Completion

**Goal:** Close dual-billing loop for dealer daily operations.

| Phase | Deliverables | Files | Hours | Acceptance Criteria |
|-------|--------------|-------|-------|---------------------|
| **3.3 Project Sale** | Mobile project invoice from Farmer Project at quotation stage | `lib/features/billing/presentation/screens/project_sale_screen.dart`, extend `billing_repository.dart`, route in `app_router.dart`, Owner/Office dashboards link | 10h | From timeline at `quotation_generated`, pre-fill cart, subsidy split matches backend `create_project_invoice`, SI linked to `agriflow_farmer_project` |
| **3.4 Thermal print** | ESC/POS or PDF share | `lib/features/billing/data/print_service.dart`, pubspec: `printing` or `esc_pos_utils` + platform channel | 8h | Cash & Carry receipt prints on Windows test printer OR exports PDF; **Skip-able** for pilot if PDF share accepted |
| **3.5 WhatsApp invoice** | Evolution API integration | `backend/agriflow/agriflow/api/v1/whatsapp.py`, `lib/features/billing/data/whatsapp_service.dart` | 10h | Invoice PDF/link sent to test number; status in `agriflow_whatsapp_status`; **Optional** — manual share fallback documented |
| **3.6 E2E billing test** | Scripted verification | `backend/agriflow/agriflow/install/test_billing_e2e.py`, `mobile/agriflow_mobile/integration_test/billing_flow_test.dart` | 6h | Cash & Carry + Project Sale + list_recent in one script; mobile integration test green |
| **3.7 Print formats** | English + Tamil SI print | `backend/agriflow/agriflow/print_formats/` or ERPNext Print Format JSON fixtures | 6h | Tamil labels on receipt; subsidy line visible |

**Dependencies:** Week 3.1–3.2 complete (`903e50e`, `aa01e63`).  
**Risks:** Bluetooth printer fragmentation → **mitigation:** PDF-first, printer as stretch. Evolution API downtime → **mitigation:** manual WhatsApp share button.

**Week 3 total:** ~40h (3 focused days + buffer)

---

### Week 4 (Days 4–8): M4 MIMIS Module

**Goal:** Excel upload → reconcile → stage update with audit trail.

| Deliverable | Files | Hours | Acceptance |
|-------------|-------|-------|------------|
| MIMIS Import Batch DocType | `backend/.../mimis_sync/doctype/mimis_import_batch/` | 8h | Batch stores file hash, row count, status |
| Upload + parse API | `backend/.../api/v1/mimis.py` | 10h | `upload_excel` whitelisted; validates columns against sample template |
| Reconciliation engine | `backend/.../mimis_sync/services/reconcile.py` | 12h | Matches farmer/project by ID; flags conflicts |
| Mobile upload UI | `lib/features/mimis/presentation/mimis_upload_screen.dart` | 10h | Pick file → upload → progress → summary |
| Conflict resolution | `lib/features/mimis/presentation/mimis_conflict_sheet.dart` | 8h | User resolves stale rows; audit log written |
| Stage sync hook | `lifecycle.py` or MIMIS service | 4h | Approved rows advance `mimis_registered` where valid |

**Dependencies:** Sample Excel template agreed with client (**risk: format unknown** — Day 1 spike: obtain real MIMIS export or build synthetic template in `packages/excel_templates/`).  
**Skip-able:** Auto stage advance (manual approve only for pilot).  
**Risk mitigation:** Ship with **synthetic sample** first; adapter layer for column mapping.

**Week 4 total:** ~52h (~5 days)

---

### Week 5 (Days 9–13): M7 Service/AMC + M8 Officer

**Goal:** Field service loop + officer economics (safe labels).

| Deliverable | Files | Hours | Acceptance |
|-------------|-------|-------|------------|
| Service Visit DocType | `backend/.../service/doctype/service_visit/` | 8h | Linked to Farmer Project; status workflow |
| AMC schedule (3-year) | `backend/.../service/services/amc_scheduler.py` | 10h | Generates visit tasks from install date; **Skip-able:** manual visits only for pilot |
| Service mobile screen | `lib/features/service/presentation/service_visit_screen.dart` | 10h | List due visits → complete with notes |
| Expense Entry DocType + API | `backend/.../officer_network/doctype/expense_entry/` | 8h | Officer submits expense linked to block |
| Expense mobile | `lib/features/officer/presentation/expense_entry_screen.dart` | 8h | Create expense offline → sync |
| Commission tracking (safe labels) | `backend/.../api/v1/officer.py`, dashboard widgets | 8h | "Performance incentive" labels — no gambling terminology |
| Assignment history seed | `scripts/seed_officer_assignments.py` | 4h | ≥1 assignment per demo officer |

**Dependencies:** M5 projects exist for linking.  
**Risks:** AMC complexity → **mitigation:** pilot with manual service visits only (AMC auto = optional).

**Week 5 total:** ~56h (~5 days)

---

### Week 6 (Days 14–18): M9 Profit + Backend Tests

**Goal:** Owner sees P&L; regression safety net.

| Deliverable | Files | Hours | Acceptance |
|-------------|-------|-------|------------|
| Profit API | `backend/.../api/v1/profit.py` | 10h | Per-project revenue, subsidy split, material cost estimate |
| Profit mobile dashboard | `lib/features/profit/presentation/profit_dashboard_screen.dart` | 10h | Charts: revenue split, stock turnover summary |
| Stock turnover report | `profit.py` + Owner dashboard link | 6h | Matches seeded inventory movements |
| **Backend tests** | | | |
| `test_billing.py` | `backend/agriflow/agriflow/tests/test_billing.py` | 6h | Covers 5 billing methods |
| `test_workflow.py` | `tests/test_workflow.py` | 4h | Sequential transition + skip blocked |
| `test_geography.py` | `tests/test_geography.py` | 4h | Cascading validation |
| `test_farmer.py` | `tests/test_farmer.py` | 4h | list/get/create guards |
| `test_project.py` | `tests/test_project.py` | 6h | timeline + transition |
| Coverage gate | `pytest.ini`, CI step | 4h | **≥50%** on `agriflow/` package |

**Dependencies:** Billing + seed data.  
**Risk:** pytest + Frappe test setup learning curve → **mitigation:** start with `test_billing.py` cloning `install/test_billing_api.py`.

**Week 6 total:** ~54h (~5 days)

---

### Week 7 (Days 19–22): Demo Prep + Polish

**Goal:** Credible Tiruvannamalai demo + final audit.

| Deliverable | Files | Hours | Acceptance |
|-------------|-------|-------|------------|
| Realistic seed | `scripts/seed_pilot_demo.py` | 12h | 50 farmers, 25 projects (all stages), 100 tasks, 50 invoices |
| Tamil i18n final pass | `app_ta.arb`, new feature strings | 8h | 100% on billing, MIMIS, service, profit, role dashboards |
| Performance | sync batch tuning, lazy lists | 6h | Farmer list <1s with 50 rows on mid Android |
| Demo script | `docs/PILOT_DEMO_SCRIPT.md` | 4h | 15-min Owner + Field Staff walkthrough |
| Video recording | External | 2h | Screen capture of 12/12 checklist |
| Final 360° audit | `docs/PILOT_READY_AUDIT.md` | 4h | Score ≥95 documented |

**Dependencies:** Weeks 3–6 complete.  
**Week 7 total:** ~36h (~4 days)

---

## Section 4: Pilot Phase (Weeks 8–12)

| Week | Focus | Activities | Hours/wk |
|------|-------|------------|----------|
| 8 | Client onboarding | Site config, 4 users, block permissions, device install | 20h |
| 9 | Training | Owner 2h, Office 2h, Field 2h, Installer 1h — Tamil materials | 12h |
| 10 | Daily monitoring | Error log review, sync failures, WhatsApp/print issues | 15h |
| 11 | Weekly fixes | P0 bugs within 48h; P1 within 1 week | 20h |
| 12 | Feature iteration | Top 3 client requests scoped; backup drill #1 | 20h |

**Production data backup strategy (pilot):**

- Daily: `infra/scripts/backup_daily.sh` → encrypted offsite (MinIO or Hetzner Storage Box)
- Weekly: restore test on staging bench
- Mobile: Drift DB is device-local — document that server is SoT

**Skip-able during pilot:** Multi-site tenancy, auto-scaling, full AMC automation.

---

## Section 5: Production Hardening (Weeks 13–20)

| Week | Theme | Key deliverables |
|------|-------|------------------|
| 13–14 | Testing | Coverage 50% → 70%; load test script (`scripts/phase24_benchmark.py` extend) |
| 15 | Security | Bandit/Semgrep, permission audit (`phase16_permission_audit.py`), JWT review, rotate dev secrets |
| 16 | Hosting migration | Hetzner CX31 (4GB), `infra/docker/docker-compose.prod.yml`, SSL Let's Encrypt, domain |
| 17 | Monitoring | GlitchTip self-host or Sentry, Uptime Kuma, MariaDB disk alerts |
| 18 | CI/CD | GitHub Actions: pytest + `flutter analyze` + staging deploy on merge to `stabilization-v1` |
| 19 | Documentation | Tamil user manual PDF, admin guide, OpenAPI export from `API_CONTRACTS.md`, DR runbook |
| 20 | DR drill + sign-off | Full restore, 24h uptime test, production readiness audit ≥98 |

**Mandatory for production:** all Tier B criteria (Section 11).  
**Skip-able:** Evolution API self-host (use Meta Cloud API if stable), thermal printer native drivers (PDF sufficient).

---

## Section 6: Risk Register

| Risk | Likelihood | Impact | Mitigation | Contingency |
|------|------------|--------|------------|-------------|
| Backend test gap (0 pytest today) | **High** | **High** | Week 6 dedicated; clone billing smoke tests | Freeze features; manual regression checklist |
| MIMIS Excel format unknown | **High** | **High** | Column-mapping adapter; client sample by Week 4 Day 1 | Manual CSV entry UI; defer auto-reconcile |
| Evolution API instability | Medium | Medium | Queue + retry; status field on SI | Manual WhatsApp share from PDF |
| Bluetooth printer compatibility | Medium | Low | PDF/share first | Email invoice link |
| Rural internet reliability | **High** | **High** | Offline-first already built; queue UX | Train "sync before leave office" SOP |
| Power outages (field) | Medium | Medium | Drift persistence; battery optimization doc exists | Solar power bank recommendation in training |
| Android device fragmentation | Medium | Medium | Test on 3 devices (low/mid/high Android) | Responsive layouts (already started in dashboards) |
| Data growth (5K+ farmers) | Low (pilot) | **High** (prod) | Pagination, indexes (`phase24_indexes.py`), sync deltas | Archive old timeline events |
| Solo developer bandwidth | **High** | **High** | Strict skip-able list; 25% time buffer | Defer M9 charts to post-pilot |
| ERPNext upgrade breakage | Low | **High** | Pin ERPNext v15; test migrate on staging | Snapshot bench before upgrade |
| DocType RBAC gaps | **High** | **High** | Week 5 permission fixtures for 8 Agriflow roles | API-level block checks (already in `permissions.py`) |

---

## Section 7: Cost Estimate

### One-time

| Item | Cost (INR) | Notes |
|------|------------|-------|
| Domain (.in or .com) | ₹500–1,500 / year | e.g. `agriflow.in` |
| SSL | ₹0 | Let's Encrypt |
| Cloud server initial setup labor | ~₹2,000 | 4–8h VPS hardening (self or contractor) |
| Thermal printer (optional) | ₹3,000–8,000 | 58mm ESC/POS Bluetooth |

### Monthly recurring

| Item | Cost (INR/month) | Notes |
|------|------------------|-------|
| Hetzner CX31 / DO 4GB | ₹2,000–3,000 | ~€4–6 + MariaDB on same VM |
| Backup storage (100GB) | ₹500 | Hetzner Storage Box or S3-compatible |
| Transactional email | ₹500 | Resend/SMTP for alerts |
| Evolution API hosting | ₹1,000 | Self-host on same VPS or dedicated |
| Domain (amortized) | ~₹125 | |
| **Total** | **~₹4,125–5,125** | |

### Client billing perspective

- 1 client × 15 users × ₹5,000/month = **₹75,000/month** — covers infra with large margin
- Pilot phase may be discounted; infra still <7% of revenue at target pricing

*Prices approximate for India market Q2 2026; verify Hetzner EUR/INR at purchase.*

---

## Section 8: Module Implementation Matrix

| Module | Current % | Pilot Target | Production Target | Effort to Pilot | Effort to Prod |
|--------|-----------|--------------|-------------------|-----------------|----------------|
| M1 Farmer | 95% | 100% | 100% | 4 hours | 1 day |
| M2 Inventory | 70% | 90% | 100% | 2 days | 4 days |
| M3 Billing | 60% | 95% | 100% | 3 days | 1 week |
| M4 MIMIS | 10% | 80% | 95% | 5 days | 2 weeks |
| M5 Lifecycle | 90% | 100% | 100% | 4 hours | 2 days |
| M6 Tasks | 60% | 90% | 100% | 2 days | 1 week |
| M7 Service | 0% | 70% | 95% | 3 days | 2 weeks |
| M8 Officer | 30% | 80% | 95% | 3 days | 1 week |
| M9 Profit | 0% | 70% | 95% | 3 days | 2 weeks |

*Current % updated from June 6 product audit + Week 3 billing/UX commits.*

---

## Section 9: Decision Framework — Pilot vs Production First?

### Inputs

| Factor | Your situation |
|--------|----------------|
| Client urgency | Low — flexible timeline |
| Budget | 1 client, sustainable build |
| Risk tolerance | Real client = real bugs acceptable with fix cadence |
| Resources | Solo developer + AI (Windsurf/Cursor) |

### Recommendation: **Pilot-Ready first, then iterate to Production**

**Reasoning:**

1. **Code vs operations gap:** Architecture score was 8/10 in product audit, but test coverage 3/10 and deployment 6/10. Shipping to production now guarantees firefighting without regression tests.

2. **Billing is mid-flight:** Cash & Carry works; project sale + print + WhatsApp are the revenue path dealers expect. Production without them fails the "dual billing" PRD promise.

3. **MIMIS is highest unknown:** Real Excel format must be validated with one client before hardening multi-tenant ops. Pilot discovers this cheaply.

4. **Unified app UX is solved:** Role dashboards remove the "two apps" confusion — perfect for pilot demo, not yet for 15 concurrent users under load.

5. **Cost is low:** ~₹5K/month infra during pilot; production hardening (Weeks 13–20) coincides with paid client revenue.

**Do not skip pilot** unless client demands go-live with signed waiver on MIMIS, service, and profit gaps.

---

## Section 10: Daily Standup Template

```markdown
## YYYY-MM-DD

### Yesterday
**Completed:**
- [ ]

**Blocked:**
- [ ]

### Today
**Goal:** [specific deliverable]
**Phase:** Week X.Y — [name]
**Effort estimate:** [X hours]

### Tomorrow
**Plan:** [specific]

### Risks / Issues
- [ ]

### Maturity Score Update
| Metric | Value |
|--------|-------|
| Yesterday | __/100 |
| Today (target) | __/100 |
| This week target | __/100 |
```

---

## Section 11: Final Acceptance Criteria

### Pilot-Ready (Week 7 milestone) — 12/12 must pass

| # | Test | Pass criteria |
|---|------|---------------|
| 1 | Field Staff registers farmer | Cascading District→Block→Village; saved in DB |
| 2 | Office Manager advances 12 stages | Sequential only; timeline events emitted |
| 3 | Cash & Carry sale | Search, cart, save SI via mobile |
| 4 | Project sale invoice | Subsidy split; linked to Farmer Project |
| 5 | MIMIS Excel upload | Sample file processes; conflicts surfaced |
| 6 | Service visit | Scheduled + completed on mobile |
| 7 | Profit dashboard | Non-zero realistic totals from seed |
| 8 | WhatsApp invoice | Sent OR documented manual fallback used |
| 9 | Thermal receipt | Printed OR PDF shared |
| 10 | Officer commission | Tracked with safe labels |
| 11 | Offline → online sync | Queue drains without data loss |
| 12 | Tamil UI | 100% on all pilot screens |

**If 12/12 pass → Pilot-Ready ✅**

### Production-Ready (additional)

- ≥70% backend pytest coverage
- Load: 15 users, p95 <2s
- 24h uptime on production VPS
- Backup restore tested
- Security scan: 0 critical
- 4 manuals complete
- User training ≥1 hour documented
- DR drill successful

---

## Section 12: Next Immediate Action (Next 3 Days)

### Day 1 — Phase 3.3: Project Sale Flow

**Goal:** Mobile project invoice from Farmer Project at quotation stage.

**Create / modify:**

```
mobile/agriflow_mobile/lib/features/billing/presentation/screens/project_sale_screen.dart
mobile/agriflow_mobile/lib/features/billing/data/billing_repository.dart  # add createProjectInvoice()
mobile/agriflow_mobile/lib/features/billing/presentation/providers/billing_providers.dart
mobile/agriflow_mobile/lib/app/router/routes.dart  # AppRoutes.projectSale(projectName)
mobile/agriflow_mobile/lib/app/router/app_router.dart
mobile/agriflow_mobile/lib/features/project_lifecycle/presentation/widgets/timeline_workflow_actions.dart  # "Create invoice" at quotation_generated
mobile/agriflow_mobile/lib/l10n/app_en.arb + app_ta.arb
```

**Test scenarios:**

1. Open project FP-* at `quotation_generated` → launch project sale
2. Add drip kit items → verify subsidy + farmer portion preview
3. Submit → `create_project_invoice` returns SI name
4. `list_recent_invoices` shows project-linked SI with `agriflow_sale_mode = Project Sale`

**Acceptance:** SI total matches backend test from `test_billing_api.py` (subsidy ₹6000 + farmer ₹2500 pattern).

---

### Day 2 — Phase 3.4–3.5: Print + WhatsApp

**Print (mandatory path: PDF):**

- Add `lib/features/billing/data/print_service.dart`
- After invoice success → "Share receipt" → PDF with Tamil labels

**WhatsApp (optional stretch):**

- Backend stub: `agriflow.api.v1.billing.send_whatsapp` posting to Evolution API
- Mobile: button on success dialog
- **Fallback:** copy invoice link to clipboard

---

### Day 3 — Phase 3.6–3.7: E2E + Print Formats

- Extend `backend/agriflow/agriflow/install/test_billing_e2e.py` (cash + project + mobile API simulation)
- ERPNext Print Format fixtures: English + Tamil receipt
- Sign-off: update `docs/WEEK3_PHASE_3_BILLING_COMPLETE_REPORT.md`
- **Maturity bump:** 89 → ~92/100

**Then:** Begin Week 4 (MIMIS) — first action: obtain real MIMIS Excel sample from client or Tamil Nadu portal documentation.

---

## Appendix A: Key File Index

| Area | Path |
|------|------|
| Mobile entry | `mobile/agriflow_mobile/lib/main.dart` → `app/bootstrap.dart` |
| Auth + roles | `lib/features/auth/`, `lib/core/auth/user_role_provider.dart` |
| Billing API | `backend/agriflow/agriflow/api/v1/billing.py` |
| Lifecycle | `backend/agriflow/agriflow/project_lifecycle/services/lifecycle.py` |
| Sync | `mobile/.../core/sync/sync_orchestrator.dart` |
| Infra | `infra/docker/docker-compose.prod.yml` |
| Audits | `docs/PRODUCT_STANDARD_360_AUDIT.md`, `docs/CURRENT_STATE_360_AUDIT.md` |

---

## Appendix B: Document History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-12 | Initial production readiness roadmap |

---

*This roadmap is the definitive planning document for AgriFlow OS pilot and production phases. Update maturity scores at the end of each week using the standup template.*
