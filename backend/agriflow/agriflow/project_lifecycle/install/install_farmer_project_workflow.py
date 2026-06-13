# Copyright (c) 2026, Murugan and contributors
"""Install Farmer Project Lifecycle workflow (idempotent)."""

from __future__ import annotations

import json
from pathlib import Path

import frappe

WORKFLOW_NAME = "Farmer Project Lifecycle"
WORKFLOW_JSON = (
	Path(__file__).resolve().parents[2]
	/ "workflow"
	/ "farmer_project_workflow"
	/ "farmer_project_workflow.json"
)


def _load_workflow_data() -> dict:
	with WORKFLOW_JSON.open(encoding="utf-8") as handle:
		return json.load(handle)


def _ensure_child_doctypes(data: dict) -> dict:
	for row in data.get("states") or []:
		row.setdefault("doctype", "Workflow Document State")
	for row in data.get("transitions") or []:
		row.setdefault("doctype", "Workflow Transition")
	return data


def _ensure_workflow_states(data: dict) -> None:
	for row in data.get("states") or []:
		state_name = row.get("state")
		if not state_name or frappe.db.exists("Workflow State", state_name):
			continue
		frappe.get_doc(
			{
				"doctype": "Workflow State",
				"workflow_state_name": state_name,
				"style": row.get("style") or "Primary",
			}
		).insert(ignore_permissions=True)


def _ensure_workflow_actions(data: dict) -> None:
	seen: set[str] = set()
	for row in data.get("transitions") or []:
		action = row.get("action")
		if not action or action in seen:
			continue
		seen.add(action)
		if frappe.db.exists("Workflow Action Master", action):
			continue
		frappe.get_doc(
			{
				"doctype": "Workflow Action Master",
				"workflow_action_name": action,
			}
		).insert(ignore_permissions=True)


def after_migrate() -> None:
	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		return

	data = _ensure_child_doctypes(_load_workflow_data())
	_ensure_workflow_states(data)
	_ensure_workflow_actions(data)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	frappe.logger("agriflow.workflow").info("Installed workflow %s", WORKFLOW_NAME)
