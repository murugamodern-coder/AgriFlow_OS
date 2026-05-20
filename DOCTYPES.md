# AgriFlow OS — DocType Specification

**Version:** 1.0  
**Status:** Phase 1 specification (documentation only)  
**Last updated:** 2026-05-20  

**Related documents:** [PRD.md](./PRD.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [UI_TOKENS.md](./UI_TOKENS.md) · [.cursorrules](./.cursorrules)

---

## Document purpose

This document defines **enterprise-grade Frappe DocType specifications** for AgriFlow OS Phase 1. It is the authoritative data model reference for backend implementation, mobile sync mapping, fixtures, and permissions.

**Scope**

| Priority | DocTypes | Delivery |
|----------|----------|----------|
| **P0** | Core operational + geography + officer network | Phase 1 — required |
| **P1** | Inventory, expenses, MIMIS reconciliation | Phase 1 — implement after P0 spine is stable |

**Out of scope for this document:** application code, Frappe JSON exports, SQL DDL. Future Lead / Project Type DocTypes are defined in [ARCHITECTURE.md §21](./ARCHITECTURE.md#21-future-expansion-architecture) only.

---

## Global conventions

### Naming

| Artifact | Convention | Example |
|----------|------------|---------|
| DocType name | Title Case, singular | `Farmer Project` |
| Database table | `tab` + Title Case with spaces | `tabFarmer Project` |
| Field name | snake_case | `current_stage` |
| Stage keys | snake_case fixture values | `lead_captured` |
| Child table | Title Case | `Project Stage History` |

### Autoname strategies

| Pattern | Use when |
|---------|----------|
| `format:FP-{YYYY}-{#####}` | Farmer Project (human-readable ops ID) |
| `format:FR-{#####}` | Farmer |
| `format:TSK-{YYYY}-{#####}` | Task |
| `field:district_code` | District (stable code from fixture) |
| `field:block_code` | Block |
| `field:code` | Cluster, Village, Officer (short codes) |
| `hash` | High-volume immutable rows (stage history lines, reconciliation rows) |
| `naming_series:` | Stock Entry, Expense Entry, MIMIS Import Batch |

### Aggregate root

**Farmer Project** is the aggregate root for subsidy workflow. Related documents (Task, Stage History, Stock Entry, Expense Entry) link **to** Farmer Project; the project does not embed mutable copies of master geography beyond snapshot links.

---

## Cross-cutting specifications

### ER relationship overview

```
District ──< Block ──< Cluster ──< Village
                │         │
                │         └──< Officer Assignment History >── Officer
                │
Farmer ─────────┴── (block, village links)
  │
  └──< Farmer Project (aggregate root) ──< Project Stage History (child)
            │              │
            │              ├──< Task
            │              ├──< Stock Entry (P1)
            │              ├──< Expense Entry (P1)
            │              └──< MIMIS Reconciliation Row (P1)
            │
            └── officer, cluster, block, village (links)

Officer ── department, cluster (current)

MIMIS Import Batch ──< MIMIS Reconciliation Row

Inventory Item ──< Stock Entry Item (child)
```

**Cardinality rules**

- One `Farmer` → many `Farmer Project` (only one active subsidy project per policy — enforce in validation).
- One `Farmer Project` → many `Project Stage History` rows (append-only).
- One `Cluster` → many `Village`; one active `Officer Assignment History` row per cluster scope at a time.
- `MIMIS Reconciliation Row` always belongs to one `MIMIS Import Batch` and optionally links one `Farmer Project` after match.

---

### Common audit fields

Apply to all **transactional** DocTypes (Farmer, Farmer Project, Task, Stock Entry, Expense Entry, MIMIS batch/rows). Master geography DocTypes use a reduced set.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `created_by_user` | Link → User | Auto | Set on create |
| `created_via` | Select | No | `mobile`, `desk`, `import`, `system` |
| `client_id` | Data (UUID) | Mobile creates | Idempotency; unique where not null |
| `last_synced_at` | Datetime | No | Server-side last mobile push/pull marker |
| `ip_address` | Data | No | On sensitive mutations |

Frappe standard fields (`owner`, `creation`, `modified`, `modified_by`) remain enabled. **Do not duplicate** `modified` semantics in custom fields.

**AgriFlow Audit Log** (separate DocType — implement with P0):

| Field | Type |
|-------|------|
| `timestamp` | Datetime |
| `actor` | Link → User |
| `action` | Data |
| `reference_doctype` | Data |
| `reference_name` | Dynamic Link |
| `before_json` | Long Text |
| `after_json` | Long Text |
| `client_id` | Data |
| `ip_address` | Data |

---

### Sync metadata fields

Apply to entities that participate in mobile **sync.push / sync.pull** (P0: Farmer, Farmer Project, Task; P1: Expense Entry where field-created).

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `client_id` | Data (36) | On mobile create | Idempotent create |
| `doc_version` | Int | Auto increment | LWW conflict detection |
| `is_deleted` | Check | No | Soft delete for sync tombstones |
| `sync_status` | Select | No | `synced`, `pending` (desk-only diagnostic) |

**Not used on:** District, Block, Cluster, Village, Officer (master — server wins).  
**Not used on:** MIMIS Import Batch (online-only pipeline).

---

### Enumerations and fixtures

Ship as **Frappe fixtures** (`agriflow/fixtures/`), not hardcoded in Python/Dart.

| Fixture name | Values / purpose |
|--------------|------------------|
| `project_stage.json` | 12 stage keys + sequence + i18n label key |
| `project_stage_role_matrix.json` | Which roles may trigger which transition |
| `task_template.json` | Tasks auto-created per `to_stage` |
| `task_type.json` | `visit`, `call`, `document`, `inspection`, `installation`, `service` |
| `task_priority.json` | `low`, `medium`, `high`, `urgent` |
| `task_status.json` | `open`, `in_progress`, `completed`, `cancelled` |
| `officer_department.json` | `agriculture`, `horticulture` |
| `assignment_reason.json` | `transfer`, `initial`, `correction` |
| `mimis_row_status.json` | `matched`, `ambiguous`, `unmatched`, `approved`, `rejected` |
| `mimis_batch_status.json` | `draft`, `processing`, `completed`, `failed` |
| `stock_entry_type.json` | `receipt`, `issue`, `transfer`, `adjustment` |
| `expense_category.json` | Owner-configurable categories |
| `godown.json` | `godown_1`, `godown_2` (two physical godowns) |
| `district_seed.json` | Phase 1: Tiruvannamalai + 12 blocks |

**Project stage fixture (authoritative sequence)**

| seq | stage_key | label_i18n_key |
|-----|-----------|----------------|
| 1 | `lead_captured` | `project.stage.lead_captured` |
| 2 | `eligibility_check` | `project.stage.eligibility_check` |
| 3 | `documents_collected` | `project.stage.documents_collected` |
| 4 | `mimis_registered` | `project.stage.mimis_registered` |
| 5 | `field_survey` | `project.stage.field_survey` |
| 6 | `quotation_generated` | `project.stage.quotation_generated` |
| 7 | `pre_inspection_approval` | `project.stage.pre_inspection_approval` |
| 8 | `work_order_received` | `project.stage.work_order_received` |
| 9 | `material_dispatched` | `project.stage.material_dispatched` |
| 10 | `installation_done` | `project.stage.installation_done` |
| 11 | `post_inspection_approval` | `project.stage.post_inspection_approval` |
| 12 | `subsidy_released` | `project.stage.subsidy_released` |

---

### Recommended Frappe settings (global)

| Setting | Recommendation |
|---------|----------------|
| Track Changes | **On** for Farmer Project, Farmer, Officer Assignment History, MIMIS Import Batch |
| Track Seen | Off (mobile-first) |
| Allow Import | On for geography masters only |
| Allow Rename | Off for Farmer Project, stage history, assignment history |
| Is Submittable | Off (use service-layer state; avoid submit/cancel complexity in Phase 1) |
| Quick Entry | Off for Farmer Project |
| Title Field | See per DocType |

---

### Suggested additional child tables (Phase 1 optional)

| Child table | Parent | Purpose |
|-------------|--------|---------|
| `Farmer Land Parcel` | Farmer | Multiple survey numbers / extents |
| `Farmer Project Attachment` | Farmer Project | File reference + tag (not a separate DocType in Phase 1) |
| `Stock Entry Item` | Stock Entry | Line items |
| `Task Checklist Item` | Task | Sub-steps for installation/service |

---

# P0 — Core operational entities

---

## 1. Farmer

### 1. Purpose

Stores farmer **identity**, contact, and primary land reference. Farmers exist independently of projects; one farmer may have multiple projects over time (only one active subsidy project at a time in Phase 1).

### 2. Module

`Farmer Registry` (M1)

### 3. Naming strategy

- **Autoname:** `format:FR-{#####}`
- **Title field:** `farmer_name`
- **Search fields:** `farmer_name`, `mobile`, `aadhaar_last4`, `village`

### 4. Core fields

| Field | Label |
|-------|-------|
| `farmer_name` | Farmer Name |
| `mobile` | Mobile |
| `alternate_mobile` | Alternate Mobile |
| `aadhaar_last4` | Aadhaar (last 4) |
| `father_name` | Father / Spouse Name |
| `block` | Block |
| `village` | Village |
| `district` | District |
| `address_line` | Address |
| `pincode` | Pincode |
| `primary_survey_number` | Survey Number |
| `land_extent_acres` | Land Extent (acres) |
| `is_active` | Active |
| `notes` | Notes |
| `tags` | Tags |

### 5. Field types

| Field | Type | Options / link |
|-------|------|----------------|
| `farmer_name` | Data | — |
| `mobile` | Data | Phone validation |
| `alternate_mobile` | Data | — |
| `aadhaar_last4` | Data | Length 4 |
| `father_name` | Data | — |
| `block` | Link | Block |
| `village` | Link | Village |
| `district` | Link | District |
| `address_line` | Small Text | — |
| `pincode` | Data | — |
| `primary_survey_number` | Data | — |
| `land_extent_acres` | Float | — |
| `is_active` | Check | Default 1 |
| `notes` | Text | — |
| `tags` | Table MultiSelect or Small Text | Phase 1: comma-separated or child `Farmer Tag` later |

### 6. Required fields

`farmer_name`, `mobile`, `block`, `village`, `district`

### 7. Link relationships

| Field | Links to |
|-------|----------|
| `district` | District |
| `block` | Block |
| `village` | Village |

**Validation:** `village.block` must equal `block`; `block.district` must equal `district`.

### 8. Child tables

| Child | Phase | Notes |
|-------|-------|-------|
| `Farmer Land Parcel` | Optional P0 | `survey_number`, `extent_acres`, `crop` |

### 9. Workflow behavior

- No stage workflow. Lifecycle = active/inactive only.
- Creating a farmer does **not** create a Farmer Project (explicit separate action).

### 10. Validation rules

- `mobile`: 10 digits, unique per district (configurable strictness).
- `village` must belong to selected `block`.
- Cannot deactivate farmer if **active** Farmer Project exists.
- PII: store only `aadhaar_last4`; never full Aadhaar in Phase 1.

### 11. Permissions by role

| Role | Create | Read | Write | Delete |
|------|--------|------|-------|--------|
| Owner | ✓ | ✓ | ✓ | ✓ |
| Office Manager | ✓ | ✓ | ✓ | — |
| Office Staff | ✓ | ✓ | ✓ | — |
| Field Staff | ✓ | scoped | ✓ | — |
| Installer / Service / Store | — | limited* | — | — |

\*Field Staff: User Permission on `Block`. Installer/Service: read only if linked via project (API enforced).

### 12. Offline sync considerations

| Aspect | Policy |
|--------|--------|
| Conflict | New farmer: **client wins** (client_id). Updates: **LWW** via `doc_version`. |
| Master links | `block`, `village`, `district` resolved server-side on push if IDs changed |
| Pull | Included in `sync.pull` entity `farmer` with `modified_since` |
| Cache | Drift table `farmers`; not Hive (transactional) |

### 13. Audit requirements

- Log create/update of `mobile`, `block`, `village`, `is_active`.
- Track Changes enabled.

### 14. Suggested indexes

- `(mobile, district)` unique partial where not deleted
- `(village, is_active)`
- `(modified)` for delta sync
- `(client_id)` unique sparse

### 15. Future extensibility notes

- Reserve optional links: `lead` (future), `preferred_language` (default `ta`).
- Do not add project fields on Farmer — keep normalized.

---

## 2. Farmer Project

### 2. Purpose

**Aggregate root** for subsidy operations. Holds current workflow stage, geographic scope, officer context, and summary fields for timeline and profit. All operational modules attach here.

### 2. Module

`Project Lifecycle` (M5)

### 3. Naming strategy

- **Autoname:** `format:FP-{YYYY}-{#####}`
- **Title field:** `project_title` (computed or stored: farmer name + village short)
- **Search fields:** `name`, `farmer`, `village`, `current_stage`

### 4. Core fields

| Field | Label |
|-------|-------|
| `project_title` | Title |
| `farmer` | Farmer |
| `project_type` | Project Type |
| `current_stage` | Current Stage |
| `stage_sequence` | Stage Sequence |
| `district` | District |
| `block` | Block |
| `cluster` | Cluster |
| `village` | Village |
| `officer` | Officer |
| `status` | Status |
| `started_on` | Started On |
| `expected_subsidy_amount` | Expected Subsidy |
| `quoted_amount` | Quoted Amount |
| `total_expense` | Total Expense (rollup) |
| `mimis_registration_number` | MIMIS Registration No. |
| `work_order_number` | Work Order No. |
| `assigned_to` | Assigned To (User) |
| `priority` | Priority |
| `remarks` | Remarks |

### 5. Field types

| Field | Type | Notes |
|-------|------|-------|
| `project_title` | Data | Auto from farmer + village |
| `farmer` | Link | Farmer |
| `project_type` | Select | Phase 1: `subsidy` only; fixture-ready |
| `current_stage` | Select | Fixture: 12 stage keys |
| `stage_sequence` | Int | Denormalized 1–12 for sorting |
| `district` | Link | District |
| `block` | Link | Block |
| `cluster` | Link | Cluster |
| `village` | Link | Village |
| `officer` | Link | Officer |
| `status` | Select | `active`, `on_hold`, `completed`, `cancelled` |
| `started_on` | Date | |
| `expected_subsidy_amount` | Currency | |
| `quoted_amount` | Currency | |
| `total_expense` | Currency | Read-only rollup from Expense Entry |
| `mimis_registration_number` | Data | Set by reconciliation or manual |
| `work_order_number` | Data | |
| `assigned_to` | Link | User |
| `priority` | Select | `low`, `medium`, `high` |
| `remarks` | Text | |

Plus **sync metadata** and **audit** fields from cross-cutting sections.

### 6. Required fields

`farmer`, `project_type`, `current_stage`, `district`, `block`, `cluster`, `village`, `status`

`officer` required when `stage_sequence` ≥ 4 (MIMIS registered) — validate in service.

### 7. Link relationships

| Field | Links to |
|-------|----------|
| `farmer` | Farmer |
| `district` | District |
| `block` | Block |
| `cluster` | Cluster |
| `village` | Village |
| `officer` | Officer |
| `assigned_to` | User |

### 8. Child tables

| Child | Required |
|-------|----------|
| `Project Stage History` | Yes — append-only via service |

Optional: `Farmer Project Attachment` (file_id, description, stage_key)

### 9. Workflow behavior

- **Stage changes only** via `ProjectLifecycleService.transition()` — never direct edit of `current_stage` from desk/mobile UI bypassing service.
- Sequential 12-stage progression; `stage_sequence` must equal prior + 1.
- On transition: append `Project Stage History`, update `current_stage` + `stage_sequence`, enqueue `generate_stage_tasks` job.
- `status` = `completed` only when `current_stage` = `subsidy_released`.
- Stage-specific role gates (see validation).

**Stage permission matrix (service-enforced)**

| to_stage (key) | Minimum role |
|----------------|--------------|
| `lead_captured` … `documents_collected` | Office Staff / Field Staff |
| `mimis_registered` | Office Manager (after MIMIS approval) or system job |
| `field_survey` | Field Staff |
| `quotation_generated` | Office Staff |
| `pre_inspection_approval`, `post_inspection_approval` | Office Manager |
| `work_order_received` | Office Staff |
| `material_dispatched` | Store Keeper |
| `installation_done` | Installer Team |
| `subsidy_released` | Owner or Office Manager |

### 10. Validation rules

- Only **one** `active` subsidy project per `farmer` at a time.
- `village` ∈ `cluster`; `cluster.block` = `block`; `block.district` = `district`.
- `officer` must match active `Officer Assignment History` for `cluster` (warning if mismatch; block if stage ≥ 7).
- Cannot skip stages; cannot move `stage_sequence` backward without Owner compensating history entry.
- `cancelled` projects frozen — no transitions.
- `doc_version` incremented on every successful transition.

### 11. Permissions by role

| Role | Create | Read | Write | Transition |
|------|--------|------|-------|------------|
| Owner | ✓ | all | ✓ | all |
| Office Manager | ✓ | all | ✓ | approval stages |
| Office Staff | ✓ | all | ✓ | office stages |
| Field Staff | — | block scope | limited | field_survey, visits |
| Installer | — | stage 9–10 | — | installation_done |
| Store Keeper | — | stage 9 | stock link | material_dispatched |
| Service Tech | — | AMC only* | — | — |

\*AMC fields in Phase 2; read-only project context in Phase 1 if needed.

### 12. Offline sync considerations

| Aspect | Policy |
|--------|--------|
| Create | **Client wins** with `client_id` |
| Stage transition | Queued; **server authoritative** — stale transition rejected |
| Pull priority | High — `project.list`, `project.timeline` |
| Ordering | SyncQueue serialized **per project id** |
| Denormalized fields | `stage_sequence` updated only on server after transition |

### 13. Audit requirements

- **Mandatory** audit log on every stage transition (before/after `current_stage`).
- Track Changes on financial fields and `officer`.
- Timeline = child history + audit log (dual evidence).

### 14. Suggested indexes

- `(farmer, status)` where status = active
- `(block, current_stage, modified)`
- `(cluster, officer, current_stage)`
- `(district, modified)`
- `(client_id)` unique sparse
- `(stage_sequence, block)` for dashboards

### 15. Future extensibility notes

- `project_type` fixture: `subsidy`, `cash_carry`, `tree_crop`, … (ARCHITECTURE §21.4).
- Optional future: `lead`, `lead_source`, `referral_partner` (immutable snapshot).
- Do not split into multiple DocTypes per project type.

---

## 3. Project Stage History

### 3. Purpose

Immutable **append-only** record of each stage transition for timeline UI and compliance. Never updated in place; corrections use compensating rows with `is_correction` flag.

### 3. Module

`Project Lifecycle` (M5)

### 3. Naming strategy

- **Implementation:** Child table on `Farmer Project` (preferred Phase 1) *or* standalone DocType with `parent` link — child table reduces orphan rows.
- **Row identity:** `hash` or incremental `idx` within parent
- **Title:** `to_stage` + `transitioned_on`

### 4. Core fields

| Field | Label |
|-------|-------|
| `from_stage` | From Stage |
| `to_stage` | To Stage |
| `from_sequence` | From Sequence |
| `to_sequence` | To Sequence |
| `transitioned_on` | Transitioned On |
| `transitioned_by` | Transitioned By |
| `notes` | Notes |
| `attachment` | Attachment |
| `is_correction` | Is Correction |
| `corrects_row` | Corrects Row |
| `client_id` | Client ID |

### 5. Field types

| Field | Type |
|-------|------|
| `from_stage` | Select (fixture) |
| `to_stage` | Select (fixture) |
| `from_sequence` | Int |
| `to_sequence` | Int |
| `transitioned_on` | Datetime |
| `transitioned_by` | Link → User |
| `notes` | Small Text |
| `attachment` | Attach / Link → File |
| `is_correction` | Check |
| `corrects_row` | Data | child row name reference |
| `client_id` | Data |

### 6. Required fields

`from_stage`, `to_stage`, `to_sequence`, `transitioned_on`, `transitioned_by`

(`from_stage` null only for initial creation → `lead_captured`)

### 7. Link relationships

- Parent: `Farmer Project` (table child `parent`, `parenttype`, `parentfield`)
- `transitioned_by` → User
- `attachment` → File

### 8. Child tables

None.

### 9. Workflow behavior

- Rows created **only** by `ProjectLifecycleService` — hook blocks manual child row add/delete for non-Administrator.
- No delete permission for any role except System Manager compensating tool.
- Initial row: `to_stage` = `lead_captured`, `from_stage` empty.

### 10. Validation rules

- `to_sequence` = `from_sequence` + 1 (except initial).
- `to_stage` must match fixture sequence for `to_sequence`.
- Duplicate transition same `to_stage` forbidden unless `is_correction`.

### 11. Permissions by role

| Role | Add | Read | Delete |
|------|-----|------|--------|
| All operational | via service only | ✓ | — |
| Owner | — | ✓ | correction via service |
| System Manager | ✓ | ✓ | break-glass only |

### 12. Offline sync considerations

- Embedded in project push or separate timeline pull — mobile Drift `project_stage_history` keyed by `project_id`.
- **Server wins** on conflict — client cannot edit history rows.
- Transition API returns full new row for cache insert.

### 13. Audit requirements

- Each row is itself an audit artifact; also write summary to AgriFlow Audit Log.
- Track Changes optional (child rows version with parent).

### 14. Suggested indexes

- `(parent, to_sequence)` on child table
- `(parent, transitioned_on desc)`

### 15. Future extensibility notes

- `transition_reason` Select for hold/cancel paths.
- `project_type` inherited from parent — no field needed on child.

---

## 3A. Timeline Event

### 3A. Purpose

**Unified append-only activity stream** for Farmer Project operations. Powers mobile activity feeds, offline sync replay, audit visibility, and future notifications. Complements **Project Stage History** (workflow-specific) without duplicating full document snapshots.

### 3A. Module

`Project Lifecycle` (M5)

### 3A. Naming strategy

- **Autoname:** `hash`
- **Title field:** `event_type`
- **Sort:** `created_on` DESC

### 3A. Core fields

| Field | Label |
|-------|-------|
| `farmer_project` | Farmer Project |
| `farmer` | Farmer |
| `event_type` | Event Type |
| `event_source` | Event Source |
| `created_on` | Created On |
| `actor` | Actor |
| `actor_name` | Actor Name |
| `payload_json` | Payload |
| `reference_doctype` | Reference DocType |
| `reference_name` | Reference Name |
| `district` | District |
| `block` | Block |
| `client_id` | Client ID |
| `is_deleted` | Is Deleted |

### 3A. Field types

| Field | Type | Notes |
|-------|------|-------|
| `farmer_project` | Link → Farmer Project | Required; indexed |
| `farmer` | Link → Farmer | Required; denormalized for farmer feeds |
| `event_type` | Select | `project_created`, `stage_transition`, `mimis_gate_updated`, `project_status_changed`, `manual_note` |
| `event_source` | Select | `lifecycle`, `mimis`, `desk`, `mobile`, `system` |
| `created_on` | Datetime | Required; chronological sort key |
| `actor` | Link → User | |
| `actor_name` | Data | Display snapshot |
| `payload_json` | JSON | Lightweight refs only — no full entity blobs |
| `reference_doctype` | Data | e.g. `Project Stage History` |
| `reference_name` | Data | Linked row name |
| `district` | Link → District | Scope filter |
| `block` | Link → Block | Scope filter |
| `client_id` | Data (36) | Idempotent emit / sync replay |
| `is_deleted` | Check | Sync tombstone |

### 3A. Required fields

`farmer_project`, `farmer`, `event_type`, `event_source`, `created_on`

### 3A. Link relationships

| Field | Links to |
|-------|----------|
| `farmer_project` | Farmer Project |
| `farmer` | Farmer |
| `actor` | User |
| `district` | District |
| `block` | Block |

### 3A. Child tables

None.

### 3A. Workflow behavior

- Rows created **only** via `TimelineService.emit()` (and desk whitelisted `add_timeline_note_for_desk`).
- **Immutable:** no in-place updates; `track_changes` off.
- Lifecycle hooks emit: `project_created`, `stage_transition`; Farmer Project `on_update` emits `mimis_gate_updated`, `project_status_changed`.
- Future `project.timeline` API reads via `TimelineService.query()` + stage history merge.

### 3A. Validation rules

- Payload size capped in service (no large duplicated objects).
- Duplicate `(client_id, event_type, farmer_project)` rejected on emit (idempotent return).
- DocType blocks save on existing rows outside service flag.

### 3A. Permissions by role

| Role | Create | Read | Write | Delete |
|------|--------|------|-------|--------|
| System Manager | via service | ✓ | — | — |
| Operational roles | via service only | ✓ | — | — |
| Administrator | break-glass | ✓ | break-glass | break-glass |

### 3A. Offline sync considerations

| Aspect | Policy |
|--------|--------|
| Pull | Delta by `created_on` + `farmer_project` / `farmer` |
| Push | New events via `client_id` idempotency |
| Conflict | **Server wins** — events never updated client-side |
| Mobile cache | Drift `timeline_events` keyed by `project_id` |

### 3A. Audit requirements

- Each event is an audit artifact; stage transitions also reference `Project Stage History` row.
- AgriFlow Audit Log (future) may mirror summary; timeline is operational feed.

### 3A. Suggested indexes

- `(farmer_project, created_on desc)`
- `(farmer, created_on desc)`
- `(event_type, created_on desc)`
- `(client_id)` sparse unique via service check

### 3A. Future extensibility notes

- `task_created`, `attachment_added`, `notification_sent` event types in later phases.
- Notifications and websocket delivery read from timeline — no mutation.

---

## 4. Task

### 4. Purpose

Operational **follow-up** unit: visits, calls, document collection, inspections. Generated from stage templates or created manually. Drives “nothing gets forgotten.”

### 4. Module

`Task Engine` (M6)

### 4. Naming strategy

- **Autoname:** `format:TSK-{YYYY}-{#####}`
- **Title field:** `subject`
- **Search fields:** `subject`, `farmer_project`, `assigned_to`, `due_date`

### 4. Core fields

| Field | Label |
|-------|-------|
| `subject` | Subject |
| `farmer_project` | Farmer Project |
| `farmer` | Farmer |
| `task_type` | Task Type |
| `status` | Status |
| `priority` | Priority |
| `due_date` | Due Date |
| `completed_on` | Completed On |
| `assigned_to` | Assigned To |
| `block` | Block |
| `stage_key` | Related Stage |
| `source_template` | Source Template |
| `description` | Description |
| `visit_outcome` | Visit Outcome |

### 5. Field types

| Field | Type |
|-------|------|
| `subject` | Data |
| `farmer_project` | Link → Farmer Project |
| `farmer` | Link → Farmer (fetch from project) |
| `task_type` | Select (fixture) |
| `status` | Select (fixture) |
| `priority` | Select (fixture) |
| `due_date` | Date |
| `completed_on` | Datetime |
| `assigned_to` | Link → User |
| `block` | Link → Block (denormalized for filter) |
| `stage_key` | Select (stage fixture) |
| `source_template` | Data | template id from fixture |
| `description` | Text |
| `visit_outcome` | Small Text |

### 6. Required fields

`subject`, `farmer_project`, `task_type`, `status`, `due_date`, `assigned_to`

### 7. Link relationships

| Field | Links to |
|-------|----------|
| `farmer_project` | Farmer Project |
| `farmer` | Farmer |
| `assigned_to` | User |
| `block` | Block |

### 8. Child tables

| Child | Purpose |
|-------|---------|
| `Task Checklist Item` | Optional sub-steps |

### 9. Workflow behavior

- Auto-create on stage entry via `generate_stage_tasks` from `task_template` fixture.
- Status flow: `open` → `in_progress` → `completed` | `cancelled`.
- Completing task does **not** auto-advance project stage (explicit transition).
- Overdue tasks highlighted in reports; cron reminder job.

### 10. Validation rules

- `farmer` must match `farmer_project.farmer`.
- `block` must match project `block`.
- Cannot complete task if project `status` = `cancelled`.
- `completed_on` required when `status` = `completed`.

### 11. Permissions by role

| Role | Create | Read | Write | Complete |
|------|--------|------|-------|----------|
| Owner | ✓ | all | ✓ | ✓ |
| Office Manager | ✓ | all | ✓ | ✓ |
| Office Staff | ✓ | all | ✓ | ✓ |
| Field Staff | — | assigned + block | ✓ | ✓ assigned |
| Installer | — | installation tasks | ✓ | ✓ |
| Service Tech | — | service tasks | ✓ | ✓ |
| Store Keeper | — | stock-related | limited | — |

### 12. Offline sync considerations

| Aspect | Policy |
|--------|--------|
| Create | Client wins (manual tasks) |
| Update notes/status | **LWW** `doc_version` |
| Auto-generated | Server wins on first pull after transition |
| Pull | Entity `task` filtered by `assigned_to` + `block` |

### 13. Audit requirements

- Log status changes and `assigned_to` changes.
- Log completion with `visit_outcome`.

### 14. Suggested indexes

- `(assigned_to, status, due_date)`
- `(farmer_project, status)`
- `(block, due_date)` where status != completed
- `(modified)` delta sync

### 15. Future extensibility notes

- `amc_contract` link (M7).
- WhatsApp reminder sent flag (Phase 2).

---

## 5. District

### 5. Purpose

Top-level **geographic master** for multi-district readiness. Phase 1 seeds Tiruvannamalai; additional districts added via fixtures without schema change.

### 5. Module

`Officer Network` (M8) — shared geography module

### 5. Naming strategy

- **Autoname:** `field:district_code` (e.g. `TVM`)
- **Title field:** `district_name`

### 5. Core fields

| Field | Type | Required |
|-------|------|----------|
| `district_code` | Data | ✓ |
| `district_name` | Data | ✓ |
| `state` | Data | ✓ default `Tamil Nadu` |
| `is_active` | Check | ✓ |

### 5–15. Summary tables

| # | Section | Specification |
|---|---------|---------------|
| 7 | Links | None upstream |
| 8 | Child tables | None |
| 9 | Workflow | Master; activate/deactivate only |
| 10 | Validation | Unique `district_code` |
| 11 | Permissions | Owner/Office Manager: CRUD; others: read |
| 12 | Offline | **Server wins**; Hive cache keyed by `district_code` |
| 13 | Audit | Log deactivate |
| 14 | Indexes | Unique `(district_code)` |
| 15 | Future | Link `state` → State DocType if multi-state |

**Frappe settings:** Track Changes On; Allow Import On; Rename Off.

---

## 6. Block

### 6. Purpose

Administrative block within a district (12 blocks in Phase 1). Primary **User Permission** scope for field staff.

### 6. Module

`Officer Network` (M8)

### 6. Naming strategy

- **Autoname:** `field:block_code`
- **Title field:** `block_name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `block_code` | Data | ✓ |
| `block_name` | Data | ✓ |
| `district` | Link → District | ✓ |
| `is_active` | Check | ✓ |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 7 | `district` → District |
| 8 | None |
| 9 | Master data |
| 10 | `block_code` unique within `district` |
| 11 | Owner/Office Manager: write; Field Staff: read scoped |
| 12 | Server wins; delta pull `master.blocks` |
| 13 | Track Changes |
| 14 | Index `(district, block_code)` unique |
| 15 | No hardcoded block names in code |

**Frappe settings:** Allow Import On; Rename Off.

---

## 7. Cluster

### 7. Purpose

Groups villages under an officer jurisdiction within a block. Bridge between block geography and officer assignment.

### 7. Module

`Officer Network` (M8)

### 7. Naming strategy

- **Autoname:** `field:cluster_code`
- **Title field:** `cluster_name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `cluster_code` | Data | ✓ |
| `cluster_name` | Data | ✓ |
| `block` | Link → Block | ✓ |
| `district` | Link → District | fetch |
| `is_active` | Check | ✓ |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 7 | `block` → Block; `district` denormalized/fetched |
| 8 | Optional child: village list via `Village.cluster` link (not child table) |
| 9 | Master |
| 10 | `cluster_code` unique per `block` |
| 11 | Same as Block |
| 12 | Server wins; include in master pull |
| 13 | Track Changes |
| 14 | `(block, cluster_code)` unique |
| 15 | Officer assignment references cluster, not block alone |

---

## 8. Village

### 8. Purpose

Lowest geographic unit for farmer and project location. Belongs to one cluster and block.

### 8. Module

`Officer Network` (M8)

### 8. Naming strategy

- **Autoname:** `field:village_code`
- **Title field:** `village_name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `village_code` | Data | ✓ |
| `village_name` | Data | ✓ |
| `cluster` | Link → Cluster | ✓ |
| `block` | Link → Block | ✓ |
| `district` | Link → District | fetch |
| `pincode` | Data | — |
| `is_active` | Check | ✓ |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 7 | `cluster`, `block`, `district` |
| 8 | None |
| 9 | Master |
| 10 | `cluster.block` = `block`; village code unique per block |
| 11 | All roles read; Owner/Office Manager write |
| 12 | Server wins; large fixture import |
| 13 | Track Changes |
| 14 | `(block, village_code)` unique; `(cluster)` |
| 15 | Tamil name field `village_name_ta` optional for reports (i18n display still via ARB if same string) |

---

## 9. Officer

### 9. Purpose

Government agriculture / horticulture officer master. **Current** cluster association is derived from active `Officer Assignment History`, not duplicated as authoritative truth on this DocType.

### 9. Module

`Officer Network` (M8)

### 9. Naming strategy

- **Autoname:** `field:officer_code`
- **Title field:** `officer_name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `officer_code` | Data | ✓ |
| `officer_name` | Data | ✓ |
| `department` | Select | ✓ `agriculture`, `horticulture` |
| `mobile` | Data | — |
| `email` | Data | — |
| `is_active` | Check | ✓ |
| `current_cluster` | Link → Cluster | — read-only computed |

### 7. Link relationships

- `current_cluster` — maintained by assignment service (read-only on form)

### 8. Child tables

None. Use **Officer Assignment History** DocType (not child) for append-only history.

### 9. Workflow behavior

- Officer record persists across transfers; history tracks cluster changes.
- Deactivate only if no active assignment and no open projects.

### 10. Validation rules

- `officer_code` globally unique.
- Cannot delete — only deactivate.

### 11. Permissions by role

| Role | Write |
|------|-------|
| Owner, Office Manager | ✓ |
| Others | Read |

### 12. Offline sync considerations

- Master: server wins; Hive `master_officers`.
- `current_cluster` refreshed on each master pull.

### 13. Audit requirements

- Officer create/deactivate logged.
- Assignment changes logged on **Officer Assignment History**, not by editing Officer in place.

### 14. Suggested indexes

- Unique `(officer_code)`
- `(is_active)`

### 15. Future extensibility notes

- `external_contact` merge if lead ecosystem added (ARCHITECTURE §21).

---

## 10. Officer Assignment History

### 10. Purpose

**Append-only** record of officer ↔ cluster (and village scope) over time. Supports ~3-year transfers and “as-of” reporting. Never delete rows; close with `valid_to`.

### 10. Module

`Officer Network` (M8)

### 10. Naming strategy

- **Autoname:** `hash`
- **Title:** `{officer} - {cluster} ({valid_from})`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `officer` | Link → Officer | ✓ |
| `cluster` | Link → Cluster | ✓ |
| `block` | Link → Block | fetch |
| `district` | Link → District | fetch |
| `valid_from` | Date | ✓ |
| `valid_to` | Date | — null = current |
| `assignment_reason` | Select | ✓ fixture |
| `notes` | Small Text | — |
| `is_active` | Check | computed: valid_to empty |

### 5–6. Field types / required

As above. `valid_to` must be null for at most **one** active row per `(officer, cluster)` or per cluster policy — **one active officer per cluster** at a time.

### 7. Link relationships

`officer`, `cluster`, `block`, `district`

Optional future child: `Officer Assignment Village` (`village` Link) if village-level scope required; Phase 1 cluster-level scope is sufficient.

### 8. Child tables

| Child | Phase |
|-------|-------|
| `Officer Assignment Village` | Future — only if village subset needed |

### 9. Workflow behavior

- **Transfer:** set `valid_to` = transfer date on old row; insert new row with `valid_from` = transfer date + 1 day (policy-defined).
- No UI delete; cancel only via System Manager with audit compensating entry.
- Service `OfficerAssignmentService.assign()` sole writer.

### 10. Validation rules

- `valid_to` ≥ `valid_from` when set.
- Overlapping active assignments for same `cluster` forbidden.
- Cannot close row if `valid_to` before `valid_from`.

### 11. Permissions by role

| Role | Create/close |
|------|--------------|
| Owner, Office Manager | ✓ |
| Others | Read |

### 12. Offline sync considerations

- Read-only on mobile Phase 1 (master).
- Server wins always.

### 13. Audit requirements

- **Mandatory** full audit on create and close (`valid_to` set).
- Track Changes On.

### 14. Suggested indexes

- `(cluster, valid_to)` — find current: `valid_to IS NULL`
- `(officer, valid_from)`
- `(district, modified)`

### 15. Future extensibility notes

- Village-level child without changing Officer DocType.
- Link to `External Contact` for department leads (§21).

**Frappe settings:** Allow Rename Off; Track Changes On; **Is Submittable** Off.

---

# P1 — Inventory, profit, MIMIS

Implement after P0 timeline and task engine are stable.

---

## 11. Inventory Item

### 11. Purpose

Product / material master for drip components, filters, etc. Used by stock entries and project material planning.

### 11. Module

`Inventory` (M2)

### 11. Naming strategy

- **Autoname:** `field:item_code`
- **Title field:** `item_name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `item_code` | Data | ✓ |
| `item_name` | Data | ✓ |
| `item_group` | Link / Select | — |
| `uom` | Link → UOM | ✓ default Nos |
| `is_stock_item` | Check | ✓ |
| `standard_rate` | Currency | — |
| `reorder_level` | Float | — |
| `is_active` | Check | ✓ |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 7 | Optional `item_group` → Item Group (Frappe stock) |
| 8 | None |
| 9 | Master |
| 10 | Unique `item_code` |
| 11 | Store Keeper + Owner: write; others: read |
| 12 | Server wins; Hive cache for mobile pickers |
| 13 | Price changes logged |
| 14 | Unique `(item_code)` |
| 15 | Link `supplier` future; no duplicate ERP item tables |

**Frappe settings:** Track Changes On; Allow Import On.

---

## 12. Stock Entry

### 12. Purpose

Records stock movement between **two godowns** and issue/receipt tied to operations. Supports P4 stock confusion (2 godowns).

### 12. Module

`Inventory` (M2)

### 12. Naming strategy

- **Autoname:** `naming_series:` `STE-.YYYY.-`
- **Title field:** `name`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `stock_entry_type` | Select | ✓ fixture |
| `posting_date` | Date | ✓ |
| `posting_time` | Time | — |
| `from_godown` | Select | ✓ fixture godown |
| `to_godown` | Select | conditional |
| `farmer_project` | Link | — required for `issue` to project |
| `remarks` | Small Text | — |
| `total_qty` | Float | read-only |

### 5. Child table: Stock Entry Item

| Field | Type |
|-------|------|
| `inventory_item` | Link → Inventory Item |
| `qty` | Float |
| `uom` | Link → UOM |
| `valuation_rate` | Currency |

### 6–15. Summary

| # | Specification |
|---|---------------|
| 6 | Required: `stock_entry_type`, `posting_date`, child lines ≥ 1 |
| 7 | `farmer_project` → Farmer Project (optional except project issue) |
| 9 | On save: update godown balances (bin table Phase 1 simplified: `Godown Balance` report from entries) |
| 10 | `transfer` requires `from_godown` ≠ `to_godown`; both godowns from fixture |
| 11 | Store Keeper: full; Owner: full; others: read |
| 12 | Online-preferred; mobile Store Keeper can queue with client_id |
| 13 | **Mandatory** audit — stock and profit impact |
| 14 | `(farmer_project, posting_date)`, `(from_godown, posting_date)` |
| 15 | Future link `Delivery Note`; keep normalized to project |

**Frappe settings:** Track Changes On.

---

## 13. Expense Entry

### 13. Purpose

Operational expense per farmer project for **profit visibility** (M9). Feeds `Farmer Project.total_expense` rollup.

### 13. Module

`Profit` (M9)

### 13. Naming strategy

- **Autoname:** `naming_series:` `EXP-.YYYY.-`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `farmer_project` | Link → Farmer Project | ✓ |
| `expense_date` | Date | ✓ |
| `expense_category` | Select | ✓ fixture |
| `amount` | Currency | ✓ |
| `paid_to` | Data | — |
| `payment_mode` | Select | cash, upi, bank |
| `bill_attachment` | Attach | — |
| `notes` | Small Text | — |
| `block` | Link | fetch from project |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 9 | On submit/save: recalculate project `total_expense` |
| 10 | `amount` > 0; project must be `active` |
| 11 | Owner, Office Manager: CRUD; Office Staff: create; Field Staff: — |
| 12 | Client wins create; LWW update |
| 13 | Audit mandatory — profit-sensitive |
| 14 | `(farmer_project, expense_date)` |
| 15 | Future: link `officer` expense-safe tracking (M8) |

---

## 14. MIMIS Import Batch

### 14. Purpose

Header for each **Excel reconciliation** upload. MIMIS is reconciliation-only — no government API. Tracks batch processing job.

### 14. Module

`MIMIS Sync` (M4)

### 14. Naming strategy

- **Autoname:** `naming_series:` `MIMIS-BAT-.YYYY.-`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `batch_status` | Select | ✓ fixture |
| `uploaded_file` | Attach | ✓ |
| `template_version` | Data | ✓ |
| `uploaded_by` | Link → User | ✓ |
| `uploaded_on` | Datetime | ✓ |
| `row_count` | Int | — |
| `matched_count` | Int | read-only |
| `error_log` | Long Text | — |
| `file_hash` | Data | ✓ idempotency |

### 7–15. Summary

| # | Specification |
|---|---------------|
| 7 | None |
| 8 | Child via separate DocType `MIMIS Reconciliation Row` (master-detail link) |
| 9 | Status: draft → processing → completed \| failed via job `process_mimis_import` |
| 10 | Reject duplicate `file_hash`; validate columns against template_version |
| 11 | Office Manager, Owner: create/read; others: — |
| 12 | **Online only** — not in mobile SyncQueue |
| 13 | Audit upload, completion, failure |
| 14 | Unique `(file_hash)` |
| 15 | Never store govt portal credentials |

**Frappe settings:** Track Changes On; no mobile offline.

---

## 15. MIMIS Reconciliation Row

### 15. Purpose

One row per Excel line with match outcome and approval state. Links to Farmer Project when matched.

### 15. Module

`MIMIS Sync` (M4)

### 15. Naming strategy

- **Autoname:** `hash`

### 4. Core fields

| Field | Type | Required |
|-------|------|----------|
| `mimis_import_batch` | Link → MIMIS Import Batch | ✓ |
| `row_number` | Int | ✓ |
| `row_status` | Select | ✓ fixture |
| `mimis_registration_number` | Data | — |
| `govt_farmer_id` | Data | — |
| `excel_name` | Data | — |
| `excel_mobile` | Data | — |
| `farmer_project` | Link → Farmer Project | — |
| `farmer` | Link → Farmer | — |
| `match_confidence` | Float | — |
| `approved_by` | Link → User | — |
| `approved_on` | Datetime | — |
| `rejection_reason` | Small Text | — |
| `raw_row_json` | Long Text | audit |

### 7. Link relationships

`mimis_import_batch`, `farmer_project`, `farmer`

### 9. Workflow behavior

- Created by import job only.
- Office Manager **approves** matched/ambiguous rows → may trigger `project.transition` to `mimis_registered` (human gate).
- Rejected rows remain for audit.

### 10. Validation rules

- Cannot approve if `farmer_project` null unless manual link first.
- Stage bump only if project `stage_sequence` = 3 (`documents_collected`) → 4.

### 11. Permissions by role

| Role | Approve |
|------|---------|
| Office Manager, Owner | ✓ |
| Others | Read batch results |

### 12. Offline sync considerations

- Read-only cache on mobile for status display; approve on desk/online mobile only.

### 13. Audit requirements

- **Mandatory** per approval/rejection with `before_json`/`after_json` on project stage.

### 14. Suggested indexes

- `(mimis_import_batch, row_number)` unique
- `(mimis_registration_number)`
- `(farmer_project)`
- `(row_status)`

### 15. Future extensibility notes

- Auto-match only; never auto-release subsidy from MIMIS row alone.

---

## Implementation order (recommended)

| Step | DocTypes |
|------|----------|
| 1 | District, Block, Cluster, Village, Officer, Officer Assignment History |
| 2 | Farmer |
| 3 | Farmer Project + Project Stage History (service) |
| 3A | Timeline Event + TimelineService |
| 4 | Task + task_template fixture |
| 5 | Inventory Item, Stock Entry |
| 6 | Expense Entry |
| 7 | MIMIS Import Batch, MIMIS Reconciliation Row |

---

## DocType ↔ PRD module index

| DocType | PRD | Priority |
|---------|-----|----------|
| Farmer | M1 | P0 |
| Farmer Project | M5 | P0 |
| Project Stage History | M5 | P0 |
| Timeline Event | M5 | P0 |
| Task | M6 | P0 |
| District, Block, Cluster, Village, Officer, Officer Assignment History | M8 / §10 | P0 |
| Inventory Item, Stock Entry | M2 | P1 |
| Expense Entry | M9 | P1 |
| MIMIS Import Batch, MIMIS Reconciliation Row | M4 | P1 |

---

## Change control

| Change type | Required action |
|-------------|-----------------|
| New field on Farmer Project | Architecture + PRD review if workflow impact |
| New stage | Fixture + service matrix + i18n + ARCHITECTURE §2.4 |
| New DocType | Update this file + ARCHITECTURE.md |
| Breaking mobile sync | API version bump + `min_mobile_version` |

---

*End of DOCTYPES.md*
