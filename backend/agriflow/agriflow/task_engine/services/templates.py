# Copyright (c) 2026, Murugan and contributors
"""Idempotent stage task generation from JSON fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frappe
from frappe.utils import add_days, today


def template_client_id(farmer_project: str, template_id: str) -> str:
	"""Deterministic idempotency key within 36 chars."""
	return hashlib.sha256(f"{farmer_project}|{template_id}".encode()).hexdigest()[:32]

from agriflow.task_engine.services.lifecycle import TaskLifecycleService

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "task_template.json"


def load_task_templates() -> list[dict]:
	if not FIXTURE_PATH.exists():
		return []
	with FIXTURE_PATH.open(encoding="utf-8") as fh:
		data = json.load(fh)
	return data if isinstance(data, list) else []


def generate_stage_tasks(farmer_project: str, to_stage: str) -> list[str]:
	"""Create template tasks for entered stage; idempotent by source_template + stage_key."""
	project = frappe.get_doc("Farmer Project", farmer_project)
	created: list[str] = []
	lifecycle = TaskLifecycleService()

	for tpl in load_task_templates():
		if tpl.get("to_stage") != to_stage:
			continue
		template_id = tpl["template_id"]
		if frappe.db.exists(
			"Project Task",
			{
				"farmer_project": farmer_project,
				"source_template": template_id,
				"stage_key": to_stage,
				"is_deleted": 0,
			},
		):
			continue

		officer = None
		if tpl.get("default_officer_from") == "project.officer":
			officer = project.officer

		due = add_days(today(), int(tpl.get("due_offset_days", 3)))
		doc = lifecycle.create_task(
			subject=tpl["subject"],
			farmer_project=farmer_project,
			task_type=tpl["task_type"],
			due_date=due,
			priority=tpl.get("priority", "normal"),
			stage_key=to_stage,
			source_template=template_id,
			assigned_officer=officer,
			auto_assign=bool(officer),
			client_id=template_client_id(farmer_project, template_id),
		)
		created.append(doc.name)
	return created
