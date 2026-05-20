# Copyright (c) 2026, Murugan and contributors
"""Sync push handlers for Project Task."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.errors import SYNC_CONFLICT_LWW, is_stale_doc_version
from agriflow.api.v1.permissions import assert_task_access, assert_task_create
from agriflow.task_engine.api.serializers import normalize_priority_in, to_task_detail
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

VALID_TYPES = frozenset(
	{
		"field_visit",
		"document_collection",
		"verification",
		"approval",
		"installation",
		"follow_up",
	}
)


def _conflict_lww(task_name: str, client_version, exc: Exception) -> dict[str, Any]:
	server = frappe.db.get_value(
		"Project Task",
		task_name,
		["name", "doc_version", "modified", "status", "subject", "description"],
		as_dict=True,
	)
	return {
		"status": "conflict",
		"conflict": {
			"type": "lww_version_mismatch",
			"resolution": "server_payload",
			"server": {
				"name": server.name,
				"doc_version": server.doc_version,
				"modified": str(server.modified),
				"fields": to_task_detail(server),
			},
			"client": {"doc_version": client_version},
			"message": str(exc),
		},
	}


def handle_create(op: dict) -> dict[str, Any]:
	payload = op.get("payload") or {}
	for f in ("subject", "farmer_project", "task_type", "due_date"):
		if not payload.get(f):
			frappe.throw(_("Missing required field: {0}").format(f))
	if payload["task_type"] not in VALID_TYPES:
		frappe.throw(_("Invalid task_type"))
	assert_task_create(payload["farmer_project"])
	svc = TaskLifecycleService()
	doc = svc.create_task(
		subject=payload["subject"],
		farmer_project=payload["farmer_project"],
		task_type=payload["task_type"],
		due_date=payload["due_date"],
		priority=normalize_priority_in(payload.get("priority")),
		description=payload.get("description"),
		client_id=op.get("client_id") or payload.get("client_id"),
		assigned_officer=payload.get("assigned_officer"),
		assigned_to=payload.get("assigned_to"),
		auto_assign=bool(payload.get("assigned_officer")),
	)
	return {
		"status": "success",
		"entity": "task",
		"client_id": doc.client_id,
		"name": doc.name,
		"doc_version": doc.doc_version,
		"task": to_task_detail(doc),
	}


def handle_update(op: dict) -> dict[str, Any]:
	payload = op.get("payload") or {}
	name = payload.get("name")
	if not name:
		frappe.throw(_("Task name required for update"))
	if payload.get("doc_version") is None:
		frappe.throw(_("doc_version required for update"))
	assert_task_access(name)
	doc_version = int(payload["doc_version"])
	lifecycle = TaskLifecycleService()
	assign_svc = TaskAssignmentService()
	try:
		if payload.get("assigned_officer"):
			task = assign_svc.assign(
				name,
				payload["assigned_officer"],
				assigned_to=payload.get("assigned_to"),
				reason="reassignment",
			)
			doc_version = task.doc_version
		if payload.get("status"):
			task = lifecycle.transition_status(
				name,
				payload["status"],
				doc_version=doc_version,
				blocked_reason=payload.get("blocked_reason"),
				visit_outcome=payload.get("visit_outcome"),
			)
		elif payload.get("description") is not None:
			task = lifecycle.update_description(
				name, doc_version=doc_version, description=payload["description"]
			)
		else:
			task = frappe.get_doc("Project Task", name)
		task.reload()
	except frappe.ValidationError as exc:
		if is_stale_doc_version(exc):
			return _conflict_lww(name, doc_version, exc)
		raise
	return {
		"status": "success",
		"entity": "task",
		"name": task.name,
		"doc_version": task.doc_version,
		"task": to_task_detail(task),
	}


def handle_complete(op: dict) -> dict[str, Any]:
	payload = op.get("payload") or {}
	name = payload.get("name")
	if not name:
		frappe.throw(_("Task name required for complete"))
	if payload.get("doc_version") is None:
		frappe.throw(_("doc_version required for complete"))
	assert_task_access(name)
	doc_version = int(payload["doc_version"])
	try:
		task = TaskLifecycleService().complete(
			name,
			doc_version=doc_version,
			visit_outcome=payload.get("visit_outcome"),
			completed_on=payload.get("completed_on"),
		)
	except frappe.ValidationError as exc:
		if is_stale_doc_version(exc):
			return _conflict_lww(name, doc_version, exc)
		raise
	return {
		"status": "success",
		"entity": "task",
		"name": task.name,
		"doc_version": task.doc_version,
		"task": to_task_detail(task),
	}
