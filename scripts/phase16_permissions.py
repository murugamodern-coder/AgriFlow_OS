# Copyright (c) 2026, Murugan and contributors
"""Session + JWT bearer auth; block scope checks (Phase 16)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.api.v1.auth_jwt import resolve_bearer

BYPASS_ROLES = frozenset({"Administrator", "System Manager"})


def _authorization_header() -> str | None:
	req = getattr(frappe.local, "request", None)
	if not req:
		return None
	return req.headers.get("Authorization") or req.headers.get("authorization")


def ensure_authenticated() -> None:
	if frappe.session.user not in ("Guest", ""):
		return
	auth = _authorization_header()
	if auth:
		resolve_bearer(auth)
		if frappe.session.user not in ("Guest", ""):
			return
	frappe.throw(_("Authentication required"), exc=frappe.AuthenticationError)


def get_allowed_blocks() -> set[str] | None:
	if set(frappe.get_roles()) & BYPASS_ROLES:
		return None
	perms = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "Block"},
		pluck="for_value",
	)
	return set(perms) if perms else set()


def assert_block_scope(block: str | None) -> None:
	if not block:
		return
	allowed = get_allowed_blocks()
	if allowed is not None and block not in allowed:
		frappe.throw(_("Not permitted for block {0}").format(block), exc=frappe.PermissionError)


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
	assert_block_scope(project.block)
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


TASK_FIELDS = [
	"name",
	"subject",
	"farmer_project",
	"farmer",
	"task_type",
	"status",
	"priority",
	"due_date",
	"started_on",
	"completed_on",
	"assigned_officer",
	"assigned_to",
	"block",
	"cluster",
	"district",
	"stage_key",
	"source_template",
	"description",
	"visit_outcome",
	"blocked_reason",
	"sla_due_at",
	"sla_started_at",
	"sla_breached_at",
	"client_id",
	"doc_version",
	"sync_status",
	"is_deleted",
	"modified",
]


def assert_task_access(task_name: str) -> dict:
	ensure_authenticated()
	if not frappe.db.exists("Project Task", {"name": task_name, "is_deleted": 0}):
		frappe.throw(_("Project Task not found"), exc=frappe.DoesNotExistError)
	task = frappe.db.get_value("Project Task", task_name, TASK_FIELDS, as_dict=True)
	assert_block_scope(task.block)
	return task


def assert_task_create(farmer_project: str) -> dict:
	project = assert_project_access(farmer_project)
	if project.status == "cancelled":
		frappe.throw(_("Cannot create tasks on cancelled project"))
	return project
