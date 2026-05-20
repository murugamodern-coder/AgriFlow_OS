# Copyright (c) 2026, Murugan and contributors
"""Phase 15 demo seed — field officer user, open tasks, notifications, inventory."""

from __future__ import annotations

import json

import frappe
from frappe import _

DEMO_USER = "field.officer@agriflow.local"
DEMO_PROJECT = "FP-2026-00007"


def execute():
	frappe.only_for("Administrator")
	_ensure_demo_user()
	project = DEMO_PROJECT
	if not frappe.db.exists("Farmer Project", project):
		frappe.throw(_("Demo project {0} missing — run phase8 sample first").format(project))

	task_name = _ensure_open_task(project)
	out_notif = _ensure_notification_via_task(project, task_name)
	frappe.db.commit()
	return {
		"demo_user": DEMO_USER,
		"demo_password": "AgriFlow@2026",
		"demo_project": project,
		"demo_task": task_name,
		"notifications_for_officer": out_notif,
		"ok": True,
	}


def _ensure_demo_user():
	if frappe.db.exists("User", DEMO_USER):
		_ensure_block_permission()
		return
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": DEMO_USER,
			"first_name": "Field",
			"last_name": "Officer",
			"send_welcome_email": 0,
			"roles": [
				{"role": "System Manager"},
				{"role": "Store Keeper"},
			],
		}
	)
	user.insert(ignore_permissions=True)
	user.new_password = "AgriFlow@2026"
	user.save(ignore_permissions=True)
	_ensure_block_permission()


def _ensure_block_permission():
	block = frappe.db.get_value("Farmer Project", DEMO_PROJECT, "block")
	if block and not frappe.db.exists(
		"User Permission", {"user": DEMO_USER, "allow": "Block", "for_value": block}
	):
		frappe.get_doc(
			{
				"doctype": "User Permission",
				"user": DEMO_USER,
				"allow": "Block",
				"for_value": block,
				"apply_to_all_doctypes": 1,
			}
		).insert(ignore_permissions=True)


def _ensure_open_task(project: str):
	existing = frappe.get_all(
		"Project Task",
		filters={
			"farmer_project": project,
			"status": ("in", ["open", "assigned", "in_progress"]),
			"is_deleted": 0,
		},
		pluck="name",
		limit=1,
	)
	if existing:
		return existing[0]
	from agriflow.task_engine.services.lifecycle import TaskLifecycleService

	task = TaskLifecycleService().create_task(
		subject="Phase 15 demo — field visit",
		farmer_project=project,
		task_type="field_visit",
		due_date=frappe.utils.add_days(frappe.utils.today(), 3),
		priority="high",
		description="E2E validation task",
		assigned_officer=DEMO_USER,
		auto_assign=True,
	)
	return task.name


def _ensure_notification_via_task(project: str, task_name: str | None) -> int:
	if not task_name:
		return 0
	return frappe.db.count(
		"Notification",
		{"recipient": DEMO_USER, "farmer_project": project, "is_deleted": 0},
	)
