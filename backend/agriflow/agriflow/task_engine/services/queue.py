# Copyright (c) 2026, Murugan and contributors
"""Officer work queue queries."""

from __future__ import annotations

from typing import Any

import frappe

from agriflow.task_engine.utils.transitions import OPEN_QUEUE


def open_tasks_for_project(farmer_project: str, *, limit: int = 50) -> list[dict[str, Any]]:
	rows = frappe.get_all(
		"Project Task",
		filters={
			"farmer_project": farmer_project,
			"status": ("in", list(OPEN_QUEUE)),
			"is_deleted": 0,
		},
		fields=[
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
			"sla_breached_at",
		],
		order_by="due_date asc, priority desc, modified desc",
		limit=limit,
	)
	for row in rows:
		row["is_overdue"] = bool(
			row.due_date
			and frappe.utils.getdate(row.due_date) < frappe.utils.getdate(frappe.utils.today())
			and row.status in OPEN_QUEUE
		)
		if hasattr(row.get("modified"), "isoformat"):
			row["modified"] = row.modified.isoformat()
		if hasattr(row.get("sla_due_at"), "isoformat") and row.sla_due_at:
			row["sla_due_at"] = row.sla_due_at.isoformat()
		if hasattr(row.get("sla_breached_at"), "isoformat") and row.sla_breached_at:
			row["sla_breached_at"] = row.sla_breached_at.isoformat()
	return rows
