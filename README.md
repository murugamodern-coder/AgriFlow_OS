# 🌾 AgriFlow OS

Enterprise-grade offline-first agricultural field operations platform built with **Frappe + Flutter**.

AgriFlow OS manages:

- farmer project lifecycles
- field operations
- task execution
- offline mobile workflows
- inventory operations
- telemetry & observability
- operational governance
- multi-tenant enterprise rollout workflows

---

## ✨ Core Capabilities

| Area | What ships today |
|------|------------------|
| **Project lifecycle** | 12-stage sequential workflow per farmer subsidy project; server-authoritative stage transitions |
| **Timeline UX** | Vertical stage timeline as the primary operational screen |
| **Task engine** | Follow-up tasks generated from lifecycle events; inbox and detail flows |
| **Offline sync** | Drift `SyncQueue`, `sync.push` / `sync.pull`, idempotent replay, partial-batch handling |
| **Conflict handling** | Structured server conflicts (`stale_transition`, LWW mismatches) with mobile resolution UI |
| **Notification engine** | In-app inbox, unread counts, timeline fanout, delivery logging |
| **Inventory ledger** | Warehouses, reservations, consumption, immutable stock ledger |
| **Tamil localization** | English + Tamil ARB strings; Tamil-first operational copy |
| **Background sync** | WorkManager / headless sync runner for queued flush when online |
| **Adaptive sync** | Network-aware intervals and retry delays to reduce battery and data use |
| **Telemetry** | Client sync diagnostics and pilot telemetry hooks; server observability rollup |
| **Push foundation** | Device push token registration and delivery log scaffolding |
| **Operational consoles** | Web dashboards for pilot, GA, enterprise, and observability ops |
| **Pilot rollout** | Pilot feedback, onboarding flows, and ops dashboards |
| **Enterprise governance** | Per-site tenant ops records, SLA dashboards, audit export (one Frappe site per customer) |
| **Production readiness** | Staging/prod Docker compose, deployment scripts, runbooks in `docs/` |

Full product and engineering specs: [PRD.md](./PRD.md) · [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Flutter Mobile (agriflow_mobile)                       │
│  Riverpod · go_router · Drift · Hive · Dio              │
│  SyncQueue · adaptive sync · Tamil i18n                 │
└──────────────────────────┬──────────────────────────────┘
                           │ REST (JWT) · sync.push/pull
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Frappe Backend (backend/agriflow)                      │
│  DocTypes · services · v1 APIs · background jobs        │
│  lifecycle · tasks · sync · notifications · inventory │
└──────────────────────────┬──────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      MariaDB 11      Redis 7         MinIO (S3)
      (primary)    (cache/queues)   (file storage)
```

Deployment targets: Docker on VPS (see [infra/docker/](./infra/docker/)), TLS via nginx/Caddy patterns documented in ops guides.

---

## 📱 Mobile Capabilities

Implemented under `mobile/agriflow_mobile/`:

| Capability | Implementation |
|------------|----------------|
| **Offline queue** | Drift `SyncQueue`; writes enqueue before network flush |
| **Sync engine** | `SyncOrchestrator` — ordered push then pull |
| **Conflict handling** | `conflict_sheet` + server conflict payloads |
| **Telemetry** | `telemetry.dart`, sync diagnostics, optional Sentry bootstrap |
| **Adaptive sync** | `AdaptiveSyncPolicy` — idle interval by connectivity |
| **Background sync** | `background_sync_coordinator`, WorkManager registration |
| **Push foundation** | `push_service` + backend `device_push_token` DocType |

Feature modules: auth, farmer registry, project timeline, tasks, notifications, inventory, sync status, pilot ops, commercial readiness.

---

## 🚀 Quick Start

Detailed walkthrough: [docs/SETUP_FROM_SCRATCH.md](./docs/SETUP_FROM_SCRATCH.md)

**Backend (WSL bench)**

```bash
./scripts/install_backend_to_bench.sh
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench start
```

**Mobile**

```powershell
cd mobile\agriflow_mobile
flutter pub get
flutter gen-l10n
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000 --dart-define=DEMO_MODE=true
```

Demo credentials and tunnel setup: [docs/LOCAL_LIVE_DEMO.md](./docs/LOCAL_LIVE_DEMO.md)

---

## 📂 Repository Structure

```
AgriFlow_OS/
├── backend/agriflow/       # Frappe custom app (committed snapshot)
├── mobile/agriflow_mobile/ # Flutter field operations app
├── docs/                   # Runbooks, checklists, deployment guides
├── infra/                  # Docker compose, nginx, VPS scripts
├── scripts/                # Phase bootstraps, deploy helpers, verification
├── PRD.md                  # Product requirements
├── ARCHITECTURE.md         # System design
├── DOCTYPES.md             # Data model specification
├── API_CONTRACTS.md        # REST v1 contracts
├── IMPLEMENTATION_PLAN.md  # Phased delivery roadmap
└── PHASE*_REPORT.md        # Phase verification reports
```

---

## 📊 Operational Consoles

Static HTML consoles served from the Frappe site (deploy via `scripts/phase*_deploy*.sh`):

| Console | Path |
|---------|------|
| Observability | `/observability_console` |
| Pilot operations | `/pilot_ops_dashboard` |
| GA operations | `/ga_ops_console` |
| Enterprise operations | `/enterprise_ops_console` |

See [docs/PRODUCTION_OPERATIONS_CHECKLIST.md](./docs/PRODUCTION_OPERATIONS_CHECKLIST.md) for daily ops references.

---

## 📸 Screenshots

> Screenshots and demo GIFs will be added after pilot dress rehearsal validation.

Placeholder directory: [docs/screenshots/](./docs/screenshots/)

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [docs/](./docs/) | Operational runbooks, checklists, staging workflow |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Sync, RBAC, deployment topology |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | REST v1 endpoints and offline protocol |
| [DOCTYPES.md](./DOCTYPES.md) | Frappe DocType specification |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Phased build order and completion criteria |
| [UI_TOKENS.md](./UI_TOKENS.md) | Design system tokens |
| [docs/ENTERPRISE_TENANT_GOVERNANCE.md](./docs/ENTERPRISE_TENANT_GOVERNANCE.md) | Multi-site tenant model |
| [CHANGELOG.md](./CHANGELOG.md) | Implementation milestones |

Phase verification reports (`PHASE11`–`PHASE24`) document bench-verified delivery at the repository root.

---

## 🛣️ Roadmap

| Maturity area | Status |
|---------------|--------|
| **Core operations** | Farmer registry, 12-stage lifecycle, timeline engine, task engine |
| **Offline-first sync** | Push/pull, replay, conflict surfaces, mobile queue (Phase 11+) |
| **Operational modules** | Notifications, inventory ledger, E2E field validation |
| **Mobile product** | Role-based shell, Tamil i18n, sync status UX |
| **Pilot operations** | Pilot dashboards, feedback, rehearsal checklists |
| **Production deployment** | Docker staging/prod, backup/restore, rollout governance |
| **Commercial readiness** | Customer onboarding artifacts, GA sign-off workflows |
| **Enterprise operations** | Tenant ops records, SLA dashboards, audit export |
| **Observability** | Ops metrics dashboard, adaptive sync, performance indexes |

Remaining work is tracked in phase reports and [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) — not every PRD Phase 1 item is closed (e.g. full MIMIS Excel reconciliation UI, expense/profit dashboards).

---

## ⚠️ Current Scope

**In scope:** Subsidy dealer field operations for Tiruvannamalai pilot geography; offline-capable mobile; audit-friendly lifecycle; inventory across two godowns; operational consoles and runbooks.

**Explicitly out of scope (Phase 1 / this repo):**

- AI features
- OCR
- GIS / maps
- ERP integrations
- Advanced analytics / ML
- Recreation of government MIMIS portals or live government APIs
- Multi-tenant SaaS on a single shared database

---

## 📄 License

Private commercial implementation — demonstration repository.

License and distribution terms to be confirmed by the operating entity.
