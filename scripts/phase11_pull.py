# Copyright (c) 2026, Murugan and contributors
"""Delta pull for timeline, task, farmer_project."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import get_datetime, now_datetime

from agriflow.api.v1.permissions import get_allowed_blocks
from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.sync_engine.api.serializers import project_sync_item, tombstone
from agriflow.task_engine.api.serializers import to_task_summary

PROJECT_FIELDS = [
	"name",
	"project_title",
	"farmer",
	"current_stage",
	"stage_sequence",
	"status",
	"doc_version",
	"block",
	"cluster",
	"village",
	"officer",
	"client_id",
	"is_deleted",
	"modified",
]

TASK_PULL_FIELDS = [
	"name",
	"subject",
	"farmer_project",
	"farmer",
	"task_type",
	"status",
	"priority",
	"due_date",
	"assigned_officer",
	"assigned_to",
	"block",
	"stage_key",
	"doc_version",
	"modified",
	"client_id",
	"sla_due_at",
	"sla_started_at",
	"sla_breached_at",
	"is_deleted",
]


def _max_watermark(items: list, field: str) -> str | None:
	best = None
	for it in items:
		val = it.get(field) if isinstance(it, dict) else getattr(it, field, None)
		if val is None:
			continue
		iso = val.isoformat() if hasattr(val, "isoformat") else str(val)
		if best is None or iso > best:
			best = iso
	return best


def _pull_timeline(payload: dict, *, allowed_blocks) -> dict[str, Any]:
	since = (payload.get("modified_since") or {}).get("timeline")
	limit = min(max(int((payload.get("limits") or {}).get("timeline", 50)), 1), 100)
	cursor = (payload.get("cursors") or {}).get("timeline")
	feed = get_timeline_service().query(
		since=since,
		since_exclusive=bool(since),
		limit=limit,
		cursor=cursor,
		order="asc",
	)
	items = feed["items"]
	if allowed_blocks is not None:
		allowed_projects = set(
			frappe.get_all(
				"Farmer Project",
				filters={"block": ("in", list(allowed_blocks)), "is_deleted": 0},
				pluck="name",
			)
		)
		items = [i for i in items if i.get("farmer_project") in allowed_projects]
	wm = _max_watermark(items, "created_on")
	return {
		"items": items,
		"deleted": [],
		"cursor": feed.get("next_cursor"),
		"has_more": feed.get("has_more", False),
		"_watermark": wm,
	}


def _pull_tasks(payload: dict, *, allowed_blocks, include_deleted: bool) -> dict[str, Any]:
	since = (payload.get("modified_since") or {}).get("task")
	limit = min(max(int((payload.get("limits") or {}).get("task", 25)), 1), 100)
	cursor = (payload.get("cursors") or {}).get("task")
	conditions = ["1=1"]
	values: dict[str, Any] = {"lim": limit + 1}

	if not include_deleted:
		conditions.append("is_deleted = 0")
	else:
		conditions.append("(is_deleted = 0 OR is_deleted = 1)")

	if allowed_blocks is not None:
		conditions.append("block IN %(blocks)s")
		values["blocks"] = tuple(allowed_blocks)

	blocks = payload.get("block")
	if blocks:
		if isinstance(blocks, str):
			blocks = [blocks]
		conditions.append("block IN %(filter_blocks)s")
		values["filter_blocks"] = tuple(blocks)

	if since:
		conditions.append("modified >= %(since)s")
		values["since"] = get_datetime(since)

	if cursor:
		cur = frappe.db.get_value("Project Task", cursor, ["name", "modified"], as_dict=True)
		if not cur:
			frappe.throw(frappe._("Invalid task cursor"), exc=frappe.ValidationError)
		conditions.append("(modified > %(c_mod)s OR (modified = %(c_mod)s AND name > %(c_name)s))")
		values.update({"c_mod": cur.modified, "c_name": cur.name})

	where = " AND ".join(conditions)
	sql = f"""
		SELECT {", ".join(TASK_PULL_FIELDS)}
		FROM `tabProject Task`
		WHERE {where}
		ORDER BY modified ASC, name ASC
		LIMIT %(lim)s
	"""
	rows = frappe.db.sql(sql, values, as_dict=True)
	active, deleted = [], []
	for r in rows:
		if r.is_deleted:
			deleted.append(tombstone(r.name, r.modified))
		else:
			active.append(to_task_summary(r))
	has_more = len(rows) > limit
	if has_more:
		rows = rows[:limit]
		active = active[:limit]
		next_cursor = rows[-1].name if rows else None
	else:
		next_cursor = None
	wm = _max_watermark(active + deleted, "modified")
	return {
		"items": active,
		"deleted": deleted,
		"cursor": next_cursor,
		"has_more": has_more,
		"_watermark": wm,
	}


def _pull_projects(payload: dict, *, allowed_blocks, include_deleted: bool) -> dict[str, Any]:
	since = (payload.get("modified_since") or {}).get("farmer_project")
	limit = min(max(int((payload.get("limits") or {}).get("farmer_project", 25)), 1), 100)
	cursor = (payload.get("cursors") or {}).get("farmer_project")
	conditions = ["1=1"]
	values: dict[str, Any] = {"lim": limit + 1}

	if not include_deleted:
		conditions.append("is_deleted = 0")
	else:
		conditions.append("(is_deleted = 0 OR is_deleted = 1)")

	if allowed_blocks is not None:
		conditions.append("block IN %(blocks)s")
		values["blocks"] = tuple(allowed_blocks)

	if since:
		conditions.append("modified >= %(since)s")
		values["since"] = get_datetime(since)

	if cursor:
		cur = frappe.db.get_value("Farmer Project", cursor, ["name", "modified"], as_dict=True)
		if not cur:
			frappe.throw(frappe._("Invalid farmer_project cursor"), exc=frappe.ValidationError)
		conditions.append("(modified > %(c_mod)s OR (modified = %(c_mod)s AND name > %(c_name)s))")
		values.update({"c_mod": cur.modified, "c_name": cur.name})

	where = " AND ".join(conditions)
	sql = f"""
		SELECT {", ".join(PROJECT_FIELDS)}
		FROM `tabFarmer Project`
		WHERE {where}
		ORDER BY modified ASC, name ASC
		LIMIT %(lim)s
	"""
	rows = frappe.db.sql(sql, values, as_dict=True)
	active, deleted = [], []
	for r in rows:
		if r.is_deleted:
			deleted.append(tombstone(r.name, r.modified))
		else:
			active.append(project_sync_item(r))
	has_more = len(rows) > limit
	if has_more:
		rows = rows[:limit]
		active = active[:limit]
		next_cursor = rows[-1].name if rows else None
	else:
		next_cursor = None
	wm = _max_watermark(active + deleted, "modified")
	return {
		"items": active,
		"deleted": deleted,
		"cursor": next_cursor,
		"has_more": has_more,
		"_watermark": wm,
	}


def pull(payload: dict) -> dict[str, Any]:
	entities = payload.get("entities") or ["timeline", "task", "farmer_project"]
	include_deleted = bool(payload.get("include_deleted"))
	allowed = get_allowed_blocks()
	data: dict[str, Any] = {}
	server_watermark: dict[str, Any] = {}

	for entity in entities:
		if entity == "timeline":
			chunk = _pull_timeline(payload, allowed_blocks=allowed)
		elif entity == "task":
			chunk = _pull_tasks(payload, allowed_blocks=allowed, include_deleted=include_deleted)
		elif entity == "farmer_project":
			chunk = _pull_projects(payload, allowed_blocks=allowed, include_deleted=include_deleted)
		else:
			frappe.throw(frappe._("Unsupported pull entity: {0}").format(entity))
		server_watermark[entity] = chunk.pop("_watermark", None)
		data[entity] = {
			"items": chunk["items"],
			"deleted": chunk["deleted"],
			"cursor": chunk["cursor"],
			"has_more": chunk["has_more"],
		}

	return {
		"entities": data,
		"server_watermark": server_watermark,
		"generated_at": now_datetime().isoformat(),
	}
