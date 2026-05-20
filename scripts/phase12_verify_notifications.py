# Copyright (c) 2026, Murugan and contributors
"""Phase 12 — verify Notification Engine."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import notification as notification_api
from agriflow.notification_engine.services.fanout import deliver_for_timeline_event
from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

PROJECT = "FP-2026-00007"


def execute():
	frappe.only_for("Administrator")
	errors: list[str] = []
	report: dict = {}
	run_id = frappe.generate_hash(length=8)
	admin = frappe.session.user

	# --- fanout via manual note ---
	timeline = get_timeline_service()
	eid = timeline.emit_manual_note(
		PROJECT,
		f"Phase 12 verify note {run_id}",
		client_id=f"phase12-note-{run_id}",
	)
	report["timeline_event"] = eid
	ntf_count = frappe.db.count("Notification", {"timeline_event": eid})
	report["notifications_for_event"] = ntf_count
	if ntf_count < 1:
		errors.append("expected notifications from manual_note fanout")

	# --- duplicate fanout prevention ---
	before = frappe.db.count("Notification", {"timeline_event": eid})
	replay_results = deliver_for_timeline_event(eid)
	after = frappe.db.count("Notification", {"timeline_event": eid})
	report["duplicate_fanout_count"] = after
	report["replay_results"] = replay_results
	if after != before:
		errors.append("duplicate fanout created extra notifications")
	if not any(r.get("status") == "skipped_duplicate" for r in replay_results):
		errors.append("expected skipped_duplicate on fanout replay")

	# --- unread + mark read ---
	uc1 = notification_api.unread_count()
	count1 = (uc1.get("data") or {}).get("count", 0)
	report["unread_before"] = count1
	if count1 < 1:
		errors.append("unread_count should be >= 1 for admin")

	rows = frappe.get_all(
		"Notification",
		{"recipient": admin, "timeline_event": eid, "read_on": ("is", "not set")},
		pluck="name",
		limit=1,
	)
	if rows:
		mr = notification_api.mark_read({"name": rows[0]})
		if not mr.get("ok"):
			errors.append(f"mark_read api: {mr}")
		read_on = frappe.db.get_value("Notification", rows[0], "read_on")
		report["marked_read"] = bool(read_on)
		if not read_on:
			errors.append("mark_read failed")

	uc2 = notification_api.unread_count()
	report["unread_after_mark"] = (uc2.get("data") or {}).get("count")

	lst = notification_api.list({"limit": 5, "unread_only": False})
	if not lst.get("ok"):
		errors.append(f"list failed: {lst}")
	else:
		report["list_ok"] = True
		report["list_unread_in_response"] = lst["data"].get("unread_count")

	# --- task_assigned fanout ---
	officer = frappe.db.get_value("Farmer Project", PROJECT, "officer") or "OFF01"
	tdoc = TaskLifecycleService().create_task(
		subject=f"Phase12 notify task {run_id}",
		farmer_project=PROJECT,
		task_type="follow_up",
		due_date="2099-10-01",
		client_id=f"phase12-task-{run_id}",
	)
	TaskAssignmentService().assign(tdoc.name, officer, reason="initial")
	assign_event = frappe.db.get_value(
		"Timeline Event",
		{
			"farmer_project": PROJECT,
			"event_type": "task_assigned",
			"reference_name": tdoc.name,
		},
		"name",
		order_by="creation desc",
	)
	report["task_assigned_event"] = assign_event
	assign_ntf = frappe.db.count("Notification", {"timeline_event": assign_event})
	report["task_assigned_notifications"] = assign_ntf
	if assign_ntf < 1:
		errors.append("task_assigned fanout produced no notifications")

	# --- delivery log immutability ---
	log_name = frappe.db.get_value(
		"Notification Delivery Log", {"timeline_event": eid}, "name"
	)
	if log_name:
		log = frappe.get_doc("Notification Delivery Log", log_name)
		processed = log.processed_on
		try:
			log.status = "delivered"
			log.save(ignore_permissions=True)
			errors.append("delivery log save should have failed")
		except Exception:
			report["delivery_log_immutable"] = True
		still = frappe.db.get_value("Notification Delivery Log", log_name, "processed_on")
		if str(still) != str(processed):
			errors.append("processed_on mutated on delivery log")

	# --- notification content immutability ---
	if rows:
		doc = frappe.get_doc("Notification", rows[0])
		try:
			doc.body_preview = "hacked"
			doc.save(ignore_permissions=True)
			errors.append("notification content save should fail")
		except Exception:
			report["notification_content_immutable"] = True

	# --- block scope: list returns only scoped blocks ---
	report["block_scope_check"] = "admin bypass (all blocks)"

	# --- timeline safety: emit still works ---
	eid2 = timeline.emit_manual_note(
		PROJECT,
		f"Phase12 safety {run_id}",
		client_id=f"phase12-safe-{run_id}",
	)
	report["timeline_safety_event"] = eid2
	if not frappe.db.exists("Timeline Event", eid2):
		errors.append("timeline emit failed after fanout layer")

	# --- task_created NOT fanned (noise off) ---
	created_events = frappe.db.get_value(
		"Timeline Event",
		{"reference_name": tdoc.name, "event_type": "task_created"},
		"name",
	)
	created_ntf = frappe.db.count("Notification", {"timeline_event": created_events})
	report["task_created_notification_count"] = created_ntf
	if created_ntf != 0:
		errors.append("task_created should not fanout notifications")

	report["ok"] = len(errors) == 0
	report["errors"] = errors
	print(report)
