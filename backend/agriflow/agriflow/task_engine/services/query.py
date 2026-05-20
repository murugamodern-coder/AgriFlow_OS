# Copyright (c) 2026, Murugan and contributors
"""Paginated task list with keyset cursor (due_date, priority, modified, name)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import get_datetime, getdate, now_datetime

from agriflow.api.v1.permissions import get_allowed_blocks
from agriflow.task_engine.api.serializers import to_task_summary

VALID_STATUSES = frozenset(
	{"open", "assigned", "in_progress", "blocked", "completed", "cancelled"}
)
LIST_FIELDS = [
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
]
PF = "FIELD(priority, 'low', 'normal', 'medium', 'high', 'urgent')"


def _normalize_due_before(payload: dict) -> str | None:
	return payload.get("due_before") or payload.get("due_date_lte")


def list_tasks(payload: dict) -> dict[str, Any]:
	limit = min(max(int(payload.get("limit") or 25), 1), 100)
	conditions = ["is_deleted = 0"]
	values: dict[str, Any] = {}

	allowed = get_allowed_blocks()
	if allowed is not None:
		conditions.append("block IN %(blocks)s")
		values["blocks"] = tuple(allowed)

	if payload.get("farmer_project"):
		conditions.append("farmer_project = %(farmer_project)s")
		values["farmer_project"] = payload["farmer_project"]

	blocks = payload.get("block")
	if blocks:
		if isinstance(blocks, str):
			blocks = [blocks]
		conditions.append("block IN %(filter_blocks)s")
		values["filter_blocks"] = tuple(blocks)

	statuses = payload.get("status")
	if statuses:
		if isinstance(statuses, str):
			statuses = [statuses]
		invalid = [s for s in statuses if s not in VALID_STATUSES]
		if invalid:
			frappe.throw(frappe._("Invalid status: {0}").format(", ".join(invalid)))
		conditions.append("status IN %(statuses)s")
		values["statuses"] = tuple(statuses)

	priorities = payload.get("priority")
	if priorities:
		if isinstance(priorities, str):
			priorities = [priorities]
		norm = tuple("normal" if p == "medium" else p for p in priorities)
		conditions.append("priority IN %(priorities)s")
		values["priorities"] = norm

	assigned_to = payload.get("assigned_to")
	if assigned_to == "me":
		conditions.append("assigned_to = %(assigned_to)s")
		values["assigned_to"] = frappe.session.user
	elif assigned_to:
		conditions.append("assigned_to = %(assigned_to)s")
		values["assigned_to"] = assigned_to

	if payload.get("assigned_officer"):
		conditions.append("assigned_officer = %(assigned_officer)s")
		values["assigned_officer"] = payload["assigned_officer"]

	due_before = _normalize_due_before(payload)
	if due_before:
		conditions.append("due_date <= %(due_before)s")
		values["due_before"] = getdate(due_before)

	if payload.get("modified_since"):
		conditions.append("modified >= %(modified_since)s")
		values["modified_since"] = get_datetime(payload["modified_since"])

	cursor = payload.get("cursor")
	if cursor:
		cur = frappe.db.get_value(
			"Project Task",
			cursor,
			["name", "due_date", "priority", "modified"],
			as_dict=True,
		)
		if not cur:
			frappe.throw(frappe._("Invalid cursor"), exc=frappe.ValidationError)
		conditions.append(
			f"""(
			due_date > %(c_due)s
			OR (due_date = %(c_due)s AND {PF} < FIELD(%(c_pri)s, 'low', 'normal', 'medium', 'high', 'urgent'))
			OR (due_date = %(c_due)s AND {PF} = FIELD(%(c_pri)s, 'low', 'normal', 'medium', 'high', 'urgent') AND modified < %(c_mod)s)
			OR (due_date = %(c_due)s AND {PF} = FIELD(%(c_pri)s, 'low', 'normal', 'medium', 'high', 'urgent') AND modified = %(c_mod)s AND name > %(c_name)s)
		)"""
		)
		values.update(
			{
				"c_due": cur.due_date,
				"c_pri": cur.priority or "normal",
				"c_mod": cur.modified,
				"c_name": cur.name,
			}
		)

	where = " AND ".join(conditions)
	sql = f"""
		SELECT {", ".join(LIST_FIELDS)}
		FROM `tabProject Task`
		WHERE {where}
		ORDER BY due_date ASC, {PF} DESC, modified DESC, name ASC
		LIMIT %(lim)s
	"""
	values["lim"] = limit + 1
	rows = frappe.db.sql(sql, values, as_dict=True)
	has_more = len(rows) > limit
	if has_more:
		rows = rows[:limit]
	next_cursor = rows[-1].name if rows and has_more else None
	return {
		"items": [to_task_summary(r) for r in rows],
		"pagination": {"next_cursor": next_cursor, "has_more": has_more, "limit": limit},
		"generated_at": now_datetime().isoformat(),
	}
