# Copyright (c) 2026, Murugan and contributors
"""Sync push handler for timeline manual notes."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.permissions import assert_project_access
from agriflow.project_lifecycle.services.timeline import get_timeline_service


def handle_note(op: dict) -> dict[str, Any]:
	payload = op.get("payload") or {}
	project = payload.get("farmer_project")
	text = (payload.get("text") or "").strip()
	if not project:
		frappe.throw(_("farmer_project is required"))
	if not text:
		frappe.throw(_("text is required"))
	assert_project_access(project)
	svc = get_timeline_service()
	event_id = svc.emit(
		"manual_note",
		project,
		payload={"text": text[:2000]},
		event_source="mobile",
		client_id=op.get("client_id") or payload.get("client_id"),
	)
	return {
		"status": "success",
		"entity": "timeline",
		"name": event_id,
		"event_type": "manual_note",
		"farmer_project": project,
	}
