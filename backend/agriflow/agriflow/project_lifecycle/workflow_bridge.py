# Copyright (c) 2026, Murugan and contributors
"""Bridge Frappe Workflow actions to ProjectLifecycleService (fallback path unchanged)."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.services.lifecycle import get_lifecycle_service

WORKFLOW_BRIDGE_FLAG = "agriflow_workflow_bridge"

WORKFLOW_TO_STAGE: dict[str, str] = {
	"Lead Captured": "lead_captured",
	"Eligibility Check": "eligibility_check",
	"Documents Collected": "documents_collected",
	"MIMIS Registered": "mimis_registered",
	"Field Survey": "field_survey",
	"Quotation Generated": "quotation_generated",
	"Pre-Inspection Approval": "pre_inspection_approval",
	"Work Order Received": "work_order_received",
	"Material Dispatched": "material_dispatched",
	"Installation Done": "installation_done",
	"Post-Inspection Approval": "post_inspection_approval",
	"Subsidy Released": "subsidy_released",
}

STAGE_TO_WORKFLOW: dict[str, str] = {v: k for k, v in WORKFLOW_TO_STAGE.items()}


def workflow_state_for_stage(stage_key: str | None) -> str:
	if not stage_key:
		return "Lead Captured"
	return STAGE_TO_WORKFLOW.get(stage_key, "Lead Captured")


def sync_workflow_state_from_stage(doc) -> None:
	"""Set workflow_state from current_stage on insert / backfill."""
	target = workflow_state_for_stage(doc.current_stage)
	if doc.workflow_state != target:
		doc.workflow_state = target


def on_workflow_state_change(doc, method=None) -> None:
	"""After Frappe Workflow updates workflow_state, drive lifecycle + timeline."""
	if frappe.flags.get(WORKFLOW_BRIDGE_FLAG):
		return
	if doc.is_new():
		return

	prev_state = getattr(doc, "_prev_workflow_state", None)
	if prev_state is None and doc.name:
		prev_state = frappe.db.get_value("Farmer Project", doc.name, "workflow_state")
	if not doc.workflow_state or doc.workflow_state == prev_state:
		return

	target_stage = WORKFLOW_TO_STAGE.get(doc.workflow_state)
	if not target_stage:
		return
	if doc.current_stage == target_stage:
		return

	frappe.flags[WORKFLOW_BRIDGE_FLAG] = True
	try:
		get_lifecycle_service().transition(
			doc.name,
			target_stage,
			notes=f"Workflow: {prev_state or '—'} → {doc.workflow_state}",
		)
	finally:
		frappe.flags[WORKFLOW_BRIDGE_FLAG] = False
