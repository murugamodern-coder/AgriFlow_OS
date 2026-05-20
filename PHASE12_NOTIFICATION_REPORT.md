# Phase 12 — Notification Engine Verification Report

**Site:** `dev.agriflow.local` · **Bench:** `~/workspace/frappe-bench`  
**Verified:** 2026-05-20 · **Script:** `agriflow.project_lifecycle.install.phase12_verify_notifications.execute`  
**Result:** `ok: true`, `errors: []`

---

## 1. Notification verification report

| Check | Result |
|-------|--------|
| Module **Notification Engine** + 3 DocTypes | Pass |
| Timeline fanout (`manual_note`, `task_assigned`) | Pass |
| `task_created` fanout OFF | Pass (`task_created_notification_count: 0`) |
| Duplicate fanout replay | Pass (`skipped_duplicate` in replay results) |
| `notification.unread_count` | Pass |
| `notification.mark_read` | Pass |
| `notification.list` + embedded `unread_count` | Pass |
| Notification content immutability | Pass |
| Delivery log immutability | Pass |
| Timeline safety (emit after fanout layer) | Pass |
| Not in `sync.pull` | By design |

**Commands**

```bash
cd ~/workspace/frappe-bench
bench --site dev.agriflow.local migrate
bench --site dev.agriflow.local clear-cache
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase12_sample_notifications.execute
bench --site dev.agriflow.local execute agriflow.project_lifecycle.install.phase12_verify_notifications.execute
```

**Sample verify output**

```json
{
  "timeline_event": "aec1d9kun7",
  "notifications_for_event": 1,
  "duplicate_fanout_count": 1,
  "replay_results": [{"status": "skipped_duplicate", "name": "aedn0il3al", "recipient": "Administrator"}],
  "unread_before": 7,
  "marked_read": true,
  "unread_after_mark": 6,
  "list_ok": true,
  "task_assigned_notifications": 1,
  "delivery_log_immutable": true,
  "notification_content_immutable": true,
  "task_created_notification_count": 0,
  "ok": true
}
```

---

## 2. Sample notifications

**API list item shape**

```json
{
  "name": "aedn0il3al",
  "notification_type": "manual_note",
  "title_i18n_key": "notification.manual_note.title",
  "body_preview": "Phase 12 verify note … — FP-2026-00007",
  "payload": {
    "farmer_project": "FP-2026-00007",
    "deep_link": "/projects/FP-2026-00007/timeline",
    "text": "Phase 12 verify note …"
  },
  "priority": "normal",
  "read": false,
  "created_on": "2026-05-20T…",
  "timeline_event": "aec1d9kun7"
}
```

**Types enabled (fanout)**

| `notification_type` | Source |
|---------------------|--------|
| `task_assigned` / `task_reassigned` | Timeline `task_assigned` (+ assignment history) |
| `task_completed` | Timeline `task_completed` |
| `project_stage_changed` | Timeline `stage_transition` |
| `manual_note` | Timeline `manual_note` |
| `system_alert` | Timeline `mimis_gate_updated`, `project_status_changed` |
| `task_overdue` | Scheduler `scan_task_overdue_notifications` (foundation) |

---

## 3. Fanout proof

- `TimelineService.emit()` inserts row, then calls `deliver_for_timeline_event(event_id)` inside **try/except** (errors logged, timeline never rolled back).
- Idempotent timeline replay also re-invokes fanout; dedupe returns `skipped_duplicate` without new Notification rows.
- Verified: `notifications_for_event: 1` after `manual_note`; `task_assigned_notifications: 1` after assign.

---

## 4. Duplicate-prevention proof

- Unique `delivery_key` = SHA-256(`timeline_event|notification_type|recipient`) (or task/day key for SLA).
- Immutable **Notification Delivery Log** records first delivery; subsequent attempts return `skipped_duplicate`.
- Verified: second `deliver_for_timeline_event(eid)` → `replay_results: [{status: skipped_duplicate, …}]`, `duplicate_fanout_count` unchanged.

---

## 5. Mobile inbox integration notes

| Topic | Guidance |
|-------|----------|
| **Not in sync.pull** | Poll `notification.unread_count` on app resume + after `sync.push`; refresh inbox via `notification.list`. |
| **Badge** | `data.count` from `unread_count`. |
| **List** | `notification.list` with `unread_only`, `cursor`, `limit`; use `data.unread_count` in same response. |
| **Read** | `notification.mark_read` with `{name}` or `{names:[]}`; `mark_all_read` for clear-all. |
| **i18n** | Render `title_i18n_key` via ARB; `body_preview` is optional fallback only. |
| **Navigation** | `payload.deep_link` → go_router. |
| **Offline** | Inbox is server-authoritative online; cache last list in Drift optional in later phase. |

**Endpoints**

- `agriflow.api.v1.notification.list`
- `agriflow.api.v1.notification.unread_count`
- `agriflow.api.v1.notification.mark_read`
- `agriflow.api.v1.notification.mark_all_read`

---

## 6. Scalability notes

| Area | Approach |
|------|----------|
| Indexes | `(recipient, read_on)`, unique `delivery_key`, timeline link |
| Fanout | Synchronous per event; bounded recipients per block |
| Inbox query | Keyset pagination on `(created_on, name)` |
| Block scope | `get_allowed_blocks()` on list (empty scope → empty inbox) |
| Growth | Append-only notifications + delivery log; archival job future |
| Noise control | `task_created` fanout off; per-type **Notification Preference** JSON |

---

## 7. SLA alert foundation notes

- Scheduler (`hooks.py` daily): `agriflow.notification_engine.services.sla_alerts.scan_task_overdue_notifications`
- Scans open tasks with `due_date < today`; `delivery_key` includes task + date + recipient (one per day).
- Uses `task_overdue` type, `source_doctype=Project Task`, no timeline mutation required.
- Full WhatsApp/Evolution integration remains future (ARCHITECTURE §11).

---

## 8. Timeline safety proof

- Fanout wrapped in `try/except`; failures logged with title `notification.fanout`.
- Timeline `insert` completes before fanout; verified `timeline_safety_event` created after fanout layer active.
- Fanout exceptions do not propagate to `emit()` caller.

---

## 9. Delivery-log immutability proof

- `Notification Delivery Log.validate` / `on_update` reject updates outside service flag.
- Verify attempted `log.save()` → blocked; `processed_on` unchanged.
- **Notification** content fields reject saves except `read_on` / `is_deleted` via controller + `NOTIFICATION_FLAG`.

---

## Implementation map

```
apps/agriflow/agriflow/
  notification_engine/
    doctype/{notification,notification_preference,notification_delivery_log}/
    services/{delivery,fanout,recipients,preferences,unread,sla_alerts,i18n_keys}.py
    api/serializers.py
  api/v1/notification.py
  project_lifecycle/services/timeline.py   # fanout hook
  project_lifecycle/install/phase12_{sample,verify}_notifications.py
```

Windows mirrors: `AgriFlow_OS/scripts/phase12_*.py`

**Roadmap:** Inventory moved to **Phase 13** in `IMPLEMENTATION_PLAN.md`.
