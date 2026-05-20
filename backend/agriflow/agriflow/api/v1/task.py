# Copyright (c) 2026, Murugan and contributors
"""Task API — API_CONTRACTS §16 (Phase 10b)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.errors import (
	SYNC_CONFLICT_LWW,
	VAL_INVALID,
	VAL_INVALID_CURSOR,
	VAL_REQUIRED_FIELD,
	conflict_from_stale,
	is_stale_doc_version,
)
from agriflow.api.v1.permissions import assert_task_access, assert_task_create, ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.task_engine.api.serializers import (
	allowed_transitions,
	assignment_history,
	normalize_priority_in,
	to_task_detail,
	timeline_preview,
)
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService
from agriflow.task_engine.services.query import list_tasks

VALID_TASK_TYPES = frozenset(
	{
		"field_visit",
		"document_collection",
		"verification",
		"approval",
		"installation",
		"follow_up",
	}
)


def _stale_response(exc: Exception, task_name: str, doc_version):
	if is_stale_doc_version(exc):
		return conflict_from_stale(task_name, doc_version, str(exc))
	return None


@frappe.whitelist()
def list(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		if payload.get("cursor") and not frappe.db.exists("Project Task", payload["cursor"]):
			return fail(VAL_INVALID_CURSOR, _("Invalid cursor"), http_status=400)
		return success(list_tasks(payload))
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		if "cursor" in str(exc).lower():
			return fail(VAL_INVALID_CURSOR, str(exc), http_status=400)
		return fail(VAL_INVALID, str(exc), http_status=400)


@frappe.whitelist()
def get(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		row = assert_task_access(name)
		return success(
			{
				"task": to_task_detail(row),
				"assignment_history": assignment_history(name),
				"timeline_preview": timeline_preview(name, row.farmer_project),
				"sla": {
					**to_task_detail(row)["sla"],
					"is_overdue": to_task_detail(row)["is_overdue"],
				},
				"allowed_transitions": allowed_transitions(row.status),
			}
		)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def create(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		for field in ("client_id", "subject", "farmer_project", "task_type", "due_date"):
			if not payload.get(field):
				return fail(VAL_REQUIRED_FIELD, _("{0} is required").format(field), http_status=400)
		if payload["task_type"] not in VALID_TASK_TYPES:
			return fail(VAL_INVALID, _("Invalid task_type"), http_status=400)
		assert_task_create(payload["farmer_project"])
		svc = TaskLifecycleService()
		doc = svc.create_task(
			subject=payload["subject"],
			farmer_project=payload["farmer_project"],
			task_type=payload["task_type"],
			due_date=payload["due_date"],
			priority=normalize_priority_in(payload.get("priority")),
			description=payload.get("description"),
			client_id=payload["client_id"],
			assigned_officer=payload.get("assigned_officer"),
			assigned_to=payload.get("assigned_to"),
			auto_assign=bool(payload.get("assigned_officer")),
		)
		if payload.get("assigned_officer") and not payload.get("assigned_to"):
			pass
		elif payload.get("assigned_to") and payload.get("assigned_officer"):
			TaskAssignmentService().assign(
				doc.name,
				payload["assigned_officer"],
				assigned_to=payload["assigned_to"],
				reason="initial",
			)
			doc.reload()
		return success({"task": to_task_detail(doc)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail(VAL_INVALID, str(exc), http_status=400)


@frappe.whitelist()
def update(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		if payload.get("doc_version") is None:
			return fail(VAL_REQUIRED_FIELD, _("doc_version is required"), http_status=400)
		assert_task_access(name)
		doc_version = int(payload["doc_version"])
		lifecycle = TaskLifecycleService()
		assign_svc = TaskAssignmentService()
		task = frappe.get_doc("Project Task", name)

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
		except frappe.ValidationError as exc:
			stale = _stale_response(exc, name, doc_version)
			if stale:
				return stale
			return fail(VAL_INVALID, str(exc), http_status=400)

		task.reload()
		return success({"task": to_task_detail(task)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def complete(data=None):
	try:
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail(VAL_INVALID, _("name is required"), http_status=400)
		if payload.get("doc_version") is None:
			return fail(VAL_REQUIRED_FIELD, _("doc_version is required"), http_status=400)
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
			stale = _stale_response(exc, name, doc_version)
			if stale:
				return stale
			return fail(VAL_INVALID, str(exc), http_status=400)
		return success({"task": to_task_detail(task)})
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
