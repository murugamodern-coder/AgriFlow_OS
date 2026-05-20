#!/usr/bin/env python3
"""Phase 9b — Project Timeline API layer bootstrap."""
from __future__ import annotations

from pathlib import Path

APP = Path("/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow")
CONTRACTS = Path(
    "/mnt/c/Users/murug/OneDrive/Desktop/DOCUMENT/Projects/AgriFlow_OS/API_CONTRACTS.md"
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(APP.parent)}")


def patch_timeline_service() -> None:
    write(
        APP / "project_lifecycle" / "services" / "timeline.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Unified timeline activity stream — append-only Timeline Event rows."""

from __future__ import annotations

import json
from typing import Any, Literal

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.utils import cstr, get_fullname, now_datetime

TIMELINE_FLAG = "agriflow_timeline_write"
MAX_NOTE_LEN = 2000
MAX_PAYLOAD_KEYS = 32
VALID_EVENT_TYPES = frozenset(
	{
		"project_created",
		"stage_transition",
		"mimis_gate_updated",
		"project_status_changed",
		"manual_note",
	}
)


class TimelineService:
	def emit(
		self,
		event_type: str,
		farmer_project: str,
		*,
		payload: dict | None = None,
		event_source: str = "lifecycle",
		reference_doctype: str | None = None,
		reference_name: str | None = None,
		client_id: str | None = None,
		created_on: str | None = None,
		actor: str | None = None,
		skip_idempotency: bool = False,
	) -> str:
		"""Insert one immutable timeline event; returns event name."""
		self._validate_payload(payload)
		project = frappe.db.get_value(
			"Farmer Project",
			farmer_project,
			["farmer", "district", "block", "name"],
			as_dict=True,
		)
		if not project:
			frappe.throw(_("Farmer Project not found"))

		if client_id and not skip_idempotency:
			existing = frappe.db.exists(
				"Timeline Event",
				{
					"client_id": client_id,
					"event_type": event_type,
					"farmer_project": farmer_project,
					"is_deleted": 0,
				},
			)
			if existing:
				return existing

		actor = actor or frappe.session.user
		actor_name = get_fullname(actor) or actor

		doc = frappe.get_doc(
			{
				"doctype": "Timeline Event",
				"farmer_project": farmer_project,
				"farmer": project.farmer,
				"event_type": event_type,
				"event_source": event_source,
				"created_on": created_on or now_datetime(),
				"actor": actor,
				"actor_name": actor_name,
				"payload_json": payload or {},
				"reference_doctype": reference_doctype,
				"reference_name": reference_name,
				"district": project.district,
				"block": project.block,
				"client_id": client_id,
				"is_deleted": 0,
			}
		)
		frappe.flags[TIMELINE_FLAG] = True
		try:
			doc.insert(ignore_permissions=True)
		finally:
			frappe.flags[TIMELINE_FLAG] = False
		return doc.name

	def query(
		self,
		*,
		farmer_project: str | None = None,
		farmer: str | None = None,
		event_types: list[str] | None = None,
		since: str | None = None,
		since_exclusive: bool = False,
		limit: int = 50,
		cursor: str | None = None,
		order: Literal["desc", "asc"] = "desc",
	) -> dict[str, Any]:
		"""Keyset pagination on (created_on, name). Raw cursor = event name."""
		limit = min(max(int(limit or 50), 1), 100)
		if event_types:
			invalid = [e for e in event_types if e not in VALID_EVENT_TYPES]
			if invalid:
				frappe.throw(_("Invalid event_types: {0}").format(", ".join(invalid)))

		te = frappe.qb.DocType("Timeline Event")
		q = (
			frappe.qb.from_(te)
			.select(
				te.name,
				te.farmer_project,
				te.farmer,
				te.event_type,
				te.event_source,
				te.created_on,
				te.actor,
				te.actor_name,
				te.payload_json,
				te.reference_doctype,
				te.reference_name,
				te.client_id,
			)
			.where(te.is_deleted == 0)
		)

		if farmer_project:
			q = q.where(te.farmer_project == farmer_project)
		if farmer:
			q = q.where(te.farmer == farmer)
		if event_types:
			q = q.where(te.event_type.isin(event_types))
		if since:
			if since_exclusive:
				q = q.where(te.created_on > since)
			else:
				q = q.where(te.created_on >= since)

		if cursor:
			cursor_row = frappe.db.get_value(
				"Timeline Event",
				cursor,
				["created_on", "name"],
				as_dict=True,
			)
			if cursor_row:
				if order == "desc":
					q = q.where(
						(te.created_on < cursor_row.created_on)
						| (
							(te.created_on == cursor_row.created_on)
							& (te.name < cursor_row.name)
						)
					)
				else:
					q = q.where(
						(te.created_on > cursor_row.created_on)
						| (
							(te.created_on == cursor_row.created_on)
							& (te.name > cursor_row.name)
						)
					)

		if order == "desc":
			q = q.orderby(te.created_on, order=Order.desc).orderby(te.name, order=Order.desc)
		else:
			q = q.orderby(te.created_on, order=Order.asc).orderby(te.name, order=Order.asc)

		rows = q.limit(limit + 1).run(as_dict=True)

		next_cursor = None
		has_more = len(rows) > limit
		if has_more:
			rows = rows[:limit]
			next_cursor = rows[-1].name

		return {
			"items": [self.to_mobile_event(r) for r in rows],
			"next_cursor": next_cursor,
			"has_more": has_more,
			"limit": limit,
		}

	def build_project_feed(self, farmer_project: str, *, limit: int = 100) -> list[dict[str, Any]]:
		result = self.query(farmer_project=farmer_project, limit=limit)
		return result["items"]

	def to_mobile_event(self, row) -> dict[str, Any]:
		payload = row.payload_json
		if isinstance(payload, str):
			try:
				payload = json.loads(payload)
			except json.JSONDecodeError:
				payload = {}
		if not isinstance(payload, dict):
			payload = {}
		created_on = row.created_on
		if hasattr(created_on, "isoformat"):
			created_on = created_on.isoformat()
		return {
			"id": row.name,
			"event_type": row.event_type,
			"event_source": row.event_source,
			"created_on": created_on,
			"actor": {"user": row.actor, "display_name": row.actor_name or row.actor},
			"farmer_project": row.farmer_project,
			"farmer": row.farmer,
			"payload": payload,
			"reference": {
				"doctype": row.reference_doctype,
				"name": row.reference_name,
			},
			"client_id": row.client_id,
		}

	def emit_project_created(self, project) -> str:
		return self.emit(
			"project_created",
			project.name,
			payload={
				"project_type": project.project_type,
				"current_stage": project.current_stage,
				"stage_sequence": project.stage_sequence,
			},
			event_source=project.created_via or "lifecycle",
			reference_doctype="Farmer Project",
			reference_name=project.name,
			client_id=f"{project.client_id}-created" if project.client_id else None,
		)

	def emit_stage_transition(
		self,
		project,
		*,
		from_stage: str,
		to_stage: str,
		from_sequence: int,
		to_sequence: int,
		history_row_name: str | None,
		notes: str | None = None,
		client_id: str | None = None,
		actor: str | None = None,
		created_on: str | None = None,
	) -> str:
		return self.emit(
			"stage_transition",
			project.name,
			payload={
				"from_stage": from_stage or "",
				"to_stage": to_stage,
				"from_sequence": from_sequence,
				"to_sequence": to_sequence,
				"history_row": history_row_name,
				"notes": (notes or "")[:MAX_NOTE_LEN],
			},
			event_source="lifecycle",
			reference_doctype="Project Stage History",
			reference_name=history_row_name,
			client_id=client_id,
			actor=actor,
			created_on=created_on,
		)

	def emit_mimis_gate_updated(
		self,
		project_name: str,
		*,
		from_status: str,
		to_status: str,
		mimis_reconciliation_ref: str | None = None,
	) -> str:
		return self.emit(
			"mimis_gate_updated",
			project_name,
			payload={
				"from_status": from_status,
				"to_status": to_status,
				"mimis_reconciliation_ref": mimis_reconciliation_ref,
			},
			event_source="mimis",
		)

	def emit_project_status_changed(
		self,
		project_name: str,
		*,
		from_status: str,
		to_status: str,
		current_stage: str,
		stage_sequence: int,
	) -> str:
		return self.emit(
			"project_status_changed",
			project_name,
			payload={
				"from_status": from_status,
				"to_status": to_status,
				"current_stage": current_stage,
				"stage_sequence": stage_sequence,
			},
			event_source="lifecycle",
		)

	def emit_manual_note(self, farmer_project: str, text: str, *, client_id: str | None = None) -> str:
		return self.emit(
			"manual_note",
			farmer_project,
			payload={"text": cstr(text)[:MAX_NOTE_LEN], "visibility": "internal"},
			event_source="desk",
			client_id=client_id,
		)

	def _validate_payload(self, payload: dict | None) -> None:
		if not payload:
			return
		if len(payload) > MAX_PAYLOAD_KEYS:
			frappe.throw(_("Timeline payload has too many keys"))
		encoded = json.dumps(payload, default=str)
		if len(encoded) > 8000:
			frappe.throw(_("Timeline payload is too large"))


def get_timeline_service() -> TimelineService:
	return TimelineService()
''',
    )


def write_api_layer() -> None:
    write(APP / "api" / "__init__.py", "")
    write(APP / "api" / "v1" / "__init__.py", "")
    write(
        APP / "api" / "v1" / "response.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""API_CONTRACTS §5 — standard success/error envelope."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime


def _request_id() -> str:
	return frappe.flags.get("request_id") or frappe.generate_hash(length=12)


def success(data: Any) -> dict[str, Any]:
	return {
		"ok": True,
		"data": data,
		"error": None,
		"server_time": now_datetime().isoformat(),
		"request_id": _request_id(),
	}


def fail(code: str, message: str, *, http_status: int = 400, details: dict | None = None) -> dict[str, Any]:
	frappe.local.response["http_status_code"] = http_status
	return {
		"ok": False,
		"data": None,
		"error": {"code": code, "message": message, "details": details or {}},
		"server_time": now_datetime().isoformat(),
		"request_id": _request_id(),
	}


def parse_data(data: Any) -> dict:
	if data is None:
		return {}
	if isinstance(data, str):
		import json

		return json.loads(data) if data else {}
	if isinstance(data, dict):
		return data
	return {}
''',
    )
    write(
        APP / "api" / "v1" / "errors.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""API error codes — API_CONTRACTS §6."""

from __future__ import annotations

import frappe

from agriflow.api.v1.response import fail

NOT_FOUND = "NOT_FOUND"
PERM_DENIED = "PERM_DENIED"
VAL_INVALID = "VAL_INVALID"
VAL_INVALID_CURSOR = "VAL_INVALID_CURSOR"


def throw_not_found(message: str = "Resource not found"):
	frappe.throw(message, exc=frappe.DoesNotExistError)


def throw_perm(message: str = "Permission denied"):
	frappe.throw(message, exc=frappe.PermissionError)


def throw_validation(message: str):
	frappe.throw(message, exc=frappe.ValidationError)
''',
    )
    write(
        APP / "api" / "v1" / "permissions.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Session-based scope checks; JWT stub for Phase 3/5."""

from __future__ import annotations

import frappe
from frappe import _

BYPASS_ROLES = frozenset({"Administrator", "System Manager"})


def ensure_authenticated() -> None:
	"""Require logged-in session. JWT Bearer validation is a future hook."""
	if frappe.session.user in ("Guest", ""):
		frappe.throw(_("Authentication required"), exc=frappe.AuthenticationError)
	# Phase 3/5: parse Authorization Bearer and validate JWT here.


def get_allowed_blocks() -> set[str] | None:
	"""Return None if unrestricted; else set of block codes."""
	if set(frappe.get_roles()) & BYPASS_ROLES:
		return None
	perms = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "Block"},
		pluck="for_value",
	)
	return set(perms) if perms else set()


def assert_project_access(project_name: str) -> dict:
	ensure_authenticated()
	if not frappe.db.exists("Farmer Project", {"name": project_name, "is_deleted": 0}):
		frappe.throw(_("Farmer Project not found"), exc=frappe.DoesNotExistError)

	project = frappe.db.get_value(
		"Farmer Project",
		project_name,
		[
			"name",
			"farmer",
			"current_stage",
			"stage_sequence",
			"status",
			"doc_version",
			"block",
			"cluster",
			"village",
			"officer",
			"mimis_gate_status",
			"modified",
		],
		as_dict=True,
	)
	allowed = get_allowed_blocks()
	if allowed is not None and project.block not in allowed:
		frappe.throw(_("Not permitted for block {0}").format(project.block), exc=frappe.PermissionError)
	return project


def assert_farmer_timeline_access(farmer: str) -> None:
	ensure_authenticated()
	if not frappe.db.exists("Farmer", farmer):
		frappe.throw(_("Farmer not found"), exc=frappe.DoesNotExistError)
	allowed = get_allowed_blocks()
	if allowed is None:
		return
	block = frappe.db.get_value("Farmer", farmer, "block")
	if block and block not in allowed:
		frappe.throw(_("Not permitted for farmer block"), exc=frappe.PermissionError)
''',
    )
    write(
        APP / "api" / "v1" / "project.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Farmer Project API — timeline read endpoints (API_CONTRACTS §15)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import assert_farmer_timeline_access, assert_project_access, ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map

MIMIS_GATE_APPROVED = frozenset({"approved", "waived"})


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _project_summary(project: dict) -> dict[str, Any]:
	return {
		"name": project.name,
		"farmer": project.farmer,
		"current_stage": project.current_stage,
		"stage_sequence": project.stage_sequence,
		"status": project.status,
		"doc_version": project.doc_version,
		"block": project.block,
		"cluster": project.cluster,
		"village": project.village,
		"officer": project.officer,
		"modified": _iso(project.modified),
	}


def _slim_stage_history(project_name: str) -> list[dict[str, Any]]:
	rows = frappe.get_all(
		"Project Stage History",
		filters={"parent": project_name},
		fields=[
			"name",
			"from_stage",
			"to_stage",
			"from_sequence",
			"to_sequence",
			"transitioned_on",
			"transitioned_by",
			"notes",
			"is_correction",
		],
		order_by="to_sequence asc",
	)
	for row in rows:
		row["transitioned_on"] = _iso(row.transitioned_on)
		row["attachment_file_id"] = None
	return rows


def _workflow_meta(project: dict) -> dict[str, Any]:
	blocking: list[str] = []
	next_stage = get_next_stage_key(project.current_stage)
	can_transition = False

	if project.status != "active":
		blocking.append(_("Project status is {0}").format(project.status))
	elif not next_stage:
		blocking.append(_("No further stages"))
	else:
		can_transition = True
		if next_stage == "mimis_registered" and (project.mimis_gate_status or "pending") not in MIMIS_GATE_APPROVED:
			can_transition = False
			blocking.append(_("MIMIS gate not approved"))

	stage_map = get_stage_map()
	i18n_key = None
	if next_stage and next_stage in stage_map:
		i18n_key = stage_map[next_stage].label_i18n_key

	return {
		"next_stage": next_stage,
		"next_stage_i18n_key": i18n_key,
		"can_transition": can_transition,
		"allowed_roles": [],
		"blocking_reasons": [str(b) for b in blocking],
	}


@frappe.whitelist()
def timeline(data=None):
	"""agriflow.api.v1.project.timeline — project screen feed."""
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail("VAL_INVALID", _("name is required"))

		project = assert_project_access(name)
		timeline_svc = get_timeline_service()
		feed = timeline_svc.query(
			farmer_project=name,
			event_types=payload.get("event_types"),
			limit=payload.get("limit", 25),
			cursor=payload.get("cursor"),
			order="desc",
		)

		return success(
			{
				"project": _project_summary(project),
				"timeline": {
					"items": feed["items"],
					"next_cursor": feed["next_cursor"],
					"has_more": feed["has_more"],
					"generated_at": now_datetime().isoformat(),
				},
				"stage_history": _slim_stage_history(name),
				"open_tasks": [],
				"workflow": _workflow_meta(project),
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)


@frappe.whitelist()
def timeline_since(data=None):
	"""agriflow.api.v1.project.timeline_since — delta timeline for sync replay."""
	try:
		payload = parse_data(data)
		project = payload.get("project")
		farmer = payload.get("farmer")
		since = payload.get("since")

		if not project and not farmer:
			return fail("VAL_INVALID", _("project or farmer is required"))
		if not since:
			return fail("VAL_INVALID", _("since is required"))

		if project:
			assert_project_access(project)
		if farmer:
			assert_farmer_timeline_access(farmer)

		timeline_svc = get_timeline_service()
		feed = timeline_svc.query(
			farmer_project=project,
			farmer=farmer,
			event_types=payload.get("event_types"),
			since=since,
			since_exclusive=True,
			limit=payload.get("limit", 50),
			cursor=payload.get("cursor"),
			order="asc",
		)

		return success(
			{
				"items": feed["items"],
				"next_cursor": feed["next_cursor"],
				"has_more": feed["has_more"],
				"generated_at": now_datetime().isoformat(),
				"since": since,
				"deleted": [],
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
''',
    )


def write_verify_script() -> None:
    write(
        APP / "project_lifecycle" / "install" / "phase9b_verify_api.py",
        '''# Copyright (c) 2026, Murugan and contributors
"""Verify project.timeline and project.timeline_since APIs."""

PROJECT = "FP-2026-00007"
FARMER = "FR-00001"


def execute():
	import frappe

	from agriflow.api.v1 import project as project_api
	from agriflow.project_lifecycle.services.timeline import get_timeline_service

	frappe.set_user("Administrator")
	errors = []
	proof = {}

	# --- timeline aggregate ---
	page1 = project_api.timeline({"name": PROJECT, "limit": 2})
	if not page1.get("ok"):
		errors.append(f"timeline failed: {page1}")
	else:
		data1 = page1["data"]
		proof["timeline_page1_count"] = len(data1["timeline"]["items"])
		proof["timeline_has_more_p1"] = data1["timeline"]["has_more"]
		proof["timeline_has_stage_history"] = len(data1.get("stage_history", [])) >= 1
		proof["timeline_has_project"] = data1.get("project", {}).get("name") == PROJECT
		cursor = data1["timeline"]["next_cursor"]
		if cursor:
			page2 = project_api.timeline({"name": PROJECT, "limit": 2, "cursor": cursor})
			if not page2.get("ok"):
				errors.append("timeline page2 failed")
			else:
				ids1 = {i["id"] for i in data1["timeline"]["items"]}
				ids2 = {i["id"] for i in page2["data"]["timeline"]["items"]}
				if ids1 & ids2:
					errors.append("timeline cursor overlap between pages")
				proof["timeline_page2_count"] = len(ids2)

	# --- event_types filter ---
	filtered = project_api.timeline(
		{"name": PROJECT, "event_types": ["manual_note"], "limit": 20}
	)
	if filtered.get("ok"):
		types = {i["event_type"] for i in filtered["data"]["timeline"]["items"]}
		if types - {"manual_note"}:
			errors.append(f"event_types filter leaked: {types}")
		proof["filter_manual_note_count"] = len(types)

	# --- timeline_since ASC replay ---
	since = "2026-05-20T00:00:00"
	delta = project_api.timeline_since({"project": PROJECT, "since": since, "limit": 50})
	if not delta.get("ok"):
		errors.append(f"timeline_since failed: {delta}")
	else:
		items = delta["data"]["items"]
		proof["since_item_count"] = len(items)
		times = [i["created_on"] for i in items]
		if times != sorted(times):
			errors.append("timeline_since not ASC ordered")
		proof["since_ordered_asc"] = times == sorted(times)
		for item in items:
			if item["created_on"] <= since:
				errors.append(f"timeline_since included event before since: {item['id']}")

	# --- farmer scope ---
	farmer_delta = project_api.timeline_since({"farmer": FARMER, "since": since, "limit": 50})
	if farmer_delta.get("ok"):
		proof["farmer_since_count"] = len(farmer_delta["data"]["items"])

	# --- permission: Guest denied ---
	frappe.set_user("Guest")
	guest = project_api.timeline({"name": PROJECT})
	if guest.get("ok"):
		errors.append("Guest should not access timeline")
	proof["guest_denied"] = not guest.get("ok")

	frappe.set_user("Administrator")

	# --- immutability unchanged ---
	svc = get_timeline_service()
	if svc.query(farmer_project=PROJECT, limit=1)["items"]:
		row = frappe.get_doc("Timeline Event", svc.query(farmer_project=PROJECT, limit=1)["items"][0]["id"])
		try:
			row.payload_json = {"tamper": True}
			row.save(ignore_permissions=True)
			errors.append("timeline event should remain immutable")
		except frappe.ValidationError:
			proof["immutable_ok"] = True

	if errors:
		frappe.throw("Phase 9b API verification failed: " + "; ".join(errors))

	return {"ok": True, **proof}
''',
    )


def patch_api_contracts() -> None:
    if not CONTRACTS.exists():
        print("  skip API_CONTRACTS.md (path not mounted)")
        return
    text = CONTRACTS.read_text(encoding="utf-8")
    marker = "| Failure | `NOT_FOUND`, `PERM_DENIED` |\n\n---\n\n## 16. Task API contracts"
    insert = '''| Failure | `NOT_FOUND`, `PERM_DENIED` |

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

## 16. Task API contracts'''
    if "project.timeline_since" in text:
        print("  API_CONTRACTS.md already has timeline_since")
        return
    if marker not in text:
        print("  API_CONTRACTS.md marker not found")
        return
    CONTRACTS.write_text(text.replace(marker, insert), encoding="utf-8")
    print("  updated API_CONTRACTS.md")


def main() -> None:
    print("Phase 9b — API bootstrap")
    patch_timeline_service()
    write_api_layer()
    write_verify_script()
    patch_api_contracts()
    print("Done.")


if __name__ == "__main__":
    main()
