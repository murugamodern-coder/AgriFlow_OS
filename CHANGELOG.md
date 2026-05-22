# Changelog

All notable implementation milestones for AgriFlow OS. Entries are derived from phase verification reports and committed artifacts in this repository — not from external release tags.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added

- GitHub presentation polish: concise root README, screenshot directory scaffold, this changelog.

---

## Phase 24 — Performance & Observability

Verified on bench site `dev.agriflow.local` (see [PHASE24_PERFORMANCE_OBSERVABILITY_REPORT.md](./PHASE24_PERFORMANCE_OBSERVABILITY_REPORT.md)).

### Added

- `observability.ops_metrics_dashboard` API and `/observability_console` admin UI.
- Performance indexes, telemetry daily rollup, batched retention jobs.
- Mobile `AdaptiveSyncPolicy` — network-aware sync intervals and retry delays.
- Heartbeat throttling and idle pull skipping to reduce mobile network use.

### Changed

- Cached SLA/ops dashboard bundles to lower repeated query cost.

---

## Phase 23 — Enterprise Operations

See [PHASE23_ENTERPRISE_OPERATIONS_REPORT.md](./PHASE23_ENTERPRISE_OPERATIONS_REPORT.md).

### Added

- **Tenant Ops Record** DocType and `/enterprise_ops_console`.
- Tenant-scoped SLA dashboard API, scheduler health dashboard.
- Enterprise audit export and automated daily retention/archival jobs.
- [docs/ENTERPRISE_TENANT_GOVERNANCE.md](./docs/ENTERPRISE_TENANT_GOVERNANCE.md) — one Frappe site per customer model.

---

## Phase 22 — GA Readiness

See [PHASE22_GA_READINESS_REPORT.md](./PHASE22_GA_READINESS_REPORT.md).

### Added

- `/ga_ops_console`, release governance DocTypes, support ticket workflows.
- GA escalation and backup verification install hooks.

---

## Phase 21 — Pilot Operations

See [PHASE21_PILOT_OPERATIONS_REPORT.md](./PHASE21_PILOT_OPERATIONS_REPORT.md).

### Added

- `/pilot_ops_dashboard` with search and status filtering.
- Pilot analytics APIs, operational feedback DocTypes, mobile pilot ops screens.

---

## Phase 20 — Commercial Readiness

See [PHASE20_COMMERCIAL_READINESS_REPORT.md](./PHASE20_COMMERCIAL_READINESS_REPORT.md).

### Added

- Customer onboarding DocTypes and commercial ops console scaffolding.
- Commercial verification and demo customer seed scripts.

---

## Phase 19 — Production Rollout

See [PHASE19_PRODUCTION_ROLLOUT_REPORT.md](./PHASE19_PRODUCTION_ROLLOUT_REPORT.md).

### Added

- Production rollout verification, backup drill scripts, ops alert hooks.
- Push delivery API extensions for rollout monitoring.

---

## Phase 18 — Production Readiness

See [PHASE18_PRODUCTION_READINESS_REPORT.md](./PHASE18_PRODUCTION_READINESS_REPORT.md).

### Added

- Production readiness API, permission audit, offline survivability checks.
- Device push token DocType and push delivery log foundation.

---

## Phase 17 — Pilot Deployment

See [PHASE17_PILOT_DEPLOYMENT_REPORT.md](./PHASE17_PILOT_DEPLOYMENT_REPORT.md).

### Added

- Pilot bootstrap fixtures, operational log DocTypes, pilot simulation scripts.
- Staging deployment workflow documented in [docs/STAGING_DEPLOYMENT_WORKFLOW.md](./docs/STAGING_DEPLOYMENT_WORKFLOW.md).

---

## Phase 16 — Hardening

See [PHASE16_HARDENING_REPORT.md](./PHASE16_HARDENING_REPORT.md).

### Added

- JWT auth hardening, request context middleware, permission audit passes.
- Inventory reconcile hooks and security-oriented install verification.

---

## Phase 15 — End-to-End Validation

See [PHASE15_E2E_VALIDATION_REPORT.md](./PHASE15_E2E_VALIDATION_REPORT.md).

### Added

- Demo seed (`phase15_seed_demo`) and E2E verification script.
- Documented demo login path for field officer walkthrough.

---

## Phase 14 — Mobile Product

See [PHASE14_MOBILE_REPORT.md](./PHASE14_MOBILE_REPORT.md).

### Added

- Feature-first Flutter modules: timeline, tasks, notifications, sync status UI.
- Tamil + English localization via ARB; design tokens from [UI_TOKENS.md](./UI_TOKENS.md).

---

## Phase 13 — Inventory

See [PHASE13_INVENTORY_REPORT.md](./PHASE13_INVENTORY_REPORT.md).

### Added

- Inventory Item, Warehouse, Stock Ledger Entry, Project Material Allocation DocTypes.
- Reserve / consume / transfer flows with immutable ledger and idempotent `client_id` replay.

---

## Phase 12 — Notification Engine

See [PHASE12_NOTIFICATION_REPORT.md](./PHASE12_NOTIFICATION_REPORT.md).

### Added

- Notification DocTypes, timeline fanout, unread count and mark-read APIs.
- Mobile notification inbox and delivery log immutability checks.

---

## Phase 11 — Offline Sync Engine

See [PHASE11_SYNC_REPORT.md](./PHASE11_SYNC_REPORT.md).

### Added

- `sync.push` / `sync.pull` with keyset cursors and server watermarks.
- Sync mutation log, idempotent replay, partial batch (HTTP 207) handling.
- Mobile SyncQueue, orchestrator, conflict surfaces, push result applier.

---

## Earlier foundation (Phases 6–10)

Documented in [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) and bench verification scripts under `scripts/phase6_*` through `scripts/phase10_*`.

### Added

- Frappe app shell, geography masters, farmer registry.
- **Farmer Project** aggregate root and 12-stage lifecycle service.
- Timeline engine and task engine with lifecycle-linked templates.

---

## Documentation & specifications

### Added

- Root specifications: [PRD.md](./PRD.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [DOCTYPES.md](./DOCTYPES.md), [API_CONTRACTS.md](./API_CONTRACTS.md).
- Operational runbooks under [docs/](./docs/) — backup/restore, pilot support SOP, rollout governance, production checklists.
- [infra/docker/](./infra/docker/) compose stacks for dev, staging, and production-shaped local environments.
