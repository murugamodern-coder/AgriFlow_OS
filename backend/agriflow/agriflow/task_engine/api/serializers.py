# Copyright (c) 2026, Murugan and contributors
"""Mobile-friendly task API serializers."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import getdate, today

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.utils.transitions import ALLOWED_TRANSITIONS, OPEN_QUEUE

PRIORITY_RANK = {"urgent": 4, "high": 3, "normal": 2, "medium": 2, "low": 1}


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _sla_block(row) -> dict[str, Any]:
	return {
		"sla_due_at": _iso(row.get("sla_due_at") if isinstance(row, dict) else getattr(row, "sla_due_at", None)),
		"sla_started_at": _iso(
			row.get("sla_started_at") if isinstance(row, dict) else getattr(row, "sla_started_at", None)
		),
		"sla_breached_at": _iso(
			row.get("sla_breached_at") if isinstance(row, dict) else getattr(row, "sla_breached_at", None)
		),
	}


def is_overdue(row) -> bool:
	status = row.get("status") if isinstance(row, dict) else row.status
	if status not in OPEN_QUEUE:
		return False
	due = row.get("due_date") if isinstance(row, dict) else row.due_date
	if not due:
		return False
	return getdate(due) < getdate(today())


def to_task_summary(row) -> dict[str, Any]:
	data = row if isinstance(row, dict) else row.as_dict()
	return {
		"name": data.name,
		"subject": data.subject,
		"farmer_project": data.farmer_project,
		"farmer": data.farmer,
		"task_type": data.task_type,
		"status": data.status,
		"priority": _normalize_priority_out(data.priority),
		"due_date": str(data.due_date) if data.due_date else None,
		"assigned_officer": data.assigned_officer,
		"assigned_to": data.assigned_to,
		"block": data.block,
		"stage_key": data.stage_key,
		"doc_version": data.doc_version,
		"modified": _iso(data.modified),
		"client_id": data.client_id,
		"is_overdue": is_overdue(data),
		"sla": _sla_block(data),
	}


def to_task_detail(row) -> dict[str, Any]:
	summary = to_task_summary(row)
	data = row if isinstance(row, dict) else row.as_dict()
	summary.update(
		{
			"description": data.get("description") or "",
			"visit_outcome": data.get("visit_outcome"),
			"blocked_reason": data.get("blocked_reason"),
			"started_on": _iso(data.get("started_on")),
			"completed_on": _iso(data.get("completed_on")),
			"cluster": data.get("cluster"),
			"district": data.get("district"),
			"source_template": data.get("source_template"),
			"sync_status": data.get("sync_status"),
			"is_deleted": data.get("is_deleted") or 0,
		}
	)
	return summary


def assignment_history(task_name: str) -> list[dict[str, Any]]:
	rows = frappe.get_all(
		"Project Task Assignment History",
		filters={"project_task": task_name},
		fields=[
			"name",
			"officer",
			"assigned_on",
			"unassigned_on",
			"assigned_by",
			"assignment_reason",
			"notes",
		],
		order_by="assigned_on asc",
	)
	for row in rows:
		row["assigned_on"] = _iso(row.assigned_on)
		row["unassigned_on"] = _iso(row.unassigned_on)
	return rows


def timeline_preview(task_name: str, farmer_project: str, *, limit: int = 10) -> dict[str, Any]:
	types = ["task_created", "task_assigned", "task_status_changed", "task_completed"]
	feed = get_timeline_service().query(
		farmer_project=farmer_project,
		event_types=types,
		limit=50,
		order="desc",
	)
	items = [e for e in feed["items"] if e.get("reference", {}).get("name") == task_name]
	return {"items": items[:limit], "reference_task": task_name}


def allowed_transitions(status: str) -> list[str]:
	return sorted(ALLOWED_TRANSITIONS.get(status or "open", frozenset()))


def normalize_priority_in(value: str | None) -> str:
	if not value:
		return "normal"
	v = value.strip().lower()
	if v == "medium":
		return "normal"
	return v


def _normalize_priority_out(value: str | None) -> str:
	return value or "normal"
