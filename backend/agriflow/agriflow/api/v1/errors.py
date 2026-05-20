# Copyright (c) 2026, Murugan and contributors
"""API error codes — API_CONTRACTS §6."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.api.v1.response import fail

NOT_FOUND = "NOT_FOUND"
PERM_DENIED = "PERM_DENIED"
VAL_INVALID = "VAL_INVALID"
VAL_INVALID_CURSOR = "VAL_INVALID_CURSOR"
VAL_REQUIRED_FIELD = "VAL_REQUIRED_FIELD"
SYNC_CONFLICT_LWW = "SYNC_CONFLICT_LWW"


def throw_not_found(message: str = "Resource not found"):
	frappe.throw(message, exc=frappe.DoesNotExistError)


def throw_perm(message: str = "Permission denied"):
	frappe.throw(message, exc=frappe.PermissionError)


def throw_validation(message: str):
	frappe.throw(message, exc=frappe.ValidationError)


def is_stale_doc_version(exc: Exception) -> bool:
	return "Stale doc_version" in str(exc)


def conflict_from_stale(task_name: str, client_version: int | None, message: str | None = None):
	server = frappe.db.get_value("Project Task", task_name, "doc_version")
	return fail(
		SYNC_CONFLICT_LWW,
		message or _("Document was modified by another session"),
		http_status=409,
		details={
			"server_doc_version": server,
			"client_doc_version": client_version,
		},
	)
