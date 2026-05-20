# AgriFlow OS — System Architecture

**Version:** 1.0  
**Status:** Active Development  
**Last updated:** 2026-05-20 (Future Expansion §21 added)  

**Related documents:** [PRD.md](./PRD.md) · [DOCTYPES.md](./DOCTYPES.md) · [UI_TOKENS.md](./UI_TOKENS.md) · [.cursorrules](./.cursorrules)

---

## Document purpose

This document defines the production architecture for AgriFlow OS: a workflow-first, offline-first agriculture operations platform for irrigation subsidy dealers. It is the authoritative reference for engineering decisions, module boundaries, sync behavior, and cross-cutting concerns.

**AgriFlow OS is not a billing application.** It is an operational memory system: everything important must be tracked, visible, actionable, and auditable.

---

## Executive summary

| Dimension | Decision |
|-----------|----------|
| **North-star entity** | Farmer Project (12-stage sequential lifecycle) |
| **Backend** | Frappe Framework v15, MariaDB 11, Redis 7 |
| **Mobile** | Flutter 3.24, Riverpod, Hive + Drift, go_router |
| **Sync model** | Outbox (SyncQueue) for writes; local cache for reads; Excel-only MIMIS reconciliation |
| **Geography** | District → Block → Cluster → Officer → Village → Farmer |
| **UI** | Timeline-first, Tamil-first, design-token driven |
| **Deployment** | Docker on Hetzner via Coolify; MinIO for files; daily backups |
| **Future expansion** | Placeholders only (§21); Phase 1 unchanged |

---

## Table of contents

1. [Monorepo structure](#1-monorepo-structure)
2. [Frappe backend architecture](#2-frappe-backend-architecture)
3. [Flutter feature-first architecture](#3-flutter-feature-first-architecture)
4. [Sync engine architecture](#4-sync-engine-architecture)
5. [API standards](#5-api-standards)
6. [Repository pattern](#6-repository-pattern)
7. [Riverpod state architecture](#7-riverpod-state-architecture)
8. [Offline-first flow](#8-offline-first-flow)
9. [Database strategy](#9-database-strategy)
10. [File upload strategy](#10-file-upload-strategy)
11. [Queue and job architecture](#11-queue-and-job-architecture)
12. [Role-based access architecture](#12-role-based-access-architecture)
13. [MIMIS reconciliation architecture](#13-mimis-reconciliation-architecture)
14. [Naming conventions](#14-naming-conventions)
15. [Error handling strategy](#15-error-handling-strategy)
16. [Logging and audit strategy](#16-logging-and-audit-strategy)
17. [Deployment topology](#17-deployment-topology)
18. [Security practices](#18-security-practices)
19. [Scalability considerations](#19-scalability-considerations)
20. [Architectural invariants](#20-architectural-invariants)
21. [Future Expansion Architecture](#21-future-expansion-architecture)

---

## 1. Monorepo structure

The repository is organized as a **single monorepo** with clear ownership boundaries between backend, mobile, infrastructure, and shared documentation.

```
agriflow-os/
├── apps/
│   └── agriflow/                      # Frappe custom application (single app)
│       ├── agriflow/                  # Python package
│       │   ├── api/                   # Versioned REST entry points
│       │   ├── modules/               # Frappe modules (M1–M9 mapping)
│       │   ├── services/              # Domain services (lifecycle, tasks, MIMIS)
│       │   ├── hooks.py
│       │   └── patches/               # Data migrations
│       ├── agriflow/                  # DocType definitions per module
│       └── fixtures/                  # Roles, workflows, master data exports
│
├── mobile/
│   └── agriflow_mobile/               # Flutter application
│       ├── lib/
│       ├── assets/
│       │   ├── i18n/                  # en, ta (Tamil-first support)
│       │   └── fonts/
│       └── test/
│
├── packages/                          # Optional shared artifacts (Phase 2+)
│   ├── api_contract/                  # OpenAPI / schema definitions
│   └── excel_templates/               # MIMIS and reconciliation templates
│
├── infra/
│   ├── docker/                        # Compose, images, bench config
│   ├── frappe/                        # site_config templates, nginx snippets
│   └── coolify/                       # Deployment manifests
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md                # This document
│   ├── DOCTYPES.md
│   └── UI_TOKENS.md
│
├── scripts/
│   ├── seed/                          # Bench seed scripts
│   └── excel_reconcile/               # Server-side validation helpers
│
└── .cursorrules
```

### Ownership rules

| Path | Owner | Change frequency |
|------|-------|------------------|
| `apps/agriflow/` | Backend team | High during feature work |
| `mobile/agriflow_mobile/` | Mobile team | High |
| `docs/` | Product + engineering | Medium; PR-reviewed |
| `infra/` | DevOps | Low; environment-specific secrets outside repo |
| `fixtures/` | Backend | Versioned with releases |

### Principles

- **One Frappe app** (`agriflow`) with internal modules aligned to PRD modules M1–M9—not multiple Frappe apps.
- **Feature-first Flutter** under `lib/features/{feature}/`; shared code only in `core/` and `shared/`.
- **Documentation as code**: DocType and API changes must update `DOCTYPES.md` in the same change cycle.
- **No secrets in repo**: environment variables and Coolify secrets for production credentials.

---

## 2. Frappe backend architecture

### 2.1 Layered model

```
┌──────────────────────────────────────────────────────────────────┐
│  API Layer          Whitelisted methods + filtered REST CRUD      │
├──────────────────────────────────────────────────────────────────┤
│  Controllers        Request validation, RBAC, response shaping    │
├──────────────────────────────────────────────────────────────────┤
│  Domain Services    Stage transitions, task generation, MIMIS     │
├──────────────────────────────────────────────────────────────────┤
│  DocType Layer      Models, child tables, hooks (validate/update) │
├──────────────────────────────────────────────────────────────────┤
│  Persistence        MariaDB (primary), Redis (cache/queue/session)│
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Module map (PRD → Frappe)

| PRD Module | Frappe module name | Primary responsibility |
|------------|-------------------|----------------------|
| M1 Farmer Registry | `Farmer Registry` | Farmer identity, land, tags |
| M2 Inventory | `Inventory` | Items, 2 godowns, stock movements |
| M3 Billing | `Billing` | Cash & carry, project billing, payments |
| M4 MIMIS Sync | `MIMIS Sync` | Excel import, reconciliation (no portal) |
| M5 Project Lifecycle | `Project Lifecycle` | **Farmer Project**, stage history, transitions |
| M6 Task Engine | `Task Engine` | Follow-ups, templates, automation rules |
| M7 Service / AMC | `Service` | 3-year maintenance lifecycle |
| M8 Officer Network | `Officer Network` | Hierarchy, assignment history, expenses |
| M9 Profit Dashboard | `Profit` | Expenses, cost snapshots, owner reports |

### 2.3 Farmer Project as aggregate root

**Farmer Project** is the central workflow entity. All subsidy operations attach to it:

- Current stage (1 of 12, sequential)
- Geographic scope (block, cluster, village)
- Officer reference (current; history elsewhere)
- Financial summary fields for profit visibility
- Links to tasks, documents, billing, inventory movements

**Project Stage History** records every transition:

- From stage, to stage, actor, timestamp, notes, attachment references
- Immutable append-only semantics (corrections via compensating entries, not deletes)

**Stage transition** is permitted only through `ProjectLifecycleService`:

- Validates sequential rules (no skipping)
- Writes history row
- Triggers task template evaluation
- Emits audit event
- Returns structured result for mobile sync reconciliation

### 2.4 Twelve-stage lifecycle

| # | Stage key (storage) | Display (i18n) |
|---|---------------------|----------------|
| 1 | `lead_captured` | Lead Captured |
| 2 | `eligibility_check` | Eligibility Check |
| 3 | `documents_collected` | Documents Collected |
| 4 | `mimis_registered` | MIMIS Registered |
| 5 | `field_survey` | Field Survey |
| 6 | `quotation_generated` | Quotation Generated |
| 7 | `pre_inspection_approval` | Pre-Inspection Approval |
| 8 | `work_order_received` | Work Order Received |
| 9 | `material_dispatched` | Material Dispatched |
| 10 | `installation_done` | Installation Done |
| 11 | `post_inspection_approval` | Post-Inspection Approval |
| 12 | `subsidy_released` | Subsidy Released |

**Rules:** sequential only · no skipping · auto task generation per stage · timeline mandatory.

### 2.5 Officer assignment history

Officers rotate approximately every three years. The system **preserves historical ownership**:

- **Officer Assignment History** stores: officer, cluster, village set (or scope), `valid_from`, `valid_to`, reason
- Current assignment = row where `valid_to` is null
- Transfers close the active row and open a new row—never delete or overwrite history
- Reports and filters must support “as-of” officer for completed projects

### 2.6 Geographic hierarchy

```
District → Block → Cluster → Officer → Village → Farmer
```

- Master data is server-authoritative
- Mobile caches hierarchy in Hive for offline filtering
- List APIs always support `block`, `cluster`, `officer`, `village` filters
- Phase 1 operates within a single district context; multi-district master-data rules are defined in [§21.1](#211-multi-district-operations)

### 2.7 Cross-cutting backend concerns

| Concern | Approach |
|---------|----------|
| Validation | DocType `validate` hooks + service-layer business rules |
| Idempotency | `client_id` (UUID) on mobile-originated creates |
| Versioning | `modified` timestamp + optional integer `doc_version` on hot entities |
| Files | Frappe File linked to MinIO backend |
| Reports | Report Builder + Script Reports for owner dashboard |
| Fixtures | Stages, roles, task templates, blocks exported as JSON |

### 2.8 What we do not build on Frappe

- **MIMIS government portal** — never recreated; Excel reconciliation only
- **Generic ERP desk** as primary UX — mobile timeline is primary for field and office staff
- **Real-time bidirectional MIMIS API** — out of scope for v1

---

## 3. Flutter feature-first architecture

### 3.1 Directory layout

```
lib/
├── app/
│   ├── app.dart
│   ├── bootstrap.dart              # Init: Hive, Drift, env, ProviderScope
│   └── router/                     # go_router (only router)
│
├── core/
│   ├── design_tokens/              # Colors, spacing, typography (from UI_TOKENS.md)
│   ├── i18n/                       # l10n delegates, locale resolution
│   ├── network/                    # Dio, interceptors, auth refresh
│   ├── database/                   # Drift database, Hive adapters
│   ├── sync/                       # SyncWorker, ConflictResolver, policies
│   ├── errors/                     # Failure types, error mapping
│   └── utils/
│
├── shared/
│   ├── widgets/                    # Reusable UI (no feature logic)
│   ├── models/
│   └── extensions/
│
└── features/
    ├── auth/
    ├── farmer_registry/            # M1
    ├── project_lifecycle/          # M5 — primary workflow UI
    ├── tasks/                      # M6
    ├── inventory/                  # M2
    ├── billing/                    # M3
    ├── mimis_sync/                 # M4 — Excel upload, batch status
    ├── service_amc/                # M7
    ├── officer_network/            # M8
    ├── profit_dashboard/           # M9 — owner-oriented
    └── settings/
```

### 3.2 Feature slice structure

Each feature follows the same internal layout:

```
features/{feature}/
├── data/
│   ├── datasources/        # local (Drift/Hive), remote (Dio)
│   ├── models/             # DTOs, serializers, mappers
│   └── repositories/       # Repository implementations
├── domain/
│   ├── entities/
│   ├── repositories/       # Abstract contracts
│   └── usecases/           # Multi-step business operations
└── presentation/
    ├── providers/          # Riverpod
    ├── screens/
    └── widgets/
```

### 3.3 Navigation and shells

- **go_router** exclusively; no other navigation packages
- Role-aware shells: Field, Office, Installer, Service, Store, Owner
- Deep links: `/projects/{id}/timeline` as the primary project surface
- Tamil-first: default locale `ta` where user preference unset; always support `en`

### 3.4 UI architecture principles

| Principle | Implementation |
|-----------|----------------|
| Timeline-first | Project screen = vertical timeline + next action CTA |
| Workflow-first | Stage chip, allowed transitions, blocked states visible |
| No ERP patterns | Avoid multi-tab forms; use step sheets and bottom actions |
| Design tokens | All colors/spacing from tokens; never hardcoded hex |
| i18n | All user-visible strings via ARB keys; never hardcoded Tamil |

Inspired influences (PRD): Linear, Notion, Khatabook, PhonePe — clarity over density.

---

## 4. Sync engine architecture

### 4.1 Overview

```
                    WRITE PATH
┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│   UI    │───►│  Repository │───►│  SyncQueue  │───►│ SyncWorker   │
└─────────┘    │  (Drift)    │    │  (Drift)    │    │ (background) │
                 └─────────────┘    └─────────────┘    └──────┬───────┘
                      ▲                                         │
                      │ merge                                   ▼
┌─────────┐    ┌─────────────┐                         ┌──────────────┐
│  Hive   │◄───│  Drift DB   │◄────────────────────────│ Frappe API   │
│ masters │    │  entities   │      DELTA PULL          └──────────────┘
└─────────┘    └─────────────┘
                    READ PATH
```

### 4.2 Components

| Component | Storage | Responsibility |
|-----------|---------|----------------|
| **SyncQueue** | Drift table | Outbox: pending mutations with `client_id`, payload, status, retries |
| **SyncWorker** | Dart isolate / foreground service | Flushes queue when online; respects ordering |
| **DeltaPull** | Scheduled + on-foreground | `modified_since` fetch per entity family |
| **ConflictResolver** | Pure logic | Applies PRD conflict policies |
| **IdempotencyStore** | Drift | Maps `client_id` → server `name` after first successful push |

### 4.3 Conflict resolution policies

| Data class | Policy | Examples |
|------------|--------|----------|
| Master data | **Server wins** | Block, village, officer list, item catalog |
| New records | **Client wins** | New farmer, new farmer project, draft task |
| Field updates | **Last-write-wins** | Task notes, visit logs (compare `modified` / `doc_version`) |
| Stage transition | **Server authoritative** | Reject stale client transition; force timeline refresh |

### 4.4 Ordering and concurrency

- Operations for the **same Farmer Project** are processed **serially** (stage order integrity)
- Unrelated entities may flush in parallel batches
- Maximum batch size configurable (default: 50 operations per push)
- Exponential backoff: 1s, 2s, 4s, … cap at 5 minutes; permanent failures surface in UI

### 4.5 Sync states (per queue item)

| State | Meaning |
|-------|---------|
| `pending` | Awaiting network |
| `in_flight` | Request sent, awaiting response |
| `synced` | Server acknowledged |
| `conflict` | Resolver could not auto-merge; user action required |
| `failed` | Exhausted retries; manual retry available |

### 4.6 MIMIS separation

MIMIS Excel import is **not** part of the real-time SyncQueue. It uses a dedicated batch pipeline (see §13).

---

## 5. API standards

### 5.1 Base URL and versioning

- Base: `https://{site}/api/method/agriflow.api.v1.{area}.{action}`
- Version namespace: `v1` — breaking changes require `v2`
- Mobile sends `X-AgriFlow-Client-Version` and `X-AgriFlow-Platform` headers

### 5.2 Response envelope

All custom API methods return a uniform envelope:

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Success indicator |
| `data` | object / array | Payload on success |
| `error` | object / null | `{ code, message, details }` on failure |
| `server_time` | ISO 8601 | Server clock for sync alignment |

### 5.3 Authentication

| Endpoint | Purpose |
|----------|---------|
| `auth.login` | Exchange credentials for JWT access + refresh |
| `auth.refresh` | Rotate access token |
| `auth.logout` | Invalidate refresh token server-side |

- Access token TTL: short (15–60 minutes)
- Refresh token: longer, stored in secure storage on device
- Frappe desk users may use standard session cookies (out of mobile path)

### 5.4 Core API surface (v1)

**Farmer Project (workflow-centric)**

| Method | Purpose |
|--------|---------|
| `project.list` | Filtered list: block, cluster, officer, stage, `modified_since` |
| `project.get` | Single project with summary fields |
| `project.timeline` | Stage history + open tasks + next allowed stage |
| `project.create` | Idempotent create via `client_id` |
| `project.transition` | Validated stage advance |

**Sync**

| Method | Purpose |
|--------|---------|
| `sync.push` | Batch apply outbox operations |
| `sync.pull` | Delta download by entity type and `since` |

**Master data**

| Method | Purpose |
|--------|---------|
| `master.blocks` | Block list for district |
| `master.villages` | Villages by block/cluster |
| `master.officers` | Officers with current cluster mapping |
| `master.clusters` | Cluster definitions |

**MIMIS**

| Method | Purpose |
|--------|---------|
| `mimis.upload_excel` | Initiate import batch |
| `mimis.batch_status` | Poll processing status |
| `mimis.reconciliation_report` | Row-level match results |

### 5.5 Pagination and filtering

- Cursor-based pagination: `cursor`, `limit` (default 25, max 100)
- All list endpoints support geographic and role scoping
- Delta sync: `modified_since` (ISO 8601 UTC) required for pull endpoints

### 5.6 Idempotency

- Every mobile-originated **create** includes `client_id` (UUID v4)
- Server stores `client_id` → document `name` mapping; duplicate push returns original document

---

## 6. Repository pattern

### 6.1 Layer responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Abstract repository** (domain) | Contract for feature; no Flutter/framework imports |
| **Repository implementation** (data) | Orchestrates local + remote; applies conflict policy |
| **Local data source** | Drift and/or Hive CRUD, streams |
| **Remote data source** | Dio/Retrofit API calls |
| **Mapper** | DTO ↔ entity conversion |

### 6.2 Dependency rule

```
Presentation → Provider → UseCase → Repository → DataSource
```

- Repositories never import widgets or Riverpod
- Use cases encapsulate multi-step flows (e.g., stage transition with attachment refs)

### 6.3 Read strategy

1. **Immediate**: emit from Drift via `Stream` / `watch`
2. **Background refresh**: if online and cache TTL expired, fetch delta
3. **Stale indicator**: UI may show “last updated” timestamp from sync metadata

### 6.4 Write strategy

1. Validate locally against cached rules (allowed next stage, required fields)
2. Optimistic write to Drift
3. Enqueue SyncQueue row
4. SyncWorker pushes; on success, reconcile server IDs and versions
5. On conflict, delegate to ConflictResolver; surface user-actionable state

### 6.5 Repository inventory (by feature)

| Repository | Primary entities |
|------------|------------------|
| `FarmerProjectRepository` | Farmer Project, timeline, transitions |
| `FarmerRepository` | Farmer, land details |
| `TaskRepository` | Tasks, completions |
| `InventoryRepository` | Items, stock by godown |
| `BillingRepository` | Invoices, payments |
| `MimisRepository` | Import batches, reconciliation rows |
| `OfficerRepository` | Officers, clusters, assignment history (read) |
| `MasterDataRepository` | Blocks, villages, cached masters |
| `AuthRepository` | Session, tokens, user profile |

---

## 7. Riverpod state architecture

### 7.1 Provider tiers

| Tier | Location | Examples |
|------|----------|----------|
| **Core** | `core/` or `app/` | `connectivityProvider`, `authProvider`, `databaseProvider`, `syncStatusProvider` |
| **Feature** | `features/*/presentation/providers/` | `projectListProvider`, `projectTimelineProvider` |
| **Scoped** | `family` modifiers | `projectDetailProvider(projectId)` |

### 7.2 Provider type selection

| Pattern | Use when |
|---------|----------|
| `@riverpod` + codegen | Standard async lists and details |
| `AsyncNotifier` | Multi-step flows: stage transition, Excel upload, login |
| `StreamProvider` | Drift-backed live lists |
| `Notifier` | Synchronous UI state: filters, selected block |
| `keepAlive: true` | Auth session, sync worker, master cache |

### 7.3 Global sync visibility

`syncStatusProvider` exposes:

- Pending queue count
- Last successful sync time
- In-flight / error state
- Manual “sync now” trigger

Field staff must trust offline mode; visible sync status reduces anxiety and support calls.

### 7.4 State shape conventions

- Lists: `AsyncValue<List<T>>` with explicit loading/error/data UI
- Timeline: dedicated view model combining stage history, tasks, and next action
- Filters: separate `Notifier` persisted per role (field staff defaults to assigned block)

### 7.5 Testing

- Override providers in widget tests
- Unit test repositories and notifiers independently
- No business logic in `build()` methods beyond wiring

---

## 8. Offline-first flow

### 8.1 Day-in-the-life (field staff)

| Phase | Behavior |
|-------|----------|
| **Morning (online)** | Login → delta pull masters + assigned projects → cache warm |
| **Field (offline)** | All reads from Drift/Hive; all writes to SyncQueue |
| **Evening (online)** | SyncWorker flushes queue; conflicts surfaced |
| **Office review** | Owner/manager sees updated timelines on desk or mobile |

### 8.2 Data flow diagram

```
User Action
    │
    ▼
UseCase.validate()
    │
    ├──► Drift (optimistic entity update)
    │
    └──► SyncQueue.insert(operation)
              │
              ▼ (when online)
         SyncWorker → sync.push API
              │
              ├── success → update server name, mark synced
              └── conflict → ConflictResolver → UI notification
```

### 8.3 Offline-capable operations

| Operation | Offline | Notes |
|-----------|---------|-------|
| View project list / timeline | Yes | Cached |
| Create farmer / project | Yes | `client_id` idempotency |
| Complete task / add visit note | Yes | LWW on sync |
| Stage transition | Yes* | Queued; server may reject if stale |
| View master data | Yes | Hive snapshot |
| MIMIS Excel upload | No | Requires connectivity; batch job |
| Owner profit reports | Partial | Cached aggregates; refresh online |

### 8.4 Connectivity handling

- Listen to connectivity changes; trigger SyncWorker on regain
- Do not block UI on network waits
- Queue depth badge in app shell for transparency

---

## 9. Database strategy

### 9.1 Server (MariaDB via Frappe)

| Aspect | Decision |
|--------|----------|
| Primary store | MariaDB 11 |
| ORM | Frappe DocType ORM |
| Indexing | Composite indexes on `(block, current_stage)`, `(modified)`, `(officer, block)` |
| Migrations | Frappe patches in `apps/agriflow/patches/` |
| Backups | Daily automated to Backblaze (see §17) |

### 9.2 Mobile — Drift (SQLite)

**Authoritative local store for operational entities:**

| Table family | Contents |
|--------------|----------|
| `farmer_projects` | Project records, stage, sync metadata |
| `farmers` | Farmer profiles |
| `tasks` | Tasks and completion state |
| `project_stage_history` | Cached timeline rows |
| `sync_queue` | Outbox operations |
| `sync_metadata` | Last pull timestamps per entity type |
| `idempotency_map` | `client_id` → server `name` |

- Schema migrations via Drift migration strategy
- Generated code checked into repo or CI-generated per team policy

### 9.3 Mobile — Hive

**Fast read cache for master data and preferences:**

| Box | Contents |
|-----|----------|
| `master_blocks` | Block list |
| `master_villages` | Village index |
| `master_officers` | Officer + cluster snapshot |
| `master_items` | Product catalog (inventory) |
| `user_prefs` | Locale, theme, last-selected block |
| `auth_meta` | Non-secret session hints (tokens in secure storage) |

### 9.4 Redis (server)

| Use | Purpose |
|-----|---------|
| Cache | Hot master data, session cache |
| Queue | Background jobs (see §11) |
| Rate limiting | Optional API throttling |
| Pub/sub | Optional real-time desk notifications (v2) |

### 9.5 Data retention

| Data | Retention |
|------|-----------|
| Project stage history | Indefinite |
| Officer assignment history | Indefinite |
| Audit logs | Minimum 7 years (business policy) |
| MIMIS import batches | 2 years active; archive thereafter |
| SyncQueue (mobile) | Purge `synced` rows after 30 days |

---

## 10. File upload strategy

### 10.1 Storage backend

- **MinIO** (S3-compatible) as object store behind Frappe File
- Production: dedicated bucket per environment (`agriflow-prod`, `agriflow-staging`)
- CDN not required v1; Caddy serves Frappe; presigned URLs for large downloads

### 10.2 Upload flow (mobile)

```
1. User selects file (camera / gallery / document picker)
2. Client validates: size, MIME type, extension allowlist
3. If offline → store file in app sandbox; queue FileUpload operation in SyncQueue
4. If online → multipart upload to agriflow.api.v1.file.upload
5. Server validates again; stores in MinIO; returns file_id / url
6. Reference file_id on project transition or task attachment
```

### 10.3 Validation rules (server and client)

| Rule | Limit |
|------|-------|
| Max file size | 10 MB (images), 25 MB (PDF) — configurable |
| Allowed MIME | `image/jpeg`, `image/png`, `application/pdf` |
| Filename | Sanitized; no path traversal |
| Virus scan | Optional ClamAV hook (Phase 2) |

### 10.4 Offline file handling

- Files stored in app documents directory with queue reference
- Upload retried before dependent operations (transition with attachment) or in same batch with ordering metadata
- Failed uploads block stage transition completion until resolved

### 10.5 Access control

- Files inherit RBAC from parent Farmer Project
- Presigned URLs short-lived (15 minutes default)
- No public buckets

---

## 11. Queue and job architecture

### 11.1 Redis job queues (Frappe)

| Queue | Job types | Priority |
|-------|-----------|----------|
| `short` | Email, single-row updates | High |
| `default` | Task generation, notifications | Medium |
| `long` | MIMIS Excel parse, bulk reconciliation, reports | Low |

### 11.2 Background jobs

| Job | Trigger | Output |
|-----|---------|--------|
| `process_mimis_import` | Excel upload complete | Reconciliation rows, optional stage suggestions |
| `generate_stage_tasks` | Stage transition | Task documents from templates |
| `send_follow_up_reminder` | Scheduled (cron) | WhatsApp via Evolution API (if enabled) |
| `compute_profit_snapshot` | Nightly | Project cost aggregates for M9 |
| `purge_temp_files` | Weekly | Clean failed upload stubs |

### 11.3 Scheduling

- Frappe scheduler (`hooks.py`) for cron-style jobs
- Follow-up reminders: daily 07:00 IST for open overdue tasks
- Profit snapshot: daily 02:00 IST

### 11.4 Mobile SyncWorker (not Redis)

- Runs in Dart: `Workmanager` or foreground sync on app resume
- Separate from server queues; only consumes `sync.push` API
- Does not process MIMIS Excel—that is server-only

### 11.5 Failure handling for jobs

- Retry 3 times with backoff for transient errors
- Dead letter: mark batch `failed` with error log; notify Office Manager role
- Idempotent job design: safe to re-run `process_mimis_import` with same `batch_id`

---

## 12. Role-based access architecture

### 12.1 Roles (PRD)

| Role | Primary capabilities |
|------|---------------------|
| **Owner** | Full access; profit dashboard; all blocks |
| **Office Manager** | Approvals, reports, billing, MIMIS import approval |
| **Office Staff** | Farmer registration, quotation, documents |
| **Field Staff** | Survey, visits, follow-ups; scoped to assigned geography |
| **Installer Team** | Installation-stage tasks and material confirmation |
| **Service Technician** | AMC visits, service module |
| **Store Keeper** | Inventory across 2 godowns |

### 12.2 Permission model

| Layer | Mechanism |
|-------|-----------|
| Frappe Role | Per-DocType create/read/write/submit/cancel |
| User Permission | Restrict by `Block`, optionally `Cluster` |
| API layer | Explicit role check before whitelisted methods |
| Mobile UI | Route guards + feature flags from `user.permissions` payload |

### 12.3 Data scoping rules

| Role | Scope |
|------|-------|
| Field Staff | Assigned block(s) + active projects only |
| Installer | Projects in stages 9–10 + linked tasks |
| Service Tech | Projects with active AMC |
| Store Keeper | Inventory module; no farmer PII export |
| Owner | Unrestricted within tenant |

### 12.4 Stage-action permissions

Certain transitions require elevated roles:

| Stage transition | Minimum role |
|------------------|--------------|
| Pre/Post inspection approval | Office Manager |
| Subsidy released | Owner or Office Manager |
| Material dispatched | Store Keeper + Office Staff |
| Field survey complete | Field Staff |

Enforced in `ProjectLifecycleService`, not UI alone.

### 12.5 Permission sync to mobile

- On login and daily refresh: download permission manifest
- Cache in Hive; gate routes and action buttons
- Server always re-validates; mobile gating is UX-only

---

## 13. MIMIS reconciliation architecture

### 13.1 Constraints

- **Never recreate the MIMIS government portal**
- **Sync via Excel reconciliation only** — no live government API in v1
- Human approval required before automatic stage advancement

### 13.2 Pipeline

```
Excel Upload (Office Manager)
        │
        ▼
MIMIS Import Batch (server) ──► validate schema / columns
        │
        ▼
Background Job: process_mimis_import
        │
        ├── Match by: farmer ID, mobile, project reference, MIMIS registration number
        ├── Outcome per row: matched | ambiguous | unmatched
        └── Write Reconciliation Log rows
        │
        ▼
Review UI (Office Manager) ──► approve / reject / manual link
        │
        ▼
Optional: project.transition → mimis_registered (stage 4)
        │
        ▼
Audit log + notification
```

### 13.3 Matching strategy

| Priority | Key |
|----------|-----|
| 1 | MIMIS registration number (exact) |
| 2 | Government farmer ID |
| 3 | Mobile + name fuzzy (Tamil normalized) |
| 4 | Manual link by office staff |

### 13.4 Idempotency

- Each import has unique `batch_id`
- Row hash prevents duplicate processing on re-upload
- Re-import of same file is no-op with warning

### 13.5 Mobile role

- Upload Excel from device (online only)
- Poll `mimis.batch_status`
- Display reconciliation report; no offline MIMIS processing

### 13.6 Templates

- Versioned Excel templates in `packages/excel_templates/`
- Template version in file metadata; reject unknown formats

---

## 14. Naming conventions

### 14.1 Frappe

| Artifact | Convention | Example |
|----------|------------|---------|
| App name | lowercase | `agriflow` |
| Module | Title Case | `Project Lifecycle` |
| DocType | Title Case singular | `Farmer Project` |
| Field | snake_case | `current_stage` |
| Stage key | snake_case | `lead_captured` |
| API method | `agriflow.api.v1.{area}.{verb}` | `agriflow.api.v1.project.transition` |
| Fixture file | `{doctype}.json` | `task_template.json` |
| Patch | `patch_{date}_{description}.py` | `patch_20260520_officer_history.py` |

### 14.2 Flutter

| Artifact | Convention | Example |
|----------|------------|---------|
| Feature directory | snake_case | `project_lifecycle/` |
| File | snake_case | `farmer_project_repository.dart` |
| Class | PascalCase | `FarmerProject` |
| Provider | camelCase + `Provider` | `projectTimelineProvider` |
| Route path | lowercase segments | `/projects/:id/timeline` |
| Drift table | snake_case plural | `farmer_projects` |
| Hive box | snake_case | `master_officers` |

### 14.3 i18n keys

- Pattern: `{domain}.{context}.{key}`
- Examples: `project.stage.lead_captured`, `task.follow_up.visit`, `error.sync.conflict`
- Tamil strings only in ARB files, never in Dart source

### 14.4 Design tokens

- Reference: `UI_TOKENS.md`
- Dart: `AppColors.primary`, `AppSpacing.md`, `AppTypography.title`
- No inline color literals in widgets

---

## 15. Error handling strategy

### 15.1 Error taxonomy

| Category | Code prefix | User-facing |
|----------|-------------|-------------|
| Validation | `VAL_` | Specific field message via i18n |
| Auth | `AUTH_` | Re-login prompt |
| Permission | `PERM_` | “Not allowed” with role hint |
| Sync | `SYNC_` | Retry + conflict resolution UI |
| Network | `NET_` | Offline mode message; no alarm |
| Server | `SRV_` | Generic + support reference ID |
| MIMIS | `MIMIS_` | Row-level import errors |

### 15.2 Mobile

- Use `Result` / `Either` pattern in domain layer ( sealed failure types)
- Map exceptions to `AppFailure` in data layer
- `AsyncValue.error` in UI with recovery actions (retry, refresh, contact support)
- Never expose stack traces to users

### 15.3 Backend

- Raise `frappe.ValidationError` for business rule violations
- Return structured `error` object in API envelope
- Log full traceback server-side with correlation ID

### 15.4 Sync-specific errors

| Error | Behavior |
|-------|----------|
| Stale stage transition | Mark conflict; refresh timeline |
| Duplicate `client_id` | Treat as success; return existing document |
| Master data conflict | Overwrite local with server payload |
| Partial batch failure | Return per-operation results; retry failed only |

### 15.5 Correlation

- Every API request accepts optional `X-Request-ID`; generate if missing
- Mobile logs include `request_id` for support diagnosis

---

## 16. Logging and audit strategy

### 16.1 Audit (business-critical)

**Mandatory audit for:**

- Stage transitions (who, when, from, to)
- Officer assignment changes
- MIMIS import and reconciliation decisions
- Billing and payment events
- Stock movements between godowns
- Permission changes

**Audit Log DocType fields:**

- `timestamp`, `actor`, `action`, `reference_doctype`, `reference_name`, `before`, `after`, `ip_address`, `client_id`

- Append-only; no hard deletes
- Owner can export audit report

### 16.2 Application logging (server)

| Level | Destination | Content |
|-------|-------------|---------|
| ERROR | File + optional Sentry | Exceptions, job failures |
| WARNING | File | Deprecated API use, retry attempts |
| INFO | File | Import batch start/complete, sync batch sizes |
| DEBUG | Dev only | SQL, request payloads (no PII) |

- Structured JSON logs in production
- PII masking in logs (mobile numbers partially redacted)

### 16.3 Mobile logging

- Debug logs: debug builds only
- Production: crash reporting (e.g., Firebase Crashlytics) without PII
- Sync operation log table in Drift (last 100 events) for field diagnostics

### 16.4 Frappe built-in

- Version table enabled for Farmer Project, Farmer, Officer
- Communication log for WhatsApp messages (if Evolution API used)

---

## 17. Deployment topology

### 17.1 Production stack

```
                    Internet
                        │
                        ▼
                   ┌─────────┐
                   │  Caddy  │  TLS termination
                   └────┬────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Frappe   │  │  MinIO   │  │ Evolution│
    │ (Gunicorn│  │          │  │   API    │
    │  +Nginx) │  │          │  │ (WhatsApp│
    └────┬─────┘  └──────────┘  └──────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│MariaDB │ │ Redis  │
│  11    │ │   7    │
└────────┘ └────────┘

        Backblaze B2 (daily backups)
        Hetzner VPS (Coolify orchestration)
```

### 17.2 Environments

| Environment | Purpose | Data |
|-------------|---------|------|
| `dev` | Local bench / Docker Compose | Synthetic |
| `staging` | Pre-release QA on Coolify | Anonymized copy |
| `production` | Live dealer operations | Real |

### 17.3 Coolify deployment

- One service stack per environment
- Environment variables for secrets (DB password, JWT secret, MinIO keys)
- Health checks on Frappe `/api/method/ping`
- Zero-downtime deploy: rolling container update

### 17.4 Mobile distribution

- Android APK/AAB internal distribution (v1)
- Minimum supported version enforced via site config `min_mobile_version`
- Force upgrade only for breaking API changes

### 17.5 Backup and recovery

| Asset | Frequency | Target |
|-------|-----------|--------|
| MariaDB dump | Daily | Backblaze B2 |
| MinIO bucket | Daily incremental | Backblaze B2 |
| Redis | RDB snapshot daily | Optional |
| RTO target | 4 hours | |
| RPO target | 24 hours | |

---

## 18. Security practices

### 18.1 Authentication and session

- JWT for mobile (access + refresh)
- bcrypt password hashing (Frappe default)
- Account lockout after failed login attempts
- Refresh token rotation on use

### 18.2 Transport

- TLS 1.2+ everywhere (Caddy)
- Certificate auto-renewal via Let's Encrypt
- HSTS enabled in production

### 18.3 Application security

| Control | Implementation |
|---------|----------------|
| RBAC | Frappe roles + User Permissions |
| Input validation | DocType validators + API schema checks |
| File upload | MIME/size allowlist; no executable extensions |
| SQL injection | Frappe ORM only; no raw SQL in API layer |
| XSS | Escaped templates; mobile WebView avoided |
| CSRF | Frappe CSRF for desk; JWT for mobile API |
| Rate limiting | Redis-backed per-IP on auth endpoints |

### 18.4 Secrets management

- Secrets in Coolify environment, not in git
- Separate MinIO credentials per environment
- JWT signing key minimum 256 bits; rotate annually

### 18.5 Mobile security

- Tokens in platform secure storage (Keychain / EncryptedSharedPreferences)
- Certificate pinning (optional Phase 2)
- No sensitive data in logs
- Root/jailbreak detection (optional Phase 2)

### 18.6 Compliance posture

- Audit trail for financial and stage changes
- Data export on request (owner role)
- PII minimization in analytics

---

## 19. Scalability considerations

### 19.1 Current scale (v1)

- ~15 daily users
- 12 blocks, single district
- Estimated projects: thousands active; tens of thousands historical

Architecture is **right-sized** for current load; patterns support growth without rewrite.

### 19.2 Horizontal scaling path

| Component | Scale lever |
|-----------|-------------|
| Frappe | Additional Gunicorn workers; read replica for reports |
| MariaDB | Read replica; archive old projects to cold storage |
| Redis | Redis Cluster if queue depth grows |
| MinIO | Distributed mode if storage exceeds single node |
| Mobile | Stateless; no server session stickiness |

### 19.3 Multi-district future (PRD §19)

Operational scaling patterns (read replicas, workers) are defined here. **Geographic, lead, and project-type expansion** is specified as architecture placeholders in [§21 Future Expansion Architecture](#21-future-expansion-architecture)—not implemented in Phase 1.

### 19.4 Performance targets

| Operation | Target (p95) |
|-----------|--------------|
| `project.list` (25 rows) | < 300 ms |
| `project.timeline` | < 400 ms |
| `sync.push` (50 ops) | < 2 s |
| Mobile cold start | < 3 s |
| Delta pull (masters) | < 5 s |

### 19.5 Caching strategy

- Server: Redis cache for master data (TTL 1 hour)
- Mobile: Hive masters refreshed daily or on explicit pull
- Invalidate on fixture deploy for master changes

### 19.6 What not to optimize prematurely

- Real-time WebSocket sync (v2 if needed)
- Microservices split (monolith Frappe app remains)
- Elasticsearch (Frappe reports sufficient at current scale)

---

## 20. Architectural invariants

These rules must **never** be violated without an explicit architecture review and PRD amendment.

| # | Invariant |
|---|-----------|
| 1 | **Farmer Project** is the aggregate root for subsidy workflow. |
| 2 | **12 stages** are strictly sequential; no skipping; transitions only via `ProjectLifecycleService`. |
| 3 | **Project Stage History** is append-only and mandatory for every transition. |
| 4 | **Officer assignment history** is preserved; transfers close old rows, never delete. |
| 5 | **MIMIS** is Excel reconciliation only; never recreate the government portal. |
| 6 | **Mobile writes** go through **SyncQueue** before server; no direct fire-and-forget API writes from UI. |
| 7 | **Master data conflicts** resolve server-wins; **new records** client-wins; **updates** last-write-wins. |
| 8 | **Stage authority** is server-side; stale client transitions are rejected, not silently merged. |
| 9 | **Tamil-first** UI via i18n; no hardcoded Tamil strings in source. |
| 10 | **Design tokens** only; no hardcoded colors in Flutter widgets. |
| 11 | **Riverpod only** for state; **go_router only** for navigation. |
| 12 | **Feature-first** Flutter structure under `lib/features/{feature}/`. |
| 13 | **Frappe DocTypes + fixtures** for schema and seed data; no ad-hoc production SQL. |
| 14 | **Role-based access** enforced on server; mobile guards are supplementary. |
| 15 | **Audit logs** mandatory for stage, officer, MIMIS, billing, and stock changes. |
| 16 | **Phase 1: no AI features** (PRD §16). |
| 17 | **Timeline-first** project UI is the primary operational surface. |
| 18 | **Auto task generation** on stage entry is required behavior, not optional. |

Phase 1 invariants above remain authoritative. Future capabilities in §21 must not weaken §1–§20 without an architecture review.

---

## 21. Future Expansion Architecture

> **Status:** Future-ready placeholders only.  
> **Phase 1:** Not implemented. No schema, API, or mobile code for this section unless explicitly approved in a later PRD phase.

This section defines **how AgriFlow OS can extend** without redesigning the workflow-first, offline-first core. **Farmer Project remains the aggregate root** for all committed work; leads and opportunities are upstream inputs that may convert into projects.

### 21.0 Purpose and scope

| Principle | Guidance |
|-----------|----------|
| Extensibility without complexity | Extension points are master-data and link fields—not parallel workflow engines |
| Workflow-first preserved | Subsidy 12-stage lifecycle stays the reference model; other project types attach variant stage templates |
| Offline-first preserved | Future lead capture follows the same SyncQueue pattern; master geography remains server-wins |
| No Phase 1 delivery | Document and fixture hooks only; defer DocType creation until a scoped phase gate |
| No schema overengineering | Placeholder DocTypes listed conceptually; implement minimal fields when a phase starts |
| No unnecessary code generation | Flutter feature folders and API namespaces are **reserved names**, not scaffolded |

**Relationship to current architecture**

```
[Future] Lead / Opportunity          [Current] Farmer Project (aggregate root)
         │                                      │
         └──────── convert ────────────────────►│──► 12-stage timeline (subsidy)
                                                │──► alternate stage templates (future types)
```

---

### 21.1 Multi-District Operations

**Goal:** Support Tamil Nadu–scale operations and onboarding of additional districts without code changes to hierarchy logic.

#### 21.1.1 Hierarchy model (master-data driven)

All geography is **fixture- or admin-managed master data**. Application code must never assume a fixed district name, block count, or single-dealer district.

```
State (Tamil Nadu)          [Future master: State]
    └── District            [Future master: District]     ← tenant boundary candidate
            └── Block       [Master: Block]               ← exists Phase 1 (scoped)
                    └── Cluster   [Master: Cluster]
                            └── Village   [Master: Village]
                                    └── Farmer
```

| Level | Phase 1 | Future |
|-------|---------|--------|
| State | Implicit (TN) | Explicit `State` DocType if multi-state ever needed |
| District | Implicit (Tiruvannamalai) | Explicit `District`; required parent of `Block` |
| Block → Village | Master-driven | Unchanged; add `district` link on Block |

#### 21.1.2 Design rules

- **No hardcoded geographic assumptions** in API filters, mobile defaults, or reports—always resolve from user's `District` / `Block` permissions.
- **District onboarding playbook:** fixtures export (blocks, clusters, villages, officers) + User Permission template + MinIO prefix per district (see §17).
- **Officer history** (§2.5) applies per cluster within district; no change to append-only semantics.
- **Mobile Hive cache** keys masters by `district_id` + `modified_since` so multiple districts can coexist on one device for owner roles only.

#### 21.1.3 Placeholder DocTypes (conceptual)

| DocType | Role |
|---------|------|
| `District` | Top-level operational scope; links to state |
| `Dealer Tenant` (optional) | SaaS boundary: one dealer org per tenant, many districts |

*Implementation note:* Phase 1 may use implicit single district; adding `District` is a **data migration + link field** on `Block`, not a new app.

---

### 21.2 Lead Ecosystem Architecture

**Goal:** Capture demand from multiple channels before a Farmer Project exists, without fragmenting the operational timeline.

#### 21.2.1 Lead vs project

| Concept | Responsibility |
|---------|----------------|
| **Lead** | Pre-project intent: contact, source, category, crop interest, block/village hint |
| **Farmer Project** | Post-qualification operational entity with stage history and tasks |
| **Conversion** | One-way (or rare reopen) link: Lead → Farmer Project; preserves `lead_source` on project |

#### 21.2.2 Lead channel placeholders

Architecture reserves **lead category** and **source type** enumerations (fixtures)—not hardcoded UI branches.

| Channel placeholder | Description | Typical owner role |
|---------------------|-------------|-------------------|
| Farmer leads | Walk-in / field enquiry | Field Staff, Office Staff |
| VIP referrals | High-priority referrer | Office Manager |
| Agriculture department leads | Govt agri officer referral | Field Staff |
| Horticulture department leads | Horticulture officer referral | Field Staff |
| Forest department referrals | Forest dept. contact | Field Staff |
| Sugar mill staff referrals | Mill employee referral | Office Staff |
| Existing customer referrals | Prior farmer/customer | Office Staff |
| Institutional leads | Schools, cooperatives, FPOs | Office Manager |
| Tree crop irrigation enquiries | Plantation / orchard interest | Field Staff |
| Cash & Carry drip opportunities | Non-subsidy retail intent | Store Keeper, Office Staff |

Each channel maps to **`Lead Source`** + **`Lead Category`** (§21.3), not to separate mobile apps or duplicate sync engines.

#### 21.2.3 Flutter extension (reserved)

```
lib/features/
    lead_capture/          # [Future] list, create, assign, convert
    referral_dashboard/    # [Future] partner and source analytics (owner)
```

Offline: lead create uses SyncQueue with `client_id`; conversion calls server to atomically create Farmer Project + link.

#### 21.2.4 Frappe extension (reserved)

| Module (future) | Name |
|-----------------|------|
| M10 | `Lead Management` |

Services (future): `LeadConversionService`, `LeadAssignmentService`—mirror pattern of `ProjectLifecycleService`.

---

### 21.3 Lead Source System

**Goal:** Normalize attribution and partner relationships through master data.

#### 21.3.1 Conceptual DocTypes (placeholders)

| DocType | Purpose | Key relationships |
|---------|---------|-------------------|
| **Lead Source** | Canonical channel (e.g. `agri_dept`, `sugar_mill`, `vip_referral`) | → Lead Category; used on Lead and Farmer Project |
| **Lead Category** | Grouping for reporting (govt, partner, customer, institutional, retail) | ← Lead Source (many-to-one or tags) |
| **Referral Partner** | Repeatable referrer org/person (mill, dept office, VIP) | → External Contact; optional commission flag (future) |
| **External Contact** | Named individual outside the dealer (officer, mill staff) | → Referral Partner optional; → Block/District scope |
| **Institutional Contact** | Org-level contact (FPO, estate, corporate) | → Institutional lead type |
| **Project Type** | Defines workflow template and billing pattern | → stage template set; see §21.4 |

*All enumerations (source codes, categories) ship as **fixtures**, not enums in Dart/Python.*

#### 21.3.2 Field placement strategy (minimal future schema)

When implemented, prefer **links over duplication**:

- `Lead` → `lead_source`, `lead_category`, `referral_partner`, `external_contact`, `project_type` (intended), `block`, `village`, `district`
- `Farmer Project` → copy `lead_source` + `referral_partner` at conversion (immutable snapshot for analytics)

#### 21.3.3 API namespace (reserved)

`agriflow.api.v1.lead.*` — list, create, assign, convert (future); not registered in Phase 1.

---

### 21.4 Flexible Project Types

**Goal:** One platform, multiple commercial workflows; **Farmer Project** remains the document type name, differentiated by `project_type`.

#### 21.4.1 Project type placeholders

| Project Type (fixture) | Workflow | Notes |
|------------------------|----------|-------|
| Subsidy Project | 12-stage subsidy lifecycle (§2.4) | Phase 1 default |
| Cash & Carry | Short retail workflow (quote → dispatch → payment) | Links M2, M3; no MIMIS stages |
| Tree Crop Irrigation | Subsidy-like or simplified stages + crop metadata | Crop flags on project |
| AMC | Service-centric stages (M7) | Extends 3-year service model |
| Institutional Project | Bulk sites, multi-farmer linkage (future) | May parent multiple farmers |
| Corporate Irrigation | B2B quotation and milestone billing | Officer network optional |

#### 21.4.2 Stage template pattern

```
Project Type (master)
    └── Project Stage Template (child / fixture)
            └── stage_key, sequence, task_templates[], required_roles[]
```

- **Subsidy** uses existing 12 stages.
- Other types **must not skip** the pattern: sequential stages, history table, `ProjectLifecycleService` with `project_type` parameter.
- Avoid N duplicate DocTypes (e.g. no separate `Cash Carry Project` table)—use `Farmer Project` + `project_type` + template selector.

#### 21.4.3 Mobile UX principle

Timeline screen reads **stage template from project type**; UI stays timeline-first. No new navigation paradigm per type.

---

### 21.5 Referral Intelligence

**Goal:** Architecture hooks for partner performance and future commission—reporting only until business rules are defined.

#### 21.5.1 Tracking model (conceptual)

| Artifact | Purpose |
|----------|---------|
| `Lead.referral_partner` | Attribution at intake |
| `Farmer Project.referral_partner` | Frozen at conversion |
| `Conversion Event` (future log) | lead_id, project_id, converted_at, converted_by |
| `Referral Performance Snapshot` (future report) | Aggregates by partner, source, block, period |

#### 21.5.2 Analytics dimensions (future reports)

- Referral volume and **conversion rate** by `Lead Source` / `Referral Partner`
- Time-to-convert (lead created → stage `lead_captured` or project create)
- **Source performance** by block and project type
- **Partner ecosystem** health (active partners, dormant partners)
- **Commission workflow** (placeholder): optional `commission_rule` on Referral Partner; payout status DocType deferred until finance rules exist

#### 21.5.3 Constraints

- No commission calculation in Phase 1
- Analytics read from MariaDB / Script Reports; no separate warehouse required at current scale
- PII in referral reports follows §18 role scoping

---

### 21.6 Crop-Based Opportunity Tracking

**Goal:** Support future demand analytics (tree crop, plantation, non-subsidy irrigation) without a separate product silo.

#### 21.6.1 Crop metadata (placeholder)

| Concept | Attachment point |
|---------|------------------|
| **Crop Category** (master) | e.g. tree crop, plantation, field crop, sugarcane |
| **Crop Interest** on Lead | Multi-select or primary crop |
| **Crop flags on Farmer Project** | Copied at conversion; drives reporting |

#### 21.6.2 Opportunity types for analytics

| Opportunity | Tracked via |
|-------------|-------------|
| Tree crop irrigation | Lead Category + Crop Category + Project Type `tree_crop_irrigation` |
| Plantation projects | Institutional + crop metadata |
| Non-subsidy irrigation demand | Cash & Carry + crop tags |
| Crop category trends | Owner dashboard (M9 extension): leads and projects by crop × block × month |

#### 21.6.3 Offline and sync

- Crop masters: **server-wins**, cached in Hive like other masters
- Lead crop interests: client-wins on create; LWW on edit

---

### 21.7 Architectural Constraints (Future Expansion)

The following constraints govern **all** §21 work:

| Constraint | Requirement |
|------------|-------------|
| Placeholders only | §21 does not authorize implementation; PRD phase gate + `DOCTYPES.md` update required |
| Phase 1 unchanged | Current modules M1–M9, 12-stage subsidy flow, and Tiruvannamalai scope remain the delivery target |
| No schema overengineering | Implement DocTypes incrementally per phase; start with links + fixtures, not wide denormalized tables |
| No unnecessary code generation | Do not scaffold empty features, APIs, or Drift tables until phase approved |
| Workflow-first | Every `Project Type` uses stage templates + history + tasks—not ad-hoc status fields |
| Offline-first | Leads and conversions obey SyncQueue; geography masters obey server-wins |
| Farmer Project as root | Leads never replace projects; conversion creates or links to Farmer Project |
| MIMIS unchanged | Subsidy types only; Cash & Carry and corporate types bypass MIMIS stages |
| Tamil-first / i18n | New source labels and categories via ARB + fixtures, not hardcoded strings |
| Audit | Conversion and referral attribution changes are audit-logged when implemented |

#### 21.7.1 Phase activation checklist (when a future phase starts)

1. PRD amendment + phase number  
2. Update `DOCTYPES.md` with concrete fields (minimal)  
3. Export fixtures for `Lead Source`, `Project Type`, etc.  
4. Extend `DOCTYPES.md` and §5 API list—version bump if breaking  
5. Add Flutter feature folder only for in-scope UX  
6. Architecture review: confirm invariants §20 still hold  

#### 21.7.2 Explicit non-goals (future phases)

- Separate lead-management mobile app  
- Real-time govt portal integration for leads  
- ML lead scoring (Phase 2 AI remains operational-only per PRD §16)  
- Multi-currency or multi-country (out of scope)

---

## Appendix A — Technology reference

| Layer | Technology | Version |
|-------|------------|---------|
| Backend framework | Frappe | v15 |
| Database | MariaDB | 11 |
| Cache / queue | Redis | 7 |
| Mobile framework | Flutter | 3.24 |
| State management | Riverpod | 2.5 |
| Local DB | Drift + Hive | current stable |
| HTTP | Dio + Retrofit | current stable |
| Routing | go_router | current stable |
| Object storage | MinIO | S3-compatible |
| Orchestration | Docker + Coolify | — |
| Hosting | Hetzner VPS | — |
| Messaging | Evolution API | WhatsApp (optional) |

---

## Appendix B — Document maintenance

| Trigger | Action |
|---------|--------|
| New DocType | Update `DOCTYPES.md` |
| New API method | Update §5 and `DOCTYPES.md` |
| New design token | Update `UI_TOKENS.md` |
| Stage workflow change | Update §2.4, fixtures, and invariants |
| Breaking API change | Increment version namespace; update `min_mobile_version` |
| Future expansion phase approved | Update §21, `DOCTYPES.md`, PRD; implement only scoped placeholders |
| New district / lead source | Fixtures + User Permissions; no hardcoded geography (§21.1) |

**Review cadence:** architecture review at each phase gate (PRD development phases).

---

*End of ARCHITECTURE.md*
