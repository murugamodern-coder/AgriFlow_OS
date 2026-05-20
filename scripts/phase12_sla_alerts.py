# Copyright (c) 2026, Murugan and contributors
"""SLA overdue notification foundation (scheduler, no push)."""

from __future__ import annotations

import frappe
from frappe.utils import getdate, now_datetime, today

from agriflow.notification_engine.services.delivery import deliver_one, make_delivery_key
from agriflow.notification_engine.services.i18n_keys import title_key
from agriflow.notification_engine.services.recipients import resolve_task_recipients


def scan_task_overdue_notifications() -> dict:
	"""Daily job: notify assignees for overdue open tasks (one key per task/day)."""
	today_str = str(today())
	tasks = frappe.get_all(
		"Project Task",
		filters={
			"is_deleted": 0,
			"status": ("in", ["open", "assigned", "in_progress", "blocked"]),
			"due_date": ("<", today_str),
		},
		fields=[
			"name",
			"subject",
			"farmer_project",
			"farmer",
			"block",
			"district",
			"due_date",
			"assigned_to",
		],
		limit=500,
	)
	delivered = 0
	skipped = 0
	for task in tasks:
		recipients = resolve_task_recipients(task.name)
		for user in recipients:
			source_key = f"task_overdue|{task.name}|{today_str}|{user}"
			dk = make_delivery_key(
				timeline_event=None,
				notification_type="task_overdue",
				recipient=user,
				source_name=source_key,
			)
			if frappe.db.exists("Notification Delivery Log", {"delivery_key": dk}):
				skipped += 1
				continue
			project = frappe.db.get_value(
				"Farmer Project",
				task.farmer_project,
				"project_title",
				as_dict=True,
			) or {}
			payload = {
				"task": task.name,
				"subject": task.subject,
				"due_date": str(task.due_date),
				"farmer_project": task.farmer_project,
				"deep_link": f"/projects/{task.farmer_project}/tasks/{task.name}",
			}
			preview = f"Overdue: {task.subject} — {project.get('project_title') or task.farmer_project}"[
				:140
			]
			out = deliver_one(
				recipient=user,
				notification_type="task_overdue",
				title_i18n_key=title_key("task_overdue"),
				body_preview=preview,
				payload_json=payload,
				farmer_project=task.farmer_project,
				farmer=task.farmer,
				block=task.block,
				district=task.district,
				timeline_event=None,
				source_doctype="Project Task",
				source_name=source_key,
				priority="high",
			)
			if out.get("status") == "delivered":
				delivered += 1
			else:
				skipped += 1
	return {
		"scanned": len(tasks),
		"delivered": delivered,
		"skipped": skipped,
		"ran_at": now_datetime().isoformat(),
	}
