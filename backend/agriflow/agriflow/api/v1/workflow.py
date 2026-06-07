# Copyright (c) 2026, Murugan and contributors
"""Farmer Project workflow actions for mobile (Frappe Workflow bridge)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow, get_transitions, get_workflow

from agriflow.api.v1.permissions import assert_project_access, ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success

WORKFLOW_NAME = "Farmer Project Lifecycle"

ALL_STAGES: list[dict[str, Any]] = [
	{"order": 1, "key": "lead_captured", "state": "Lead Captured", "label_ta": "முன்னோடி பதிவு", "color": "blue"},
	{"order": 2, "key": "eligibility_check", "state": "Eligibility Check", "label_ta": "தகுதி சரிபார்ப்பு", "color": "blue"},
	{"order": 3, "key": "documents_collected", "state": "Documents Collected", "label_ta": "ஆவணங்கள் சேகரிப்பு", "color": "orange"},
	{"order": 4, "key": "mimis_registered", "state": "MIMIS Registered", "label_ta": "MIMIS பதிவு", "color": "orange"},
	{"order": 5, "key": "field_survey", "state": "Field Survey", "label_ta": "களப்பணி", "color": "orange"},
	{"order": 6, "key": "quotation_generated", "state": "Quotation Generated", "label_ta": "விலை மதிப்பீடு", "color": "orange"},
	{"order": 7, "key": "pre_inspection_approval", "state": "Pre-Inspection Approval", "label_ta": "முன் ஆய்வு ஒப்புதல்", "color": "yellow"},
	{"order": 8, "key": "work_order_received", "state": "Work Order Received", "label_ta": "பணி உத்தரவு", "color": "yellow"},
	{"order": 9, "key": "material_dispatched", "state": "Material Dispatched", "label_ta": "பொருள் அனுப்பப்பட்டது", "color": "yellow"},
	{"order": 10, "key": "installation_done", "state": "Installation Done", "label_ta": "நிறுவல் முடிந்தது", "color": "green"},
	{"order": 11, "key": "post_inspection_approval", "state": "Post-Inspection Approval", "label_ta": "பின் ஆய்வு ஒப்புதல்", "color": "green"},
	{"order": 12, "key": "subsidy_released", "state": "Subsidy Released", "label_ta": "மானியம் வழங்கப்பட்டது", "color": "purple"},
]


def _load_project(project_name: str):
	if not project_name:
		frappe.throw(_("project_name is required"), exc=frappe.ValidationError)
	if not frappe.db.exists("Farmer Project", {"name": project_name, "is_deleted": 0}):
		frappe.throw(_("Farmer Project not found"), exc=frappe.DoesNotExistError)
	assert_project_access(project_name)
	return frappe.get_doc("Farmer Project", project_name)


def _workflow_payload(project) -> dict[str, Any]:
	try:
		get_workflow("Farmer Project")
	except frappe.DoesNotExistError:
		return {
			"current_state": project.workflow_state or "Lead Captured",
			"current_stage": project.current_stage,
			"stage_sequence": project.stage_sequence or 1,
			"doc_version": project.doc_version or 1,
			"status": project.status,
			"actions": [],
			"all_stages": ALL_STAGES,
			"error": "Workflow not configured",
		}

	current_state = project.workflow_state or "Lead Captured"
	transitions = get_transitions(project)
	available = [
		{
			"action": t.action,
			"next_state": t.next_state,
			"allowed_role": t.allowed,
		}
		for t in transitions
	]
	return {
		"current_state": current_state,
		"current_stage": project.current_stage,
		"stage_sequence": project.stage_sequence or 1,
		"doc_version": project.doc_version or 1,
		"status": project.status,
		"actions": available,
		"all_stages": ALL_STAGES,
	}


@frappe.whitelist()
def get_available_actions(data=None):
	"""Return allowed workflow actions for the current user on a project."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		project_name = payload.get("project_name") or frappe.form_dict.get("project_name")
		project = _load_project(project_name)
		return success(_workflow_payload(project))
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)


@frappe.whitelist()
def apply_workflow_action(data=None):
	"""Apply a workflow action (transition) via the Frappe workflow bridge."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		project_name = payload.get("project_name")
		action = payload.get("action")
		if not project_name or not action:
			return fail("VAL_INVALID", _("project_name and action are required"), http_status=400)

		project = _load_project(project_name)
		if project.status == "on_hold":
			return fail("VAL_INVALID", _("On-hold projects cannot transition until resumed"), http_status=400)

		allowed = _workflow_payload(project)["actions"]
		valid_actions = {row["action"] for row in allowed}
		if action not in valid_actions:
			return fail(
				"VAL_INVALID",
				_("Action '{0}' is not allowed for current state '{1}' or your role.").format(
					action, project.workflow_state
				),
				http_status=400,
			)

		apply_workflow(project, action)
		project.reload()
		return success(
			{
				"success": True,
				"new_state": project.workflow_state,
				"new_stage": project.current_stage,
				"new_sequence": project.stage_sequence,
				"doc_version": project.doc_version,
			}
		)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
