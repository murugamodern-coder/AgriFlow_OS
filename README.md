# AgriFlow OS

**Agriculture operations platform for irrigation subsidy dealers in Tamil Nadu.**

AgriFlow OS is a workflow-first, offline-first system that helps dealer teams track farmer subsidy projects from lead capture through subsidy release—without losing follow-ups, documents, or profit visibility in the field.

| | |
|---|---|
| **Status** | Phase 1 — specification complete; application scaffolding per [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) |
| **Primary users** | ~15 staff across 12 blocks (Tiruvannamalai District) |
| **North-star entity** | **Farmer Project** (12-stage sequential lifecycle) |
| **Documentation** | Product and engineering specs in this repository (see [Documentation index](#documentation-index)) |

---

## Table of contents

1. [Project overview](#1-project-overview)  
2. [Vision summary](#2-vision-summary)  
3. [Key architecture principles](#3-key-architecture-principles)  
4. [Monorepo structure](#4-monorepo-structure)  
5. [Technology stack](#5-technology-stack)  
6. [Required software](#6-required-software)  
7. [Local development setup](#7-local-development-setup)  
8. [Backend setup overview](#8-backend-setup-overview)  
9. [Flutter setup overview](#9-flutter-setup-overview)  
10. [Environment variables overview](#10-environment-variables-overview)  
11. [Folder structure explanation](#11-folder-structure-explanation)  
12. [Documentation index](#12-documentation-index)  
13. [Implementation roadmap summary](#13-implementation-roadmap-summary)  
14. [Development workflow](#14-development-workflow)  
15. [Git branch strategy](#15-git-branch-strategy)  
16. [Coding standards summary](#16-coding-standards-summary)  
17. [Offline-first philosophy](#17-offline-first-philosophy)  
18. [Timeline-first UX philosophy](#18-timeline-first-ux-philosophy)  
19. [Sync engine philosophy](#19-sync-engine-philosophy)  
20. [Deployment overview](#20-deployment-overview)  
21. [Security expectations](#21-security-expectations)  
22. [Contribution guidelines](#22-contribution-guidelines)  
23. [Cursor AI usage rules](#23-cursor-ai-usage-rules)  
24. [Future expansion philosophy](#24-future-expansion-philosophy)  
25. [Phase 1 scope disclaimer](#25-phase-1-scope-disclaimer)  

---

## 1. Project overview

AgriFlow OS supports **irrigation subsidy dealer operations** in Tamil Nadu: farmer registration, government scheme workflow (including MIMIS tracking via Excel reconciliation), field surveys, inventory across two godowns, expenses, and owner-level profit visibility.

The platform is built for **real field conditions**—patchy mobile connectivity, Tamil-speaking staff, and the need for a single trustworthy timeline per farmer project.

**Business lines (Phase 1 focus)**

| Line | Phase 1 |
|------|---------|
| Subsidy projects | Primary — full 12-stage workflow |
| Cash & carry / machinery | Documented for future; not Phase 1 delivery |

**What this repository is today**

- Authoritative **product and engineering specifications** (PRD, architecture, DocTypes, APIs, UI tokens, implementation plan).  
- Target **monorepo layout** for Frappe backend + Flutter mobile (see [§4](#4-monorepo-structure)). Application directories will appear as implementation phases complete.

---

## 2. Vision summary

> **Nothing gets forgotten. Everything gets tracked. Profit becomes visible.**

AgriFlow OS is an **operational memory system** for agriculture businesses—not a generic billing or ERP replacement.

| Goal | How |
|------|-----|
| End workflow chaos | One sequential 12-stage lifecycle per subsidy project |
| Stop follow-up failure | Task engine + timeline visibility |
| Surface profit | Expense tracking and owner dashboards |
| Support field work | Offline-first mobile with explicit sync status |
| Respect local language | Tamil-first UI via i18n (English supported) |
| Preserve accountability | Audit logs, officer assignment history, stage history |

---

## 3. Key architecture principles

| Principle | Meaning |
|-----------|---------|
| **Workflow-first** | Operations revolve around **Farmer Project** stages |
| **Offline-first** | Writes go to a local queue first; server reconciles when online |
| **Timeline-first** | Project timeline is the primary operational screen |
| **Tamil-first** | Default locale and typography tuned for Tamil readability |
| **Role-based** | Field, office, store, installer, service, and owner see scoped data |
| **Master-data driven geography** | District → Block → Cluster → Village — no hardcoded blocks |
| **Server-authoritative stages** | Stage transitions validated only on the server |
| **MIMIS via Excel only** | No government portal recreation; reconciliation imports only |
| **Normalized schema** | Avoid parallel DocTypes per project type in Phase 1 |
| **No Phase 1 AI** | Operational AI deferred per PRD |

Full detail: [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 4. Monorepo structure

Single repository containing backend app, mobile app, infrastructure definitions, and documentation.

```
AgriFlow_OS/
├── apps/agriflow/              # Frappe custom app (target)
├── mobile/agriflow_mobile/     # Flutter app (target)
├── packages/                   # Shared templates / contracts (target)
├── infra/                      # Docker, Coolify, site config (target)
├── scripts/                    # Seed and tooling (target)
├── docs/                       # Optional doc mirror (specs may live at root)
├── PRD.md                      # Product requirements
├── ARCHITECTURE.md             # System architecture
├── DOCTYPES.md                 # Data model specification
├── API_CONTRACTS.md            # REST API contracts (v1)
├── UI_TOKENS.md                # Design system tokens
├── IMPLEMENTATION_PLAN.md      # Phased delivery roadmap
├── README.md                   # This file
└── .cursorrules                # Cursor AI project rules
```

**Ownership**

| Path | Team | Notes |
|------|------|-------|
| `apps/agriflow/` | Backend | DocTypes, services, APIs, fixtures |
| `mobile/agriflow_mobile/` | Mobile | Features, sync, UI |
| `infra/` | DevOps | Compose, deployment |
| Spec `*.md` at root | Product + engineering | Change via PR with linked code |

---

## 5. Technology stack

| Layer | Technology |
|-------|------------|
| Backend framework | [Frappe](https://frappeframework.com/) v15 |
| Database | MariaDB 11 |
| Cache / queues | Redis 7 |
| Object storage | MinIO (S3-compatible) |
| Mobile | Flutter 3.24 |
| State management | Riverpod 2.5 |
| Local storage | Hive (masters) + Drift (entities + SyncQueue) |
| HTTP | Dio (+ Retrofit when adopted) |
| Routing | go_router |
| API style | REST — Frappe whitelisted methods, versioned `v1` |
| Hosting | Docker on Hetzner, orchestrated with Coolify |
| TLS | Caddy |
| Backups | Backblaze B2 (target) |

---

## 6. Required software

Install before local development once scaffolding exists. Versions are **minimum targets** from the PRD and architecture specs.

| Tool | Purpose |
|------|---------|
| Git | Version control |
| Docker Desktop or Docker Engine + Compose | Local MariaDB, Redis, Frappe, MinIO |
| Python 3.10+ | Frappe / bench ecosystem |
| Node.js 18+ | Frappe asset builds (as required by bench) |
| Flutter SDK 3.24.x | Mobile app |
| Android Studio or Xcode | Device emulators |
| Cursor or VS Code | Editor (optional; Cursor rules in `.cursorrules`) |

**References (external)**

- Frappe installation: [Frappe Framework docs](https://docs.frappe.io/framework)  
- Flutter installation: [Flutter docs](https://docs.flutter.dev/get-started/install)  

Detailed bench and device setup steps will live in `infra/` and phase guides inside [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) as those directories are added—do not assume commands in this README until those guides exist.

---

## 7. Local development setup

### 7.1 Onboarding sequence (recommended)

1. Read [PRD.md](./PRD.md) and [ARCHITECTURE.md](./ARCHITECTURE.md) (executive sections).  
2. Clone this repository.  
3. Complete [Phase 2–4](./IMPLEMENTATION_PLAN.md#phase-2--monorepo-setup) from the implementation plan (monorepo scaffold, backend bench, Flutter shell).  
4. Configure environment variables (§10) from `.env.example` when provided under `infra/`.  
5. Start local stack via Docker Compose when `infra/docker/` is available.  
6. Run backend health check (`ping` API per [API_CONTRACTS.md](./API_CONTRACTS.md)).  
7. Run Flutter app against dev site URL.

### 7.2 Current repository state

If `apps/` and `mobile/` are not yet present, the project is in the **documentation-first** gate. Implement [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) Phase 2 before expecting runnable services.

### 7.3 Environments

| Environment | Use |
|-------------|-----|
| **dev** | Local Docker + emulators |
| **staging** | Coolify on Hetzner; UAT |
| **prod** | Live dealer operations |

See [IMPLEMENTATION_PLAN.md §17](./IMPLEMENTATION_PLAN.md#17-dev--staging--prod-environments).

---

## 8. Backend setup overview

The backend is a **single Frappe custom app** named `agriflow` with modules aligned to PRD areas (Farmer Registry, Project Lifecycle, Task Engine, Inventory, MIMIS Sync, Officer Network, Profit).

**Responsibilities**

- DocTypes and business rules per [DOCTYPES.md](./DOCTYPES.md)  
- Versioned APIs under `agriflow.api.v1.*` per [API_CONTRACTS.md](./API_CONTRACTS.md)  
- `ProjectLifecycleService` for sequential 12-stage transitions  
- Background jobs (task generation, MIMIS import, profit snapshots)  
- JWT authentication for mobile; Frappe roles and User Permissions for scope  

**Local backend (when scaffolded)**

1. Start dependencies (MariaDB, Redis) via project Docker Compose.  
2. Install or attach Frappe bench with `apps/agriflow` mounted.  
3. Create dev site; run migrations; import fixtures.  
4. Start web, worker, and scheduler processes.  

Concrete commands and compose file names will be documented in `infra/docker/README.md` during Phase 3—not duplicated here to avoid stale instructions.

---

## 9. Flutter setup overview

The mobile app **`agriflow_mobile`** uses **feature-first** layout under `lib/features/{feature}/` with shared `core/` and `shared/`.

**Responsibilities**

- Tamil-first UI using design tokens from [UI_TOKENS.md](./UI_TOKENS.md)  
- Offline SyncQueue (Drift) and master cache (Hive)  
- Riverpod state; go_router navigation only  
- Role-based shells (field, office, store, owner)  

**Local mobile (when scaffolded)**

1. Install Flutter SDK matching `pubspec` constraint (3.24.x).  
2. From `mobile/agriflow_mobile/`, resolve dependencies and run code generation for Drift/Riverpod as documented in that package README.  
3. Configure dev API base URL (environment / dart-define).  
4. Run on emulator or device; verify login and sync chip.  

Feature screens are built **after** corresponding backend APIs exist ([IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) — backend before screens).

---

## 10. Environment variables overview

Secrets **must not** be committed. Use `.env` locally and Coolify secrets in deployed environments.

| Variable (conceptual) | Component | Description |
|---------------------|-----------|-------------|
| `SITE_URL` | Mobile, desk | Frappe site base URL |
| `JWT_SECRET` / signing keys | Backend | Token signing |
| `DB_HOST`, `DB_NAME`, `DB_PASSWORD` | Backend | MariaDB |
| `REDIS_URL` | Backend | Cache and job queues |
| `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET` | Backend | File storage |
| `MIN_MOBILE_VERSION` | Backend | Force upgrade gate |
| `SENTRY_DSN` (optional) | Mobile, backend | Error reporting |

An `.env.example` will be added under `infra/` during implementation. Until then, treat this table as the contract for ops setup.

---

## 11. Folder structure explanation

| Path | Contents |
|------|----------|
| **`apps/agriflow/`** | Frappe app: `api/`, `services/`, DocType JSON, `fixtures/`, `patches/` |
| **`mobile/agriflow_mobile/lib/app/`** | Bootstrap, router, app widget |
| **`mobile/.../lib/core/`** | Design tokens, network, database, sync, i18n |
| **`mobile/.../lib/features/`** | `auth`, `farmer_registry`, `project_lifecycle`, `tasks`, `inventory`, `mimis_sync`, etc. |
| **`mobile/.../assets/i18n/`** | ARB files (`en`, `ta`) |
| **`packages/excel_templates/`** | Versioned MIMIS Excel templates |
| **`infra/docker/`** | Compose stacks for dev and production-shaped local |
| **`infra/coolify/`** | Deployment manifests |
| **`scripts/seed/`** | Bench seed and fixture helpers |
| **Root `*.md`** | Authoritative specifications (Phase 1) |

---

## 12. Documentation index

Read in this order for new engineers:

| Document | Purpose |
|----------|---------|
| [PRD.md](./PRD.md) | Product vision, roles, 12 stages, modules, constraints |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, sync, RBAC, deployment, future expansion (§21) |
| [DOCTYPES.md](./DOCTYPES.md) | Frappe DocType fields, validation, permissions, indexes |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | REST v1 endpoints, envelopes, offline protocol |
| [UI_TOKENS.md](./UI_TOKENS.md) | Colors, typography, timeline UI, components |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Phased build order, QA, release, Cursor guidelines |
| [.cursorrules](./.cursorrules) | Mandatory stack and conventions for AI-assisted coding |

**Rule:** Schema, API, or token changes require updating the matching spec in the same change set as code (when code exists).

---

## 13. Implementation roadmap summary

Phase 1 delivery (~16–22 weeks for a small team) follows [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md).

| Order | Phase | Outcome |
|-------|-------|---------|
| 1 | Monorepo + backend foundation | Bench, app shell, API envelope |
| 2 | Flutter foundation | Tokens, router, Drift/Hive skeleton |
| 3 | Authentication | JWT + role manifest |
| 4 | Geography masters | 12 blocks, officers, fixtures |
| 5 | Farmer module | Registry CRUD |
| 6 | **Farmer Project** | Aggregate root + lifecycle service |
| 7 | **Timeline engine** | Primary UX milestone |
| 8 | Task engine | Follow-ups + templates |
| 9 | **Offline sync** | `sync.push` / `pull` — critical infrastructure |
| 10 | Inventory, expense, MIMIS | P1 operational modules |
| 11 | UI polish + QA + prod | Go-live |

**Critical path:** Geography → Farmer Project → Timeline → Sync.

---

## 14. Development workflow

| Practice | Detail |
|----------|--------|
| Spec-first | DOCTYPES + API_CONTRACTS updated before or with implementation |
| Vertical slices | Ship end-to-end thin features every 2–3 weeks |
| Backend before screens | API smoke-tested before Flutter business UI |
| PR reviews | Architecture-sensitive changes need explicit review (sync, stages, MIMIS) |
| UAT | Owner validates Tamil copy, geography fixtures, and stage flow |
| Definition of done | Phase validation checklist in implementation plan |

Ceremonies and roles: [IMPLEMENTATION_PLAN.md §27](./IMPLEMENTATION_PLAN.md#27-team-workflow).

---

## 15. Git branch strategy

```
main     ← production releases (tagged)
develop  ← integration branch
feat/*   ← features
fix/*    ← bugfixes
release/*← release candidates
```

- Pull requests required into `develop`.  
- `main` updated only from tested `release/*` branches.  
- Conventional commits encouraged: `feat:`, `fix:`, `docs:`, `chore:`.  
- No force-push to `main`.

Full policy: [IMPLEMENTATION_PLAN.md §28](./IMPLEMENTATION_PLAN.md#28-git-branch-strategy).

---

## 16. Coding standards summary

From [.cursorrules](./.cursorrules) and architecture specs:

| Area | Standard |
|------|----------|
| Flutter layout | `lib/features/{feature}/` — feature-first |
| State | Riverpod only |
| Navigation | go_router only |
| Colors / spacing | Design tokens from UI_TOKENS — **never hardcode hex** |
| Strings | i18n ARB — **never hardcode Tamil** in source |
| Backend | Frappe DocTypes + fixtures; snake_case fields |
| DocType names | Title Case; API namespace `agriflow.api.v1` |
| Aggregate root | Farmer Project; transitions via service only |
| Officer history | Append-only |
| MIMIS | Excel reconciliation only |
| Comments | Only where business logic is non-obvious |
| AI features | None in Phase 1 |

---

## 17. Offline-first philosophy

Field staff in rural Tamil Nadu cannot rely on continuous connectivity.

| Layer | Behavior |
|-------|----------|
| **Read** | Drift + Hive serve data immediately |
| **Write** | Append to **SyncQueue** first; flush via `sync.push` when online |
| **Masters** | Geography and catalog: server wins on pull |
| **Creates** | Client wins with `client_id` idempotency |
| **Updates** | Last-write-wins with `doc_version` |
| **Stage change** | Server authoritative — stale transitions refresh timeline |

Sync status must remain **visible** in the app chrome (pending count, errors). Details: [ARCHITECTURE.md §4](./ARCHITECTURE.md#4-sync-engine-architecture), [API_CONTRACTS.md §8](./API_CONTRACTS.md#8-offline-sync-protocol).

---

## 18. Timeline-first UX philosophy

The **Farmer Project detail screen** centers on a vertical **stage timeline** (completed / current / future), not ERP tabs or dense forms.

- ≥50% of screen emphasis on timeline (see UI_TOKENS).  
- One primary action: advance to **next allowed stage** or complete the blocking task.  
- Stage labels via i18n (`project.stage.*`).  
- Muted stage accents — clarity over twelve loud colors.  

Inspired by operational clarity in Linear and Notion; financial simplicity in Khatabook; confident CTAs in PhonePe—without copying consumer-payment patterns.

---

## 19. Sync engine philosophy

The sync engine is **critical infrastructure**, not a bolt-on.

- Modeled as an **outbox** (`SyncQueue` on device; `sync.push` on server).  
- Operations ordered per **Farmer Project** to protect stage integrity.  
- Conflicts return structured payloads (`stale_transition`, `lww_version_mismatch`) for deterministic UI.  
- MIMIS Excel import is **outside** the queue (online-only batch jobs).  

Treating sync as optional guarantees field data loss and support churn—Phase 11 in the implementation plan is a hard gate before production.

---

## 20. Deployment overview

| Component | Target |
|-----------|--------|
| Compute | Hetzner VPS |
| Orchestration | Coolify |
| TLS | Caddy (Let's Encrypt) |
| App | Frappe (Gunicorn) + workers + scheduler |
| Data | MariaDB, Redis, MinIO |
| Backups | Daily to Backblaze B2 |
| Mobile | Android internal / Play track (phased staff rollout) |

Milestones: [IMPLEMENTATION_PLAN.md §18](./IMPLEMENTATION_PLAN.md#18-docker--coolify-deployment-milestones). Topology: [ARCHITECTURE.md §17](./ARCHITECTURE.md#17-deployment-topology).

---

## 21. Security expectations

| Topic | Expectation |
|-------|-------------|
| Transport | HTTPS everywhere in non-local environments |
| Auth | JWT access + refresh; short TTL; rotation |
| Authorization | Frappe roles + User Permissions (block scope); server re-validates every API |
| Audit | Stage transitions, MIMIS approvals, stock, expenses logged |
| PII | Minimal storage (e.g. Aadhaar last 4 only); mask mobile in lists |
| Files | MIME and size allowlists |
| Secrets | Environment / Coolify only — never in git |
| Dependencies | Scan in CI when pipeline exists |

Checklist: [IMPLEMENTATION_PLAN.md §21](./IMPLEMENTATION_PLAN.md#21-security-checklist).

---

## 22. Contribution guidelines

1. **Open a PR** against `develop` with a clear description and phase reference.  
2. **Update specs** if you change DocTypes, APIs, tokens, or invariants.  
3. **Keep scope minimal** — no drive-by refactors.  
4. **Test** — lifecycle transitions, permissions, and sync paths for touched features.  
5. **Tamil** — add/update ARB keys; request native review for user-visible Tamil.  
6. **No new dependencies** without brief justification in PR.  
7. **Do not implement** ARCHITECTURE §21 future features (leads, SaaS, extra project types) unless explicitly scheduled.

Questions on product intent: see PRD. Questions on structure: see ARCHITECTURE.

---

## 23. Cursor AI usage rules

Cursor is a productivity tool, not a source of truth.

| Do | Don't |
|----|-------|
| Attach PRD, DOCTYPES, API_CONTRACTS for context | Invent fields, stages, or endpoints |
| Generate code matching `.cursorrules` | Hardcode Tamil or colors |
| One feature per session with acceptance criteria | Bypass SyncQueue for mobile writes |
| Run analyzer/tests after generated changes | Add AI/chatbot features (Phase 1) |
| Update docs in the same PR as schema changes | Implement lead ecosystem (§21) early |

Full guide: [IMPLEMENTATION_PLAN.md §29](./IMPLEMENTATION_PLAN.md#29-cursor-ai-usage-guidelines).

---

## 24. Future expansion philosophy

Phase 1 is intentionally narrow. [ARCHITECTURE.md §21](./ARCHITECTURE.md#21-future-expansion-architecture) documents **placeholders only** for:

- Multi-district and Tamil Nadu–scale geography  
- Lead sources (VIP, departments, mills, institutional, tree crop, cash & carry enquiries)  
- Additional **project types** (cash & carry, AMC, corporate irrigation)  
- Referral analytics and commission workflows  

**Farmer Project remains the aggregate root** when those phases arrive. Extension is via master data, fixtures, and links—not parallel apps or duplicate workflows.

---

## 25. Phase 1 scope disclaimer

This repository and Phase 1 delivery **do not** include:

- AI features (OCR, chatbots, forecasting) — deferred per PRD §16  
- Recreation of the **MIMIS government portal** or live government APIs  
- Multi-tenant SaaS or multi-dealer hosting  
- Farmer-facing consumer app  
- Dark mode (reserved Phase 2 in UI_TOKENS)  
- Lead capture module (documented only in ARCHITECTURE §21)  
- Guaranteed production infrastructure in-repo until `infra/` is implemented  

What Phase 1 **does** commit to: a dependable **12-stage subsidy workflow**, **offline-capable mobile** operations for ~15 users across **12 blocks** in **Tiruvannamalai**, with **auditability**, **MIMIS Excel reconciliation**, **inventory (2 godowns)**, and **expense/profit visibility** for the owner.

If a capability is not described in the indexed documents above, assume it is **out of scope** until the PRD and implementation plan are formally amended.

---

## License and contact

License and maintainer contact details to be added when the operating entity confirms distribution terms.

---

**AgriFlow OS** — operational memory for agriculture businesses.
