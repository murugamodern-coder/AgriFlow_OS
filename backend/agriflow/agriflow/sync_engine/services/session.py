# Copyright (c) 2026, Murugan and contributors
"""Sync Session lifecycle."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import now_datetime

SESSION_FLAG = "agriflow_sync_session_write"


def open_session(
	*,
	device_id: str | None,
	session_type: str,
	watermarks_in: dict | None = None,
) -> frappe.model.document.Document:
	doc = frappe.get_doc(
		{
			"doctype": "Sync Session",
			"device_id": device_id or "",
			"user": frappe.session.user,
			"session_type": session_type,
			"started_on": now_datetime(),
			"watermarks_in": watermarks_in or {},
		}
	)
	doc.set_new_name()
	doc.sync_token = doc.name
	frappe.flags[SESSION_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[SESSION_FLAG] = False
	return doc


def complete_session(
	session_name: str,
	*,
	watermarks_out: dict | None = None,
	summary: dict | None = None,
) -> str:
	doc = frappe.get_doc("Sync Session", session_name)
	doc.watermarks_out = watermarks_out or {}
	doc.summary = summary or {}
	doc.completed_on = now_datetime()
	frappe.flags[SESSION_FLAG] = True
	try:
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags[SESSION_FLAG] = False
	return doc.sync_token
