# Copyright (c) 2026, Murugan and contributors
"""Project Task lifecycle — sole writer for status transitions."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.sla import apply_sla_fields
from agriflow.task_engine.utils.transitions import TERMINAL, can_transition

TASK_WRITE_FLAG = "agriflow_task_write"


class TaskLifecycleService:
	def create_task(
		self,
		*,
		subject: str,
		farmer_project: str,
		task_type: str,
		due_date: str,
		priority: str = "normal",
		stage_key: str | None = None,
		source_template: str | None = None,
		assigned_officer: str | None = None,
		assigned_to: str | None = None,
		description: str | None = None,
		client_id: str | None = None,
		auto_assign: bool = True,
	) -> frappe.model.document.Document:
		project = frappe.get_doc("Farmer Project", farmer_project)
		if project.status == "cancelled":
			frappe.throw(_("Cannot create tasks on cancelled project"))

		if client_id:
			existing = frappe.db.exists(
				"Project Task",
				{"client_id": client_id, "is_deleted": 0},
			)
			if existing:
				return frappe.get_doc("Project Task", existing)

		doc = frappe.get_doc(
			{
				"doctype": "Project Task",
				"subject": subject,
				"farmer_project": farmer_project,
				"farmer": project.farmer,
				"task_type": task_type,
				"status": "open",
				"priority": priority,
				"due_date": due_date,
				"stage_key": stage_key or project.current_stage,
				"source_template": source_template,
				"description": description or "",
				"client_id": client_id,
				"doc_version": 1,
				"sync_status": "synced",
			}
		)
		apply_sla_fields(doc)
		self._insert(doc)
		get_timeline_service().emit_task_created(doc)

		if assigned_officer and auto_assign:
			TaskAssignmentService().assign(
				doc.name,
				assigned_officer,
				assigned_to=assigned_to,
				reason="initial",
			)
			doc.reload()
		return doc

	def transition_status(
		self,
		task_name: str,
		new_status: str,
		*,
		doc_version: int | None = None,
		blocked_reason: str | None = None,
		visit_outcome: str | None = None,
		completed_on: str | None = None,
	) -> frappe.model.document.Document:
		task = frappe.get_doc("Project Task", task_name)
		if doc_version is not None and int(task.doc_version or 0) != int(doc_version):
			frappe.throw(
				_("Stale doc_version. Server has {0}, client sent {1}").format(
					task.doc_version, doc_version
				)
			)
		self._ensure_project_active(task.farmer_project)
		old = task.status
		if old in TERMINAL:
			frappe.throw(_("Task is terminal ({0})").format(old))
		if not can_transition(old, new_status):
			frappe.throw(_("Invalid transition {0} -> {1}").format(old, new_status))

		if new_status == "in_progress" and not task.started_on:
			task.started_on = now_datetime()
		if new_status == "blocked":
			task.blocked_reason = blocked_reason or task.blocked_reason
		if new_status == "completed":
			task.completed_on = completed_on or now_datetime()
			task.visit_outcome = visit_outcome or task.visit_outcome
			if not task.completed_on:
				frappe.throw(_("completed_on is required"))

		task.status = new_status
		apply_sla_fields(task, old)
		self._save(task)

		if new_status == "completed":
			get_timeline_service().emit_task_completed(task)
		else:
			get_timeline_service().emit_task_status_changed(task, from_status=old, to_status=new_status)
		return task

	def complete(
		self,
		task_name: str,
		*,
		doc_version: int | None = None,
		visit_outcome: str | None = None,
		completed_on: str | None = None,
	) -> frappe.model.document.Document:
		"""Complete from in_progress, or auto-step assigned → in_progress → completed."""
		task = frappe.get_doc("Project Task", task_name)
		if doc_version is not None and int(task.doc_version or 0) != int(doc_version):
			frappe.throw(
				_("Stale doc_version. Server has {0}, client sent {1}").format(
					task.doc_version, doc_version
				)
			)
		if task.status == "assigned":
			task = self.transition_status(
				task_name,
				"in_progress",
				doc_version=task.doc_version,
			)
			return self.transition_status(
				task_name,
				"completed",
				doc_version=task.doc_version,
				visit_outcome=visit_outcome,
				completed_on=completed_on,
			)
		if task.status not in ("in_progress",):
			frappe.throw(_("Cannot complete task in status {0}").format(task.status))
		return self.transition_status(
			task_name,
			"completed",
			doc_version=doc_version if doc_version is not None else task.doc_version,
			visit_outcome=visit_outcome,
			completed_on=completed_on,
		)


	def update_description(
		self,
		task_name: str,
		*,
		doc_version: int,
		description: str,
	) -> frappe.model.document.Document:
		task = frappe.get_doc("Project Task", task_name)
		if int(task.doc_version or 0) != int(doc_version):
			frappe.throw(
				_("Stale doc_version. Server has {0}, client sent {1}").format(
					task.doc_version, doc_version
				)
			)
		self._ensure_project_active(task.farmer_project)
		task.description = description
		self._save(task)
		return task

	def validate_direct_save(self, doc) -> None:
		frappe.throw(_("Project Task changes must use TaskLifecycleService or TaskAssignmentService"))

	def _ensure_project_active(self, farmer_project: str) -> None:
		status = frappe.db.get_value("Farmer Project", farmer_project, "status")
		if status == "cancelled":
			frappe.throw(_("Cannot update tasks on cancelled project"))

	def _insert(self, doc) -> None:
		frappe.flags[TASK_WRITE_FLAG] = True
		try:
			doc.insert(ignore_permissions=True)
		finally:
			frappe.flags[TASK_WRITE_FLAG] = False

	def _save(self, doc) -> None:
		frappe.flags[TASK_WRITE_FLAG] = True
		try:
			doc.save(ignore_permissions=True)
		finally:
			frappe.flags[TASK_WRITE_FLAG] = False
