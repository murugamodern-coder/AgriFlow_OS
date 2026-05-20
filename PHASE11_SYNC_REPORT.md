# Phase 11 — Sync Engine Verification Report

**Site:** `dev.agriflow.local` · **Bench:** `~/workspace/frappe-bench`  
**Verified:** 2026-05-20 · **Script:** `agriflow.project_lifecycle.install.phase11_verify_sync.execute`  
**Result:** `ok: True`, `errors: []`

---

## 1. Sync verification report

| Check | Result |
|-------|--------|
| `sync.pull` — entities `timeline`, `task`, `farmer_project` | Pass |
| Keyset cursor continuation (task, no overlap) | Pass |
| Server watermarks (`timeline` → `created_on`; `task` / `farmer_project` → `modified`) | Pass |
| `sync.push` — task create + replay (`client_mutation_id`) | Pass — `status: skipped`, `replay: true`, 1 mutation log row |
| Partial batch — note success + stale task update conflict | Pass — `SYNC_PARTIAL_FAILURE`, HTTP 207 |
| Timeline `note` push | Pass |
| `farmer_project` update via sync blocked | Pass — op `failed`, lifecycle server-authoritative |
| Farmer entity | Not in Phase 11 (by design) |
| `project.transition` via sync | Not implemented (by design) |

**Fixes applied during verification**

- `sync_token` set via `set_new_name()` + `validate()` (DocType field no longer blocks insert).
- API `pull()` aliased service as `run_pull` (removed infinite recursion).
- Replay: skip second `Sync Mutation Log` insert; `find_prior()` works without `response_json`; `record()` no-ops if log exists.
- Verify script uses per-run mutation IDs (`run_id` hash) to avoid stale replay from prior runs.

**Run verification**

```bash
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase11_verify_sync.execute
```

**Sample verify output**

```json
{
  "pull_ok": true,
  "sync_token_pull": "SS-2026-00041",
  "pull_task_page1": 2,
  "task_cursor_overlap": [],
  "watermarks": {
    "timeline": "2026-05-20T15:49:14.575312",
    "task": "2026-05-20T16:21:03.584348",
    "farmer_project": "2026-05-20T16:23:33.396665"
  },
  "replay_status": "skipped",
  "replay_flag": true,
  "mutation_log_count": 1,
  "stale_partial_ok": true,
  "stale_partial_code": "SYNC_PARTIAL_FAILURE",
  "stale_http": 207,
  "stale_summary": { "success": 1, "conflict": 1, "failed": 0, "skipped": 0 },
  "stale_statuses": ["success", "conflict"],
  "ok": true,
  "errors": []
}
```

---

## 2. Example `sync.pull` payload

**Request** — `POST /api/method/agriflow.api.v1.sync.pull`

```json
{
  "entities": ["timeline", "task", "farmer_project"],
  "modified_since": {
    "timeline": "2026-05-20T10:00:00",
    "task": "2026-05-20T12:00:00",
    "farmer_project": "2026-05-20T12:00:00"
  },
  "limits": { "timeline": 50, "task": 25, "farmer_project": 25 },
  "cursors": { "task": "PT-2026-00012" },
  "device_id": "tablet-abc-001"
}
```

**Response** — HTTP `200`, envelope `ok: true`

```json
{
  "ok": true,
  "data": {
    "sync_token": "SS-2026-00041",
    "generated_at": "2026-05-20T16:52:00.123456",
    "server_watermark": {
      "timeline": "2026-05-20T15:49:14.575312",
      "task": "2026-05-20T16:21:03.584348",
      "farmer_project": "2026-05-20T16:23:33.396665"
    },
    "entities": {
      "timeline": {
        "items": [
          {
            "name": "0m69vlkvi5",
            "farmer_project": "FP-2026-00007",
            "event_type": "note",
            "created_on": "2026-05-20T15:49:14.575312",
            "payload": { "text": "Field note" }
          }
        ],
        "deleted": [],
        "cursor": "0m69vlkvi5",
        "has_more": false
      },
      "task": {
        "items": [
          {
            "name": "PT-2026-00015",
            "subject": "Follow up",
            "farmer_project": "FP-2026-00007",
            "doc_version": 2,
            "modified": "2026-05-20T16:21:03.584348"
          }
        ],
        "deleted": [],
        "cursor": "PT-2026-00015",
        "has_more": true
      },
      "farmer_project": {
        "items": [
          {
            "name": "FP-2026-00007",
            "current_stage": "field_survey",
            "doc_version": 4,
            "modified": "2026-05-20T16:23:33.396665"
          }
        ],
        "deleted": [],
        "cursor": "FP-2026-00007",
        "has_more": false
      }
    }
  },
  "server_time": "2026-05-20T16:52:00",
  "request_id": "…"
}
```

**Watermark rules**

| Entity | Incremental field | Notes |
|--------|-------------------|--------|
| `timeline` | `created_on` | Immutable; keyset `(created_on, name)` |
| `task` | `modified` | Keyset `(modified, name)` |
| `farmer_project` | `modified` | Keyset `(modified, name)`; tombstones in `deleted` when `include_deleted` |

---

## 3. Example `sync.push` payload

**Request** — `POST /api/method/agriflow.api.v1.sync.push`

```json
{
  "device_id": "tablet-abc-001",
  "operations": [
    {
      "client_mutation_id": "550e8400-e29b-41d4-a716-446655440000",
      "entity": "task",
      "op_type": "create",
      "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "payload": {
        "subject": "Collect land documents",
        "farmer_project": "FP-2026-00007",
        "task_type": "document_collection",
        "due_date": "2026-06-15",
        "priority": "high"
      }
    },
    {
      "client_mutation_id": "661e8400-e29b-41d4-a716-446655440001",
      "entity": "timeline",
      "op_type": "note",
      "client_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "payload": {
        "farmer_project": "FP-2026-00007",
        "text": "Farmer visited; papers pending"
      }
    }
  ]
}
```

**Response** — HTTP `200` when all ops succeed

```json
{
  "ok": true,
  "data": {
    "sync_token": "SS-2026-00042",
    "results": [
      {
        "client_mutation_id": "550e8400-e29b-41d4-a716-446655440000",
        "entity": "task",
        "op_type": "create",
        "status": "success",
        "name": "PT-2026-00099",
        "doc_version": 1,
        "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "task": { }
      },
      {
        "client_mutation_id": "661e8400-e29b-41d4-a716-446655440001",
        "entity": "timeline",
        "op_type": "note",
        "status": "success",
        "name": "0m69vlkvi5",
        "client_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
      }
    ],
    "summary": {
      "success": 2,
      "conflict": 0,
      "failed": 0,
      "skipped": 0,
      "dependency_failed": 0
    }
  }
}
```

**Supported push matrix (Phase 11)**

| entity | op_type | Handler |
|--------|---------|---------|
| `task` | `create`, `update`, `complete` | Task Engine services |
| `timeline` | `note`, `create` | `TimelineService.emit(..., event_source="mobile")` |
| `farmer_project` | any | Rejected — use desk / lifecycle API |

Public mutation key: **`client_mutation_id` only** (no `op_id` in API).

---

## 4. Conflict examples

**Stale `doc_version` (LWW)** — second op in a partial batch:

```json
{
  "client_mutation_id": "phase11-stale-fail-…",
  "entity": "task",
  "op_type": "update",
  "status": "conflict",
  "conflict": {
    "type": "lww_version_mismatch",
    "resolution": "server_payload",
    "server": {
      "name": "PT-2026-00120",
      "doc_version": 2,
      "modified": "2026-05-20 16:52:00",
      "fields": { }
    },
    "client": { "doc_version": 0 },
    "message": "Stale doc_version. Server has 2, client sent 0"
  }
}
```

**Partial batch envelope** — HTTP `207`, `ok: true`, top-level:

```json
{
  "error": {
    "code": "SYNC_PARTIAL_FAILURE",
    "message": "Batch partially applied",
    "details": { "success": 1, "conflict": 1, "failed": 0, "skipped": 0 }
  }
}
```

**Blocked lifecycle push**

```json
{
  "client_mutation_id": "phase11-no-transition-…",
  "entity": "farmer_project",
  "op_type": "update",
  "status": "failed",
  "error": {
    "code": "VAL_INVALID",
    "message": "project.transition is not available via sync in Phase 11"
  }
}
```

---

## 5. Replay-safety proof

**Mechanism**

1. Immutable `Sync Mutation Log` — unique `client_mutation_id` (length 36).
2. Before processing: `find_prior(client_mutation_id)` returns stored `response_json`.
3. On replay: result returned with `status: "skipped"`, `replay: true`; **no second log insert**.

**Verified**

- First push: `status: success`, task name recorded.
- Second push (same `client_mutation_id`): `status: skipped`, `replay: true`, same `name`.
- `frappe.db.count("Sync Mutation Log", {"client_mutation_id": cmid}) === 1`.

---

## 6. Offline mobile integration notes

| Topic | Guidance |
|-------|----------|
| Write path | Queue mutations in Drift `SyncQueue` with `client_mutation_id` (UUID); flush via `sync.push`. |
| Read path | After successful push (or on schedule), `sync.pull` with stored `modified_since` / `server_watermark` per entity. |
| Watermarks | Persist `server_watermark.timeline` (`created_on`), `.task` / `.farmer_project` (`modified`) in Drift sync state table. |
| HTTP | Treat `207` + `SYNC_PARTIAL_FAILURE` as success with per-op reconciliation; retry only failed/conflict ops with new versions. |
| Conflicts | On `conflict`, apply `server.fields` to local Drift row; bump local `doc_version`; optionally re-queue user edit. |
| Creates | Always send `client_id` (UUID) on task/timeline creates for idempotent server mapping. |
| Lifecycle | Stage changes: online desk or dedicated `project.transition` API — **not** sync push. |
| Farmer | Not in Phase 11 pull/push; add in later phase. |
| i18n | Display `error.message` keys via app i18n; no hardcoded Tamil in payloads. |

Suggested Flutter flow: `SyncWorker` → push batch → if partial, update queue rows → pull entities → merge into Drift → update Hive masters separately (masters not in Phase 11 pull set).

---

## 7. Scalability / performance notes

| Area | Approach |
|------|----------|
| Pull paging | Per-entity `limits` (max 100); keyset cursors avoid `OFFSET`. |
| Push batching | Ops grouped by `farmer_project` for serial ordering within project; global ops last. |
| Indexes | `Sync Mutation Log.client_mutation_id` unique + search index; task/project `modified` indexed. |
| Sessions | `Sync Session` audit row per pull/push (watermarks in/out JSON). |
| Scope | `get_allowed_blocks()` filters timeline/tasks/projects — same RBAC as REST APIs. |
| Hot path | No full-table scans; timeline uses existing `TimelineService.query`. |
| Growth | Mutation log append-only; archive old sessions/logs by retention job (future ops). |

---

## 8. Partial-batch-failure proof

**Test:** One timeline `note` (success) + one task `update` with `doc_version = server - 1` (conflict).

**Observed**

- `stale_statuses`: `["success", "conflict"]`
- `stale_summary`: `{ "success": 1, "conflict": 1, … }`
- `stale_partial_code`: `SYNC_PARTIAL_FAILURE`
- `stale_http`: `207`
- First op applied; second returned conflict payload without rolling back the first (batch is not transactional).

---

## 9. Cursor continuation proof

**Test:** `sync.pull` tasks `limit: 2` → read `cursor` → second pull with `cursors.task`.

**Observed**

- `pull_task_page1`: 2
- `task_cursor_overlap`: `[]` (no duplicate IDs across pages)
- `has_more` respected on first page when more rows exist

Timeline cursor uses `(created_on, name)`; tasks/projects use `(modified, name)`.

---

## Implementation map (WSL)

```
apps/agriflow/agriflow/
  api/v1/sync.py
  sync_engine/
    doctype/sync_session/
    doctype/sync_mutation_log/
    services/{session,idempotency,pull,push}.py
    services/handlers/{task,timeline}.py
    api/serializers.py
  project_lifecycle/install/phase11_verify_sync.py
```

Windows script mirrors: `AgriFlow_OS/scripts/phase11_*.py`
