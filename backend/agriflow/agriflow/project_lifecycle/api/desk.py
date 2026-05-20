# Copyright (c) 2026, Murugan and contributors
"""Desk-only helpers for manual lifecycle testing (not public REST v1)."""

from __future__ import annotations

import frappe
from frappe import _

from agriflow.project_lifecycle.services.lifecycle import LIFECYCLE_FLAG, get_lifecycle_service
from agriflow.project_lifecycle.services.timeline import get_timeline_service


@frappe.whitelist()
def transition_for_desk(project: str, target_stage: str, notes: str | None = None, doc_version: int | None = None):
	frappe.only_for(("System Manager", "Administrator"))
	if not project or not target_stage:
		frappe.throw(_("project and target_stage are required"))
	version = int(doc_version) if doc_version not in (None, "") else None
	if version is None:
		version = frappe.db.get_value("Farmer Project", project, "doc_version")
	return get_lifecycle_service().transition(
		project,
		target_stage,
		doc_version=version,
		notes=notes,
	)


@frappe.whitelist()
def create_project_for_desk(
	farmer: str,
	project_type: str = "subsidy",
	status: str = "active",
	remarks: str | None = None,
):
	frappe.only_for(("System Manager", "Administrator"))
	svc = get_lifecycle_service()
	doc = svc.create_project(farmer, project_type=project_type, remarks=remarks, created_via="desk")
	if status and status != "active":
		frappe.flags[LIFECYCLE_FLAG] = True
		try:
			doc.status = status
			doc.save(ignore_permissions=True)
		finally:
			frappe.flags[LIFECYCLE_FLAG] = False
	return {"name": doc.name, "current_stage": doc.current_stage, "stage_sequence": doc.stage_sequence}


@frappe.whitelist()
def add_timeline_note_for_desk(project: str, text: str, client_id: str | None = None):
	"""Append manual_note timeline event — desk testing only."""
	frappe.only_for(("System Manager", "Administrator"))
	if not project or not text:
		frappe.throw(_("project and text are required"))
	if not frappe.db.exists("Farmer Project", project):
		frappe.throw(_("Farmer Project not found"))
	event_id = get_timeline_service().emit_manual_note(project, text, client_id=client_id)
	return {"event_id": event_id, "event_type": "manual_note"}
