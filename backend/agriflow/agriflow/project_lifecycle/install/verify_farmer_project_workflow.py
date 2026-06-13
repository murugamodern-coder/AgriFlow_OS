# Copyright (c) 2026, Murugan and contributors
"""Verify Farmer Project workflow install (dev bench)."""

from __future__ import annotations

import frappe
from frappe.model.workflow import apply_workflow, get_transitions


def verify() -> dict:
	out: dict = {
		"workflow_count": frappe.db.count("Workflow", {"name": "Farmer Project Lifecycle"}),
		"roles": frappe.get_all(
			"Role",
			filters=[["name", "like", "Agriflow%"]],
			pluck="name",
		),
		"projects": frappe.get_all(
			"Farmer Project",
			fields=["name", "workflow_state", "current_stage", "stage_sequence"],
			filters={"is_deleted": 0},
		),
	}
	project = "FP-2026-00007"
	if frappe.db.get_value("Farmer Project", project, "status") != "active":
		frappe.db.set_value("Farmer Project", project, "status", "active", update_modified=False)
		frappe.db.commit()
	if frappe.db.exists("Farmer Project", project):
		frappe.db.set_value(
			"Farmer Project",
			project,
			{
				"workflow_state": "Lead Captured",
				"current_stage": "lead_captured",
				"stage_sequence": 1,
			},
			update_modified=False,
		)
		frappe.db.commit()
		doc = frappe.get_doc("Farmer Project", project)
		timeline_before = frappe.db.count(
			"Timeline Event", {"farmer_project": project, "event_type": "stage_transition"}
		)
		transitions = get_transitions(doc)
		out["fp00007"] = {
			"workflow_state": doc.workflow_state,
			"current_stage": doc.current_stage,
			"transitions": [t.action for t in transitions],
			"timeline_before": timeline_before,
		}
		if doc.workflow_state == "Lead Captured" and any(
			t.action == "Verify Eligibility" for t in transitions
		):
			apply_workflow(doc, "Verify Eligibility")
			doc.reload()
			timeline_after = frappe.db.count(
				"Timeline Event",
				{"farmer_project": project, "event_type": "stage_transition"},
			)
			out["transition_test"] = {
				"workflow_state": doc.workflow_state,
				"current_stage": doc.current_stage,
				"stage_sequence": doc.stage_sequence,
				"timeline_after": timeline_after,
				"timeline_delta": timeline_after - timeline_before,
			}
			# Revert demo state
			revert = frappe.get_doc("Farmer Project", project)
			if revert.workflow_state == "Eligibility Check":
				frappe.db.set_value(
					"Farmer Project",
					project,
					{
						"workflow_state": "Lead Captured",
						"current_stage": "lead_captured",
						"stage_sequence": 1,
					},
					update_modified=False,
				)
				frappe.db.commit()
				out["reverted"] = True
	return out
