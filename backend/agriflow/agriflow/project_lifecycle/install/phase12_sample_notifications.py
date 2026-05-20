# Copyright (c) 2026, Murugan and contributors
"""Seed sample notifications via timeline + task actions."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

PROJECT = "FP-2026-00007"


def execute():
	frappe.only_for("Administrator")
	timeline = get_timeline_service()
	timeline.emit_manual_note(PROJECT, "Phase 12 sample: manual note for inbox")
	officer = frappe.db.get_value("Farmer Project", PROJECT, "officer") or "OFF01"
	task = TaskLifecycleService().create_task(
		subject="Phase 12 sample task",
		farmer_project=PROJECT,
		task_type="verification",
		due_date="2099-11-01",
		client_id="phase12-sample-task",
	)
	TaskAssignmentService().assign(task.name, officer, reason="initial")
	print(
		{
			"project": PROJECT,
			"task": task.name,
			"notifications": frappe.db.count("Notification"),
		}
	)
