# Copyright (c) 2026, Murugan and contributors
"""Append-only task assignment history."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.sla import apply_sla_fields
from agriflow.task_engine.utils.transitions import can_transition

ASSIGNMENT_FLAG = "agriflow_task_assignment_write"
TASK_WRITE_FLAG = "agriflow_task_write"


class TaskAssignmentService:
	def assign(
		self,
		task_name: str,
		officer: str,
		*,
		assigned_to: str | None = None,
		reason: str = "initial",
		notes: str | None = None,
	) -> frappe.model.document.Document:
		task = frappe.get_doc("Project Task", task_name)
		if task.is_deleted:
			frappe.throw(_("Task is deleted"))
		if not frappe.db.exists("Officer", {"name": officer, "is_active": 1}):
			frappe.throw(_("Officer not found or inactive"))

		assigned_to = assigned_to or frappe.session.user
		self._close_open_history(task_name)

		frappe.get_doc(
			{
				"doctype": "Project Task Assignment History",
				"project_task": task_name,
				"farmer_project": task.farmer_project,
				"officer": officer,
				"assigned_on": now_datetime(),
				"assigned_by": frappe.session.user,
				"assignment_reason": reason,
				"notes": notes or "",
			}
		).insert(ignore_permissions=True)

		old_status = task.status
		if task.status == "open":
			task.status = "assigned"
		task.assigned_officer = officer
		task.assigned_to = assigned_to
		apply_sla_fields(task, old_status)
		self._save_task(task)

		get_timeline_service().emit_task_assigned(
			task,
			officer=officer,
			assigned_to=assigned_to,
			reason=reason,
		)
		return task

	def unassign(self, task_name: str, *, notes: str | None = None) -> frappe.model.document.Document:
		task = frappe.get_doc("Project Task", task_name)
		if task.status not in ("assigned",):
			frappe.throw(_("Only assigned tasks can be unassigned"))
		self._close_open_history(task_name, notes=notes)
		old_status = task.status
		if not can_transition(old_status, "open"):
			frappe.throw(_("Cannot unassign from status {0}").format(old_status))
		task.status = "open"
		task.assigned_officer = None
		task.assigned_to = None
		apply_sla_fields(task, old_status)
		self._save_task(task)
		get_timeline_service().emit_task_status_changed(
			task, from_status=old_status, to_status="open", note="unassigned"
		)
		return task

	def _close_open_history(self, task_name: str, notes: str | None = None) -> None:
		open_rows = frappe.get_all(
			"Project Task Assignment History",
			filters={"project_task": task_name, "unassigned_on": ("is", "not set")},
			fields=["name"],
		)
		for row in open_rows:
			h = frappe.get_doc("Project Task Assignment History", row.name)
			h.unassigned_on = now_datetime()
			if notes:
				h.notes = (h.notes or "") + (" " + notes if h.notes else notes)
			frappe.flags[ASSIGNMENT_FLAG] = True
			try:
				h.save(ignore_permissions=True)
			finally:
				frappe.flags[ASSIGNMENT_FLAG] = False

	def _save_task(self, task) -> None:
		frappe.flags[TASK_WRITE_FLAG] = True
		try:
			task.save(ignore_permissions=True)
		finally:
			frappe.flags[TASK_WRITE_FLAG] = False
