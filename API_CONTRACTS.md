# AgriFlow OS — API Contracts (Phase 1)

**Version:** 1.0  
**API version:** `v1`  
**Status:** Phase 1 specification (documentation only)  
**Last updated:** 2026-05-20  

**Related documents:** [PRD.md](./PRD.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [DOCTYPES.md](./DOCTYPES.md) · [.cursorrules](./.cursorrules)

---

## Document purpose

This document defines **REST-style HTTP contracts** for AgriFlow OS mobile and integrators. All Phase 1 business APIs are implemented as **Frappe whitelisted methods** under a versioned namespace. No GraphQL. No application code in this file.

**Transport:** HTTPS only · JSON request/response bodies · UTF-8 · Tamil display strings via i18n keys in payloads where applicable.

---

## Table of contents

### Foundations (1–14)

1. [API philosophy](#1-api-philosophy)  
2. [Versioning strategy](#2-versioning-strategy)  
3. [Authentication flow](#3-authentication-flow)  
4. [JWT structure](#4-jwt-structure)  
5. [Request/response envelope](#5-requestresponse-envelope)  
6. [Error response schema](#6-error-response-schema)  
7. [Idempotency strategy](#7-idempotency-strategy)  
8. [Offline sync protocol](#8-offline-sync-protocol)  
9. [Delta sync strategy](#9-delta-sync-strategy)  
10. [Pagination standards](#10-pagination-standards)  
11. [Filtering standards](#11-filtering-standards)  
12. [File upload protocol](#12-file-upload-protocol)  
13. [Batch sync format](#13-batch-sync-format)  
14. [Conflict resolution response format](#14-conflict-resolution-response-format)  

### Domain APIs (15–22)

15. [Timeline API contracts](#15-timeline-api-contracts)  
16. [Task API contracts](#16-task-api-contracts)  
17. [Farmer API contracts](#17-farmer-api-contracts)  
18. [Farmer Project API contracts](#18-farmer-project-api-contracts)  
19. [Geography master APIs](#19-geography-master-apis)  
20. [MIMIS reconciliation APIs](#20-mimis-reconciliation-apis)  
21. [Inventory APIs](#21-inventory-apis)  
22. [Expense APIs](#22-expense-apis)  

### Operations (23–27)

23. [Audit / event hooks](#23-audit--event-hooks)  
24. [Rate limiting guidelines](#24-rate-limiting-guidelines)  
25. [API security rules](#25-api-security-rules)  
26. [Mobile compatibility strategy](#26-mobile-compatibility-strategy)  
27. [Future extensibility considerations](#27-future-extensibility-considerations)  

---

## 1. API philosophy

| Principle | Contract implication |
|-----------|------------------------|
| **Workflow-first** | Farmer Project APIs dominate; reads optimized for timeline and stage actions |
| **Offline-first** | Mutations queue locally; `sync.push` is the primary write path for field data |
| **Aggregate root** | `project.transition` is the only stage authority; no direct stage PATCH |
| **Thin controllers** | APIs validate, authorize, delegate to services (`ProjectLifecycleService`, etc.) |
| **Consistent envelopes** | Every response uses the same top-level shape (§5) |
| **Role-aware by default** | Lists auto-scope to User Permissions; explicit filters cannot widen scope |
| **Idempotent creates** | Mobile never relies on retry luck — `client_id` required on creates |
| **Correlation** | `X-Request-ID` on every call for support and audit linkage |
| **Master vs transactional** | Geography/inventory masters: server-wins pull; entities: push + LWW |

**What we avoid**

- GraphQL, ad-hoc per-screen endpoints, fat payloads with unbounded joins  
- Client-direct Frappe CRUD from mobile (bypasses RBAC and sync rules)  
- Real-time MIMIS government APIs (Excel reconciliation only)

---

## 2. Versioning strategy

### 2.1 URL namespace

```
https://{site}/api/method/agriflow.api.{version}.{area}.{action}
```

| Segment | Value (Phase 1) |
|---------|-----------------|
| `{version}` | `v1` |
| `{area}` | `auth`, `sync`, `project`, `farmer`, `task`, `master`, `file`, `mimis`, `inventory`, `expense`, `audit` |
| `{action}` | verb snake_case matching method name |

**Example**

```
POST https://agriflow.example.com/api/method/agriflow.api.v1.project.transition
```

### 2.2 Breaking vs non-breaking changes

| Change type | Version bump |
|-------------|--------------|
| New optional response field | No bump |
| New endpoint | No bump |
| Removed field, renamed field, changed enum meaning | **v2** |
| Changed conflict rules or stage sequence | **v2** + PRD amendment |

### 2.3 Client headers

| Header | Required | Purpose |
|--------|----------|---------|
| `Authorization` | Yes* | `Bearer {access_token}` |
| `Content-Type` | Yes (JSON) | `application/json` except file upload |
| `X-AgriFlow-Client-Version` | Yes | App build (e.g. `1.0.0+12`) |
| `X-AgriFlow-Platform` | Yes | `android`, `ios` |
| `X-Request-ID` | Recommended | UUID v4; server echoes in response |
| `Accept-Language` | Optional | `ta`, `en` — affects `error.message` locale |

\*Except `auth.login`.

### 2.4 Site configuration

Server exposes (via `auth.permissions` or site config endpoint):

```json
{
  "min_mobile_version": "1.0.0",
  "api_version": "v1",
  "supported_entities": ["farmer", "farmer_project", "task", "expense"]
}
```

---

## 3. Authentication flow

```
┌────────┐    credentials     ┌─────────────┐    JWT pair    ┌────────┐
│ Mobile │ ─────────────────► │ auth.login  │ ─────────────► │ Secure │
└────────┘                    └─────────────┘                │ storage│
     │                              │                        └────────┘
     │  Bearer access_token         │
     ▼                              ▼
┌────────────┐   401/expired   ┌──────────────┐
│ Business   │ ◄────────────── │ auth.refresh │
│ API calls  │ ──────────────► └──────────────┘
└────────────┘
```

| Step | Action |
|------|--------|
| 1 | Mobile posts `auth.login` with username/password (or API key in desk-only tools) |
| 2 | Server returns `access_token`, `refresh_token`, `user`, `permissions` manifest |
| 3 | Mobile stores tokens in secure storage; caches permissions in Hive |
| 4 | All APIs send `Authorization: Bearer {access_token}` |
| 5 | On `401` + `AUTH_TOKEN_EXPIRED`, call `auth.refresh` once; retry original request |
| 6 | On refresh failure, redirect to login |
| 7 | `auth.logout` invalidates refresh token server-side |

Desk (Frappe) users may use standard session cookies — **out of scope** for mobile contracts.

---

## 4. JWT structure

Phase 1 uses **signed JWT** (HS256 or RS256 — deployment choice). Claims below are logical; exact signing config lives in server deployment docs.

### 4.1 Access token claims

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User ID (`usr` name) |
| `iss` | string | `agriflow/{site}` |
| `aud` | string | `agriflow-mobile` |
| `exp` | number | Expiry epoch (15–60 min from issue) |
| `iat` | number | Issued at |
| `jti` | string | Unique token id |
| `roles` | string[] | Frappe role names |
| `districts` | string[] | Allowed district codes (User Permission) |
| `blocks` | string[] | Allowed block codes |

### 4.2 Refresh token claims

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User ID |
| `exp` | number | 7–30 days |
| `type` | string | `refresh` |
| `family_id` | string | Rotation family for reuse detection |

### 4.3 Token response (login / refresh)

Returned inside envelope `data` (see §5).

---

## 5. Request/response envelope

### 5.1 Request body (JSON methods)

```json
{
  "data": { }
}
```

Frappe whitelisted methods receive `data` as the parsed payload. Query parameters are **not** used for complex filters — use JSON body.

### 5.2 Success response

```json
{
  "ok": true,
  "data": { },
  "error": null,
  "server_time": "2026-05-20T10:15:30.123Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5.3 HTTP status mapping

| HTTP | When |
|------|------|
| 200 | `ok: true` |
| 400 | Validation (`VAL_*`) |
| 401 | Auth (`AUTH_*`) |
| 403 | Permission (`PERM_*`) |
| 404 | Not found |
| 409 | Sync conflict (`SYNC_*`) |
| 422 | Business rule violation |
| 429 | Rate limited |
| 500 | Server (`SRV_*`) |

---

## 6. Error response schema

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "SYNC_STALE_TRANSITION",
    "message": "Project stage has changed on server. Refresh timeline.",
    "message_i18n_key": "error.sync.stale_transition",
    "details": {
      "field": "target_stage",
      "server_stage": "field_survey",
      "server_doc_version": 12,
      "client_doc_version": 11
    }
  },
  "server_time": "2026-05-20T10:15:30.123Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 6.1 Error code catalog (Phase 1)

| Code | HTTP | Prefix |
|------|------|--------|
| `AUTH_INVALID_CREDENTIALS` | 401 | AUTH |
| `AUTH_TOKEN_EXPIRED` | 401 | AUTH |
| `AUTH_TOKEN_INVALID` | 401 | AUTH |
| `AUTH_REFRESH_REUSED` | 401 | AUTH |
| `PERM_DENIED` | 403 | PERM |
| `PERM_SCOPE_BLOCK` | 403 | PERM |
| `VAL_REQUIRED_FIELD` | 400 | VAL |
| `VAL_INVALID_STAGE` | 400 | VAL |
| `VAL_DUPLICATE_ACTIVE_PROJECT` | 422 | VAL |
| `NOT_FOUND` | 404 | — |
| `SYNC_STALE_TRANSITION` | 409 | SYNC |
| `SYNC_CONFLICT_LWW` | 409 | SYNC |
| `SYNC_PARTIAL_FAILURE` | 207* | SYNC |
| `SYNC_UNKNOWN_ENTITY` | 400 | SYNC |
| `MIMIS_INVALID_TEMPLATE` | 400 | MIMIS |
| `MIMIS_DUPLICATE_BATCH` | 409 | MIMIS |
| `SRV_INTERNAL` | 500 | SRV |

\*`207` used only for `sync.push` when batch partially succeeds; envelope still returned with per-op results.

---

## 7. Idempotency strategy

| Operation | Key | Server behavior on duplicate |
|-----------|-----|------------------------------|
| Create (farmer, project, task, expense) | `client_id` (UUID v4) | Return existing document; `ok: true`, same `name` |
| `sync.push` op | `op_id` (UUID per queue row) | Skip if `op_id` already applied |
| `project.transition` | `client_id` on transition request | Same transition not applied twice |
| MIMIS upload | `file_hash` (SHA-256) | Reject or return existing batch |
| File upload | `client_id` | Return existing `file_id` |

**Storage:** Server table `AgriFlow Idempotency Key` (`client_id`, `doctype`, `name`, `created_at`).

**Mobile rule:** Generate `client_id` at queue insert time; never regenerate on retry.

---

## 8. Offline sync protocol

### 8.1 Principles

1. **Reads:** Hive (masters) + Drift (entities); refresh via `sync.pull` and entity list APIs when online.  
2. **Writes:** Drift `SyncQueue` first → `sync.push` when connected.  
3. **No silent bypass:** Mobile must not call `project.transition` directly while queue has pending ops for same project (client-side ordering).  
4. **MIMIS / bulk import:** Online-only; not queued in SyncQueue.

### 8.2 Sync sequence (typical)

```
1. auth.login → permissions manifest
2. sync.pull (masters) → Hive
3. sync.pull (entities, modified_since) → Drift
4. [offline work → SyncQueue]
5. sync.push → reconcile Drift + idempotency map
6. sync.pull (entities) → catch server-side changes
```

### 8.3 Entity sync classification

| Entity | Push | Pull | Conflict policy |
|--------|------|------|-----------------|
| District, Block, Cluster, Village, Officer | — | ✓ | Server wins |
| Farmer | ✓ | ✓ | Create: client; Update: LWW |
| Farmer Project | ✓ | ✓ | Transition: server; Other fields: LWW |
| Task | ✓ | ✓ | LWW |
| Expense Entry | ✓ | ✓ | Create: client; Update: LWW |
| Stock Entry | ✓ (Store Keeper) | ✓ | Server validates stock |
| MIMIS Batch | — | read status | Online only |

---

## 9. Delta sync strategy

### 9.1 `modified_since`

- ISO 8601 UTC with milliseconds: `2026-05-20T04:30:00.000Z`
- Stored per entity family in Drift `sync_metadata` after successful pull
- Server compares against document `modified` (Frappe) or custom `last_synced_at`

### 9.2 `sync.pull` request

```json
{
  "data": {
    "entities": ["farmer", "farmer_project", "task"],
    "modified_since": {
      "farmer": "2026-05-20T04:30:00.000Z",
      "farmer_project": "2026-05-20T04:30:00.000Z",
      "task": "2026-05-20T04:30:00.000Z"
    },
    "include_deleted": true
  }
}
```

### 9.3 `sync.pull` response

```json
{
  "ok": true,
  "data": {
    "farmer": { "items": [], "deleted": [], "cursor": null, "has_more": false },
    "farmer_project": { "items": [], "deleted": [], "cursor": null, "has_more": false },
    "task": { "items": [], "deleted": [], "cursor": null, "has_more": false },
    "server_watermark": {
      "farmer": "2026-05-20T10:15:30.000Z",
      "farmer_project": "2026-05-20T10:15:30.000Z",
      "task": "2026-05-20T10:15:30.000Z"
    }
  }
}
```

**Deleted tombstones:** `{ "name": "FR-00042", "is_deleted": true, "modified": "..." }`

### 9.4 Master data pull

Use `master.*` endpoints with same `modified_since` OR full snapshot if watermark null (first login).

---

## 10. Pagination standards

| Parameter | Type | Default | Max |
|-----------|------|---------|-----|
| `limit` | int | 25 | 100 |
| `cursor` | string | null | opaque server token |

**Response pagination meta** (inside `data`):

```json
{
  "items": [],
  "pagination": {
    "limit": 25,
    "cursor": "eyJvZmZzZXQiOjI1fQ==",
    "has_more": true,
    "total_estimate": null
  }
}
```

- Cursor is opaque; do not parse client-side.  
- `total_estimate` optional (expensive queries omit it).

---

## 11. Filtering standards

### 11.1 Geographic filters

| Parameter | Applies to |
|-----------|------------|
| `district` | district code |
| `block` | block code (repeatable array `blocks[]`) |
| `cluster` | cluster code |
| `village` | village code |
| `officer` | officer code |

**Rule:** Filters may only **narrow** results within JWT/User Permission scope. Requesting out-of-scope `block` returns `403 PERM_SCOPE_BLOCK`, not empty list.

### 11.2 Project/task filters

| Parameter | Type |
|-----------|------|
| `current_stage` | stage_key or array |
| `stage_sequence_gte` / `lte` | int |
| `status` | `active`, `on_hold`, `completed`, `cancelled` |
| `assigned_to` | user id |
| `modified_since` | ISO datetime (delta) |
| `farmer` | farmer name id |
| `search` | string (name, mobile, project id) |

### 11.3 Role-aware defaults

| Role | Default scope applied server-side |
|------|-----------------------------------|
| Field Staff | `blocks[]` from JWT |
| Installer | projects stage 9–10 + assigned tasks |
| Store Keeper | inventory APIs only; no farmer list |
| Owner | no extra scope |

---

## 12. File upload protocol

### 12.1 Endpoint

`POST /api/method/agriflow.api.v1.file.upload`  
**Content-Type:** `multipart/form-data`

### 12.2 Form fields

| Field | Required | Description |
|-------|----------|-------------|
| `file` | ✓ | Binary |
| `client_id` | ✓ | UUID |
| `farmer_project` | — | Parent for RBAC |
| `purpose` | — | `stage_attachment`, `task_proof`, `expense_bill` |

### 12.3 Success `data`

```json
{
  "file_id": "FILE-00091",
  "file_url": "/api/method/agriflow.api.v1.file.download?file_id=...",
  "mime_type": "image/jpeg",
  "size_bytes": 204800,
  "client_id": "..."
}
```

### 12.4 Offline behavior

- File saved to app sandbox; SyncQueue operation `file_upload` runs before dependent `project.transition` referencing `attachment_file_id`.

### 12.5 Validation

- Max size: 10 MB image / 25 MB PDF  
- Allowed MIME: `image/jpeg`, `image/png`, `application/pdf`  
- Failures: `VAL_INVALID_FILE`, `PERM_DENIED`

---

## 13. Batch sync format

See API **`sync.push`** (§18 companion) — canonical batch format.

### 13.1 Operation object

```json
{
  "op_id": "uuid",
  "op_type": "create|update|delete",
  "entity": "farmer|farmer_project|task|expense",
  "client_id": "uuid",
  "doc_version": 3,
  "payload": { },
  "depends_on": []
}
```

| Field | Description |
|-------|-------------|
| `op_id` | Unique per queue row |
| `op_type` | Mutation type |
| `entity` | Sync entity family |
| `client_id` | Required for `create` |
| `doc_version` | Required for `update`; LWW check |
| `payload` | Entity fields per DOCTYPES.md |
| `depends_on` | `op_id[]` — must succeed first (e.g. file upload before transition) |

### 13.2 Ordering

- Server processes ops in array order.  
- Ops sharing same `farmer_project` name (or temp client reference) serialized.  
- `depends_on` failure skips dependent ops with `SYNC_DEPENDENCY_FAILED`.

---

## 14. Conflict resolution response format

Returned per operation inside `sync.push` result **or** as top-level error for single-entity APIs.

### 14.1 LWW conflict

```json
{
  "op_id": "uuid",
  "status": "conflict",
  "conflict": {
    "type": "lww_version_mismatch",
    "resolution": "server_payload",
    "server": { "name": "TSK-2026-00124", "doc_version": 5, "modified": "...", "fields": {} },
    "client": { "doc_version": 4 }
  }
}
```

**Mobile action:** Replace local row with `server.fields`; increment local `doc_version`; optional user notification.

### 14.2 Stale stage transition

```json
{
  "op_id": "uuid",
  "status": "conflict",
  "conflict": {
    "type": "stale_transition",
    "resolution": "refresh_timeline",
    "server": {
      "current_stage": "field_survey",
      "stage_sequence": 5,
      "doc_version": 12
    }
  }
}
```

**Mobile action:** Call `project.timeline`; drop queued transition; show UI refresh.

### 14.3 Master overwrite (pull-side)

No conflict object — pull replaces local Hive/Drift master rows unconditionally.

---

## 15. Timeline API contracts

Timeline data is served by **`project.timeline`** (aggregate). Stage history is not mutated via separate public API.

### API: `project.timeline`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.project.timeline` |
| **Method** | `POST` |
| **Purpose** | Single-screen timeline: stage history, open tasks, next allowed transition, permissions |
| **Auth** | Bearer required |

**Request `data`**

```json
{
  "name": "FP-2026-00124",
  "include_completed_tasks": false,
  "task_limit": 10
}
```

| Field | Required | Validation |
|-------|----------|------------|
| `name` | ✓ | Farmer Project id; must be in scope |

**Response `data`**

```json
{
  "project": {
    "name": "FP-2026-00124",
    "farmer": "FR-00042",
    "current_stage": "field_survey",
    "stage_sequence": 5,
    "status": "active",
    "doc_version": 12,
    "block": "BLK01",
    "cluster": "CLU01",
    "village": "VLG001",
    "officer": "OFF01",
    "modified": "2026-05-20T09:00:00.000Z"
  },
  "stage_history": [
    {
      "from_stage": "documents_collected",
      "to_stage": "mimis_registered",
      "from_sequence": 3,
      "to_sequence": 4,
      "transitioned_on": "2026-05-19T14:00:00.000Z",
      "transitioned_by": "user@example.com",
      "notes": "",
      "attachment_file_id": null,
      "is_correction": false
    }
  ],
  "open_tasks": [],
  "workflow": {
    "next_stage": "quotation_generated",
    "next_stage_i18n_key": "project.stage.quotation_generated",
    "can_transition": true,
    "allowed_roles": ["Office Staff"],
    "blocking_reasons": []
  }
}
```

| Sync | Read-only online/offline cache; refresh after `sync.push` or pull |
| Failure | `NOT_FOUND`, `PERM_DENIED` |

---

### API: `project.timeline_since`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.project.timeline_since` |
| **Method** | `POST` |
| **Purpose** | Delta timeline events for offline replay and dashboards (append-only stream) |
| **Auth** | Bearer / session required |

**Request `data`**

```json
{
  "project": "FP-2026-00124",
  "farmer": null,
  "since": "2026-05-20T15:00:00.000Z",
  "event_types": ["stage_transition", "manual_note"],
  "limit": 50,
  "cursor": null
}
```

| Field | Required | Validation |
|-------|----------|------------|
| `project` or `farmer` | One required | Scope anchor |
| `since` | ✓ | ISO 8601; returns events with `created_on > since` |
| `event_types` | No | Subset of timeline event types |
| `limit` | No | Default 50, max 100 |
| `cursor` | No | Raw Timeline Event `name`; keyset on `(created_on, name)` |

**Response `data`**

```json
{
  "items": [],
  "next_cursor": null,
  "has_more": false,
  "generated_at": "2026-05-20T16:30:00.000Z",
  "since": "2026-05-20T15:00:00.000Z",
  "deleted": []
}
```

| Ordering | `created_on ASC, name ASC` (replay-safe) |
| Sync | Mobile watermark per project/farmer; pairs with `sync.pull` in Phase 11 |
| Failure | `NOT_FOUND`, `PERM_DENIED`, `VAL_INVALID` |

**Note:** `project.timeline` response `timeline` block also exposes `items`, `next_cursor`, `has_more`, `generated_at` (newest-first) alongside `stage_history` and `workflow`.

---

## 16. Task API contracts
**Phase 10b updates:** Filters `assigned_officer`, `priority`, `due_before` (alias `due_date_lte`). TaskSummary includes `assigned_officer`, `is_overdue`, `sla`. `task.get` returns `assignment_history`, `timeline_preview`, `sla`, `allowed_transitions`. Priority `medium` accepted as alias for `normal`. `task.complete` supports `assigned` with internal auto-step to `in_progress`.



### API: `task.list`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.task.list` |
| **Method** | `POST` |
| **Purpose** | Paginated task list with role scope |
| **Auth** | Bearer required |

**Request `data`**

```json
{
  "assigned_to": "me",
  "status": ["open", "in_progress"],
  "block": ["BLK01"],
  "farmer_project": null,
  "due_date_lte": "2026-05-25",
  "modified_since": "2026-05-20T00:00:00.000Z",
  "limit": 25,
  "cursor": null
}
```

**Response `data`:** `{ "items": [ TaskSummary ], "pagination": {} }`

**TaskSummary fields:** `name`, `subject`, `farmer_project`, `farmer`, `task_type`, `status`, `priority`, `due_date`, `assigned_to`, `block`, `stage_key`, `doc_version`, `modified`, `client_id`

| Validation | `assigned_to=me` maps to current user; status values from fixture |
| Sync | Pull entity `task`; list for UI refresh |
| Failures | `PERM_DENIED`, invalid cursor → `VAL_INVALID_CURSOR` |

---

### API: `task.get`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.task.get` |
| **Method** | `POST` |
| **Auth** | Bearer required |

**Request:** `{ "name": "TSK-2026-00124" }`  
**Response:** Full task document + checklist items if any.

| Failures | `NOT_FOUND`, `PERM_DENIED` |

---

### API: `task.create`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.task.create` |
| **Method** | `POST` |
| **Purpose** | Manual task creation (auto-tasks created server-side on transition) |
| **Auth** | Bearer; Office Staff+ or Field Staff for own block |

**Request `data`**

```json
{
  "client_id": "uuid",
  "subject": "Follow up document",
  "farmer_project": "FP-2026-00124",
  "task_type": "document",
  "priority": "medium",
  "due_date": "2026-05-22",
  "assigned_to": "user@example.com",
  "description": ""
}
```

| Required | `client_id`, `subject`, `farmer_project`, `task_type`, `due_date`, `assigned_to` |
| Validation | Project active; assignee in scope; `block` denormalized from project |
| Sync | Prefer `sync.push` op `entity=task`; direct API for online-only quick create |
| Failures | `VAL_REQUIRED_FIELD`, duplicate `client_id` → idempotent success |

---

### API: `task.update`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.task.update` |
| **Method** | `POST` |

**Request:** `{ "name", "doc_version", "status?", "description?", "visit_outcome?", "assigned_to?" }`

| Validation | `doc_version` match for LWW; completed requires `visit_outcome` optional |
| Sync | `sync.push` update with `doc_version` |
| Failures | `SYNC_CONFLICT_LWW` (409) |

---

### API: `task.complete`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.task.complete` |
| **Method** | `POST` |
| **Purpose** | Idempotent completion shortcut |

**Request:** `{ "name", "doc_version", "visit_outcome", "completed_on" }`  
**Response:** Updated task; does not advance project stage.

---

## 17. Farmer API contracts

### API: `farmer.list`

| **Endpoint** | `agriflow.api.v1.farmer.list` |
| **Method** | `POST` |
| **Purpose** | Search/list farmers in scope |
| **Auth** | Bearer |

**Request:** `{ "search", "block", "village", "modified_since", "limit", "cursor", "is_active": true }`  
**Response:** `{ items: [ FarmerSummary ], pagination }`

**FarmerSummary:** `name`, `farmer_name`, `mobile`, `block`, `village`, `district`, `is_active`, `modified`, `doc_version`, `client_id`

| Sync | Delta via `modified_since` + `sync.pull` |
| Failures | `PERM_SCOPE_BLOCK` |

---

### API: `farmer.get`

| **Endpoint** | `agriflow.api.v1.farmer.get`  
**Request:** `{ "name": "FR-00042" }`  
**Response:** Full farmer per DOCTYPES.md including optional land parcels.

---

### API: `farmer.create`

| **Endpoint** | `agriflow.api.v1.farmer.create`  
**Auth** | Office Staff, Field Staff (block scope), Office Manager, Owner  

**Request `data`**

```json
{
  "client_id": "uuid",
  "farmer_name": "ராமன்",
  "mobile": "9876543210",
  "district": "TVM",
  "block": "BLK01",
  "village": "VLG001",
  "father_name": "",
  "primary_survey_number": "",
  "land_extent_acres": 1.5,
  "address_line": "",
  "created_via": "mobile"
}
```

| Validation | Mobile 10 digits; village ∈ block; unique mobile per district policy |
| Sync | **Client wins** on create; `client_id` idempotent |
| Failures | `VAL_*`, idempotent duplicate → return existing |

---

### API: `farmer.update`

| **Endpoint** | `agriflow.api.v1.farmer.update`  
**Request:** `{ "name", "doc_version", ...mutable fields }`  
| Sync | LWW on `doc_version` |
| Failures | `SYNC_CONFLICT_LWW`, cannot deactivate with active project |

---

## 18. Farmer Project API contracts

**Farmer Project is the aggregate root.** Stage changes use `project.transition` only.

### API: `project.list`

| **Endpoint** | `agriflow.api.v1.project.list` |
| **Method** | `POST` |
| **Purpose** | Primary work queue; block/stage filters |
| **Auth** | Bearer |

**Request `data`**

```json
{
  "block": ["BLK01"],
  "cluster": null,
  "officer": null,
  "current_stage": null,
  "status": "active",
  "assigned_to": null,
  "modified_since": "2026-05-20T00:00:00.000Z",
  "search": null,
  "limit": 25,
  "cursor": null
}
```

**Response:** `{ items: [ ProjectSummary ], pagination }`

**ProjectSummary:** `name`, `project_title`, `farmer`, `farmer_name`, `current_stage`, `stage_sequence`, `status`, `block`, `village`, `officer`, `priority`, `modified`, `doc_version`, `client_id`

| Sync | High-priority delta pull |
| Failures | `PERM_SCOPE_BLOCK` |

---

### API: `project.get`

| **Endpoint** | `agriflow.api.v1.project.get`  
**Request:** `{ "name": "FP-2026-00124" }`  
**Response:** Full project fields (financial summaries, mimis_registration_number, etc.)

---

### API: `project.create`

| **Endpoint** | `agriflow.api.v1.project.create` |
| **Purpose** | Start subsidy project for farmer (stage = `lead_captured`) |
| **Auth** | Office Staff+, Field Staff (block scope) |

**Request `data`**

```json
{
  "client_id": "uuid",
  "farmer": "FR-00042",
  "project_type": "subsidy",
  "district": "TVM",
  "block": "BLK01",
  "cluster": "CLU01",
  "village": "VLG001",
  "officer": "OFF01",
  "assigned_to": "user@example.com",
  "remarks": "",
  "created_via": "mobile"
}
```

| Validation | One active subsidy project per farmer; geography chain valid |
| Sync | Client wins create; server creates initial stage history row |
| Failures | `VAL_DUPLICATE_ACTIVE_PROJECT`, idempotent `client_id` |

**Response `data`:** `{ "name", "current_stage": "lead_captured", "stage_sequence": 1, "doc_version": 1, ... }`

---

### API: `project.update`

| **Endpoint** | `agriflow.api.v1.project.update` |
| **Purpose** | Update non-stage fields only |
| **Auth** | Per role |

**Mutable fields:** `assigned_to`, `priority`, `remarks`, `expected_subsidy_amount`, `quoted_amount`, `mimis_registration_number`, `work_order_number`, `officer` (with validation)

**Immutable via this API:** `current_stage`, `stage_sequence` — use `project.transition`.

| Validation | `doc_version` LWW; officer change warnings after stage 7 |
| Failures | `PERM_DENIED`, `SYNC_CONFLICT_LWW` |

---

### API: `project.transition`

| **Endpoint** | `agriflow.api.v1.project.transition` |
| **Method** | `POST` |
| **Purpose** | **Server-authoritative** sequential stage advance |
| **Auth** | Role matrix per DOCTYPES.md §2 |

**Request `data`**

```json
{
  "name": "FP-2026-00124",
  "target_stage": "field_survey",
  "doc_version": 11,
  "client_id": "uuid",
  "notes": "Survey scheduled",
  "attachment_file_id": null
}
```

| Required | `name`, `target_stage`, `doc_version`, `client_id` |
| Validation | `target_sequence = current + 1`; role gate; project `active`; attachments if required by stage policy |
| Sync | Queue with project serialization; **server wins** on stale `doc_version` or stage |
| Failures | `SYNC_STALE_TRANSITION`, `VAL_INVALID_STAGE`, `PERM_DENIED` |

**Response `data`**

```json
{
  "name": "FP-2026-00124",
  "current_stage": "field_survey",
  "stage_sequence": 5,
  "doc_version": 12,
  "stage_history_row": { "to_stage": "field_survey", "to_sequence": 5, "transitioned_on": "..." },
  "tasks_created": ["TSK-2026-00130"]
}
```

---

### API: `sync.push`

| **Endpoint** | `agriflow.api.v1.sync.push` |
| **Method** | `POST` |
| **Purpose** | Apply SyncQueue batch (primary offline write path) |
| **Auth** | Bearer |

**Request `data`**

```json
{
  "device_id": "uuid",
  "pushed_at": "2026-05-20T10:00:00.000Z",
  "operations": []
}
```

`operations[]` — see §13.

**Response `data`**

```json
{
  "results": [
    {
      "op_id": "uuid",
      "status": "success",
      "entity": "farmer_project",
      "client_id": "uuid",
      "name": "FP-2026-00124",
      "doc_version": 12
    },
    {
      "op_id": "uuid",
      "status": "conflict",
      "conflict": {}
    }
  ],
  "summary": { "success": 4, "conflict": 1, "failed": 0 }
}
```

| HTTP | 200 if all success; 207 if partial (see §6) |
| Sync | Core of offline protocol |
| Failures | `SYNC_PARTIAL_FAILURE`, malformed op → per-op `failed` |

---

### API: `sync.pull`

| **Endpoint** | `agriflow.api.v1.sync.pull` |
| **Method** | `POST` |
| **Purpose** | Delta download for transactional entities |
| **Auth** | Bearer |

**Request / Response:** See §9.

---

## 19. Geography master APIs

All masters: **read-only** on mobile · **server wins** · cache in Hive · delta via `modified_since`.

### API: `master.districts`

| **Endpoint** | `agriflow.api.v1.master.districts` |
| **Method** | `POST` |
| **Auth** | Bearer |

**Request:** `{ "modified_since": null, "is_active": true }`  
**Response:** `{ items: [{ district_code, district_name, state, is_active, modified }] }`

---

### API: `master.blocks`

| **Endpoint** | `agriflow.api.v1.master.blocks`  
**Request:** `{ "district": "TVM", "modified_since", "limit", "cursor" }`  
**Response:** Paginated block list with `district` link.

---

### API: `master.clusters`

| **Endpoint** | `agriflow.api.v1.master.clusters`  
**Request:** `{ "block": "BLK01", "modified_since" }`

---

### API: `master.villages`

| **Endpoint** | `agriflow.api.v1.master.villages`  
**Request:** `{ "block", "cluster", "modified_since", "limit", "cursor" }`  
**Validation:** At least one of `block` or `cluster` required.

---

### API: `master.officers`

| **Endpoint** | `agriflow.api.v1.master.officers`  
**Response items:** `officer_code`, `officer_name`, `department`, `current_cluster`, `is_active`, `modified`

---

### API: `master.officer_assignments`

| **Endpoint** | `agriflow.api.v1.master.officer_assignments` |
| **Purpose** | Active + historical assignments for offline officer filter / reports |
| **Auth** | Bearer; write only desk (not mobile Phase 1) |

**Request:** `{ "cluster", "officer", "active_only": true, "modified_since" }`  
**Response:** Assignment rows with `valid_from`, `valid_to`, `assignment_reason`

| Sync | Pull-only; append-only server-side |
| Failures | Large result sets — use pagination |

---

## 20. MIMIS reconciliation APIs

**Online only.** Not part of `sync.push`. Never interfaces with government portal.

### API: `mimis.upload_excel`

| **Endpoint** | `agriflow.api.v1.mimis.upload_excel` |
| **Method** | `POST` multipart |
| **Auth** | Office Manager, Owner |
| **Purpose** | Start import batch |

**Form fields:** `file`, `template_version`, `file_hash` (SHA-256)

**Response `data`:** `{ "batch_id": "MIMIS-BAT-2026-00012", "batch_status": "processing" }`

| Validation | Known `template_version`; duplicate `file_hash` → `MIMIS_DUPLICATE_BATCH` |
| Sync | None |
| Failures | `MIMIS_INVALID_TEMPLATE`, `VAL_INVALID_FILE` |

---

### API: `mimis.batch_status`

| **Endpoint** | `agriflow.api.v1.mimis.batch_status` |
| **Method** | `POST` |
| **Auth** | Office Manager, Owner |

**Request:** `{ "batch_id": "MIMIS-BAT-2026-00012" }`  
**Response:** `{ batch_status, row_count, matched_count, error_log, uploaded_on }`

---

### API: `mimis.reconciliation_report`

| **Endpoint** | `agriflow.api.v1.mimis.reconciliation_report` |
| **Method** | `POST` |
| **Purpose** | Paginated row-level results |

**Request:** `{ "batch_id", "row_status", "limit", "cursor" }`  
**Response items:** `row_number`, `row_status`, `mimis_registration_number`, `farmer_project`, `match_confidence`, `excel_name`, `excel_mobile`

---

### API: `mimis.approve_row`

| **Endpoint** | `agriflow.api.v1.mimis.approve_row` |
| **Method** | `POST` |
| **Auth** | Office Manager, Owner |
| **Purpose** | Approve match; optionally trigger `mimis_registered` transition |

**Request**

```json
{
  "batch_id": "MIMIS-BAT-2026-00012",
  "row_number": 45,
  "farmer_project": "FP-2026-00124",
  "advance_stage": true,
  "client_id": "uuid"
}
```

| Validation | Project at stage 3 if `advance_stage`; manual link if ambiguous |
| Failures | `VAL_INVALID_STAGE`, `PERM_DENIED` |
| Audit | Mandatory approval audit event |

---

### API: `mimis.reject_row`

| **Endpoint** | `agriflow.api.v1.mimis.reject_row`  
**Request:** `{ "batch_id", "row_number", "rejection_reason" }`

---

## 21. Inventory APIs

P1 · Store Keeper + Owner primary writers.

### API: `inventory.items`

| **Endpoint** | `agriflow.api.v1.inventory.items` |
| **Method** | `POST` |
| **Purpose** | Master list of Inventory Item |
| **Auth** | Bearer (read all operational roles) |

**Request:** `{ "modified_since", "search", "is_active", "limit", "cursor" }`  
**Response:** Item catalog for mobile pickers.

| Sync | Server wins master cache in Hive |

---

### API: `inventory.stock_entry.create`

| **Endpoint** | `agriflow.api.v1.inventory.stock_entry.create` |
| **Auth** | Store Keeper, Owner |

**Request `data`**

```json
{
  "client_id": "uuid",
  "stock_entry_type": "issue",
  "posting_date": "2026-05-20",
  "from_godown": "godown_1",
  "to_godown": null,
  "farmer_project": "FP-2026-00124",
  "items": [{ "inventory_item": "ITEM-001", "qty": 10, "uom": "Nos" }]
}
```

| Validation | Line items ≥ 1; transfer requires both godowns; issue may require project at stage ≥ 9 |
| Sync | May use `sync.push` entity `stock_entry` when enabled |
| Failures | `VAL_*`, insufficient stock (future bin check) |

---

### API: `inventory.stock_entry.list`

| **Endpoint** | `agriflow.api.v1.inventory.stock_entry.list`  
**Request:** `{ "farmer_project", "from_godown", "modified_since", "limit", "cursor" }`

---

## 22. Expense APIs

P1 · Profit visibility (M9).

### API: `expense.list`

| **Endpoint** | `agriflow.api.v1.expense.list` |
| **Method** | `POST` |
| **Auth** | Owner, Office Manager, Office Staff (read) |

**Request:** `{ "farmer_project", "block", "expense_date_gte", "expense_date_lte", "modified_since", "limit", "cursor" }`

---

### API: `expense.create`

| **Endpoint** | `agriflow.api.v1.expense.create` |
| **Auth** | Owner, Office Manager, Office Staff |

**Request `data`**

```json
{
  "client_id": "uuid",
  "farmer_project": "FP-2026-00124",
  "expense_date": "2026-05-20",
  "expense_category": "travel",
  "amount": 1500,
  "payment_mode": "cash",
  "notes": "",
  "bill_file_id": null
}
```

| Validation | `amount` > 0; project active; updates project `total_expense` rollup async |
| Sync | Client wins create via `sync.push` |
| Failures | idempotent `client_id` |

---

### API: `expense.update`

| **Endpoint** | `agriflow.api.v1.expense.update`  
**Request:** `{ "name", "doc_version", ... }` — LWW  
**Auth** | Office Manager, Owner for amount changes |

---

## 23. Audit / event hooks

### 23.1 Server-side audit (synchronous)

Every **write API** that mutates Farmer Project stage, officer assignment, MIMIS approval, stock, or expense emits row in **AgriFlow Audit Log** (DOCTYPES.md).

Audit payload internally includes: `request_id`, `client_id`, `actor`, `before_json`, `after_json`.

### 23.2 API: `audit.query` (desk / owner)

| **Endpoint** | `agriflow.api.v1.audit.query` |
| **Method** | `POST` |
| **Auth** | Owner, Office Manager |
| **Purpose** | Support and compliance export |

**Request:** `{ "reference_doctype", "reference_name", "from", "to", "limit", "cursor" }`  
**Response:** Audit rows (no stack traces).

### 23.3 Webhooks (Phase 1 optional / Phase 2)

Reserved hook names (not implemented Phase 1):

| Event | Payload includes |
|-------|------------------|
| `project.stage_changed` | project id, from/to stage, actor |
| `task.overdue` | task id, assigned_to |
| `mimis.batch_completed` | batch_id, counts |

Delivery: HMAC-signed POST to dealer-configured URL. Document only.

### 23.4 Mobile diagnostic: `sync.status`

| **Endpoint** | `agriflow.api.v1.sync.status` |
| **Method** | `POST` |
| **Purpose** | Last server receipt time per `device_id` (optional) |

**Response:** `{ "last_push_at", "last_pull_at", "pending_server_jobs": 0 }`

---

## 24. Rate limiting guidelines

| Endpoint class | Limit (per user) | Window |
|----------------|------------------|--------|
| `auth.login` | 10 failures / lockout 15 min | per username + IP |
| `auth.refresh` | 60 | per minute |
| `sync.push` | 30 | per minute |
| `sync.pull` | 60 | per minute |
| `master.*` | 30 | per minute |
| Default API | 120 | per minute |

**Response when limited:** HTTP `429` with `error.code = RATE_LIMITED` and `Retry-After` header (seconds).

**Guideline:** Rate limits are safety nets — normal mobile usage stays well below limits.

---

## 25. API security rules

| Rule | Requirement |
|------|-------------|
| Transport | TLS 1.2+ only |
| Auth | Bearer JWT on all except login |
| Scope | Enforce User Permission on every list/get/write |
| PII | No full Aadhaar in API; mask mobile in logs |
| IDOR | Never accept `name` without scope check |
| Input | Validate against DOCTYPES; reject unknown fields (strict mode optional) |
| Files | MIME allowlist; virus scan Phase 2 |
| Errors | No stack traces in `error.message` |
| CORS | Not applicable to mobile; desk uses same site |
| Secrets | No API keys in mobile binary |

---

## 26. Mobile compatibility strategy

| Mechanism | Behavior |
|-----------|----------|
| `min_mobile_version` | Block login with upgrade message if below |
| `api_version` | Client must match major version `v1` |
| Feature flags | `permissions.features` in login manifest |
| Backward compatible fields | Clients ignore unknown response fields |
| Forward compatibility | Server ignores unknown request fields (log once) |
| Offline | Queue + pull; show `sync.status` in UI |
| Tamil | Use `message_i18n_key` + local ARB |
| Testing | Contract tests against fixture JSON snapshots |

**Login manifest snippet (`auth.login` → `data.permissions`):**

```json
{
  "roles": ["Field Staff"],
  "blocks": ["BLK01", "BLK02"],
  "districts": ["TVM"],
  "features": {
    "project_transition": true,
    "mimis_upload": false,
    "inventory_write": false
  }
}
```

---

## 27. Future extensibility considerations

| Area | Reserved namespace | Phase 1 |
|------|-------------------|---------|
| Leads | `agriflow.api.v1.lead.*` | Not registered |
| Project types | `project_type` field + fixtures | `subsidy` only |
| Multi-district | `master.districts` + JWT `districts[]` | Single district seeded |
| Billing | `agriflow.api.v1.billing.*` | Out of scope |
| Webhooks | §23.3 | Documented only |
| API v2 | `/v2/` parallel namespace | When breaking change required |

**Extension rules**

- New endpoints must use standard envelope and `X-Request-ID`.  
- New sync entities require ARCHITECTURE + DOCTYPES + this document update.  
- Stage templates for new `project_type` values must not alter subsidy sequence numbers 1–12.

---

## Appendix A — Authentication API reference

### API: `auth.login`

| Property | Value |
|----------|-------|
| **Endpoint** | `agriflow.api.v1.auth.login` |
| **Method** | `POST` |
| **Auth** | None |

**Request `data`:** `{ "username": "user@example.com", "password": "***" }`

**Response `data`:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "user": { "name": "user@example.com", "full_name": "..." },
  "permissions": {}
}
```

| Failures | `AUTH_INVALID_CREDENTIALS` (401) |

---

### API: `auth.refresh`

| **Endpoint** | `agriflow.api.v1.auth.refresh`  
**Request:** `{ "refresh_token": "eyJ..." }`  
**Response:** New access token pair; old refresh invalidated on rotation.

| Failures | `AUTH_TOKEN_INVALID`, `AUTH_REFRESH_REUSED` |

---

### API: `auth.logout`

| **Endpoint** | `agriflow.api.v1.auth.logout`  
**Request:** `{ "refresh_token": "eyJ..." }`  
**Response:** `{ "logged_out": true }`

---

### API: `auth.permissions`

| **Endpoint** | `agriflow.api.v1.auth.permissions` |
| **Method** | `POST` |
| **Purpose** | Refresh manifest without re-login |
| **Auth** | Bearer |

**Response:** Same `permissions` object as login.

---

## Appendix B — Entity payload field reference

Detailed field lists: [DOCTYPES.md](./DOCTYPES.md). APIs return JSON camelCase **or** snake_case — **Phase 1 standard: snake_case** (matches Frappe fields and DOCTYPES).

---

## Appendix C — Phase 1 API index

| Area | Endpoints |
|------|-----------|
| Auth | `login`, `refresh`, `logout`, `permissions` |
| Sync | `push`, `pull`, `status` |
| Project | `list`, `get`, `create`, `update`, `transition`, `timeline` |
| Farmer | `list`, `get`, `create`, `update` |
| Task | `list`, `get`, `create`, `update`, `complete` |
| Master | `districts`, `blocks`, `clusters`, `villages`, `officers`, `officer_assignments` |
| File | `upload`, `download` |
| MIMIS | `upload_excel`, `batch_status`, `reconciliation_report`, `approve_row`, `reject_row` |
| Inventory | `items`, `stock_entry.create`, `stock_entry.list` |
| Expense | `list`, `create`, `update` |
| Audit | `query` |

---

## Change control

| Change | Update |
|--------|--------|
| New endpoint | This file + ARCHITECTURE §5 |
| Breaking payload | API v2 + `min_mobile_version` |
| New sync entity | §8–9, §13, DOCTYPES sync section |

---

*End of API_CONTRACTS.md*
