# Copyright (c) 2026, Murugan and contributors
"""Phase 11 — verify sync.pull / sync.push."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import sync as sync_api
from agriflow.task_engine.services.assignment import TaskAssignmentService
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

PROJECT = "FP-2026-00007"


def execute():
	frappe.only_for("Administrator")
	errors: list[str] = []
	report: dict = {}
	run_id = frappe.generate_hash(length=8)

	# --- pull foundation ---
	p1 = sync_api.pull(
		{
			"entities": ["timeline", "task", "farmer_project"],
			"modified_since": {},
			"limits": {"timeline": 3, "task": 2, "farmer_project": 2},
		}
	)
	if not p1.get("ok"):
		errors.append(f"pull failed: {p1}")
	else:
		report["pull_ok"] = True
		report["sync_token_pull"] = p1["data"].get("sync_token")
		tasks = p1["data"]["entities"]["task"]
		report["pull_task_page1"] = len(tasks["items"])
		cursor = tasks.get("cursor")
		if cursor:
			p2 = sync_api.pull(
				{
					"entities": ["task"],
					"modified_since": {},
					"cursors": {"task": cursor},
					"limits": {"task": 2},
				}
			)
			if p2.get("ok"):
				ids1 = {i["name"] for i in tasks["items"]}
				ids2 = {i["name"] for i in p2["data"]["entities"]["task"]["items"]}
				report["task_cursor_overlap"] = list(ids1 & ids2)
				if ids1 & ids2:
					errors.append("task pull cursor overlap")
			else:
				errors.append(f"pull page2: {p2}")
		wm = p1["data"].get("server_watermark") or {}
		report["watermarks"] = wm
		if not wm.get("timeline") and p1["data"]["entities"]["timeline"]["items"]:
			errors.append("timeline watermark missing")

	# --- push replay ---
	cmid = f"phase11-verify-replay-{run_id}"
	cid = f"phase11-verify-task-{run_id}"
	push1 = sync_api.push(
		{
			"operations": [
				{
					"client_mutation_id": cmid,
					"op_type": "create",
					"entity": "task",
					"client_id": cid,
					"payload": {
						"subject": "Sync verify task",
						"farmer_project": PROJECT,
						"task_type": "follow_up",
						"due_date": "2099-08-01",
					},
				}
			]
		}
	)
	if not push1.get("ok"):
		errors.append(f"push1: {push1}")
	else:
		name1 = push1["data"]["results"][0].get("name")
		push2 = sync_api.push(
			{
				"operations": [
					{
						"client_mutation_id": cmid,
						"op_type": "create",
						"entity": "task",
						"client_id": cid,
						"payload": {
							"subject": "Sync verify task",
							"farmer_project": PROJECT,
							"task_type": "follow_up",
							"due_date": "2099-08-01",
						},
					}
				]
			}
		)
		if not push2.get("ok"):
			errors.append(f"push2: {push2}")
		else:
			r2 = push2["data"]["results"][0]
			report["replay_status"] = r2.get("status")
			report["replay_flag"] = r2.get("replay")
			name2 = r2.get("name")
			if r2.get("status") != "skipped" or name1 != name2:
				errors.append("replay idempotency failed")
			logs = frappe.db.count("Sync Mutation Log", {"client_mutation_id": cmid})
			report["mutation_log_count"] = logs
			if logs != 1:
				errors.append(f"expected 1 mutation log, got {logs}")

	# --- stale conflict partial batch ---
	officer = frappe.db.get_value("Farmer Project", PROJECT, "officer") or "OFF01"
	tdoc = TaskLifecycleService().create_task(
		subject="Sync stale test",
		farmer_project=PROJECT,
		task_type="verification",
		due_date="2099-09-01",
		client_id="phase11-stale-task",
	)
	TaskAssignmentService().assign(tdoc.name, officer, reason="initial")
	tdoc.reload()
	stale_batch = sync_api.push(
		{
			"operations": [
				{
					"client_mutation_id": f"phase11-stale-ok-{run_id}",
					"op_type": "note",
					"entity": "timeline",
					"client_id": f"phase11-note-ok-{run_id}",
					"payload": {"farmer_project": PROJECT, "text": "ok note"},
				},
				{
					"client_mutation_id": f"phase11-stale-fail-{run_id}",
					"op_type": "update",
					"entity": "task",
					"payload": {
						"name": tdoc.name,
						"doc_version": int(tdoc.doc_version or 1) - 1,
						"description": "stale",
					},
				},
			]
		}
	)
	report["stale_partial_ok"] = stale_batch.get("ok") is True
	report["stale_partial_code"] = (stale_batch.get("error") or {}).get("code")
	report["stale_http"] = frappe.local.response.get("http_status_code")
	report["stale_summary"] = (stale_batch.get("data") or {}).get("summary")
	if stale_batch.get("data"):
		statuses = [r.get("status") for r in stale_batch["data"]["results"]]
		report["stale_statuses"] = statuses
		if statuses[0] != "success":
			errors.append("first op should succeed")
		if statuses[1] != "conflict":
			errors.append("second op should conflict")
	if report.get("stale_partial_code") != "SYNC_PARTIAL_FAILURE":
		errors.append(
			f"expected partial envelope SYNC_PARTIAL_FAILURE got {report.get('stale_partial_code')}"
		)

	# --- timeline note ---
	note = sync_api.push(
		{
			"operations": [
				{
					"client_mutation_id": f"phase11-note-standalone-{run_id}",
					"op_type": "note",
					"entity": "timeline",
					"client_id": f"phase11-note-standalone-cid-{run_id}",
					"payload": {"farmer_project": PROJECT, "text": "Phase 11 verify note"},
				}
			]
		}
	)
	if note.get("ok"):
		eid = note["data"]["results"][0].get("name")
		report["timeline_note_event"] = eid
		if not frappe.db.exists("Timeline Event", eid):
			errors.append("timeline event not created")

	# --- project.transition blocked ---
	blocked = sync_api.push(
		{
			"operations": [
				{
					"client_mutation_id": f"phase11-no-transition-{run_id}",
					"op_type": "update",
					"entity": "farmer_project",
					"payload": {"name": PROJECT, "doc_version": 1},
				}
			]
		}
	)
	if blocked.get("ok"):
		st = blocked["data"]["results"][0].get("status")
		if st != "failed":
			errors.append("farmer_project push should fail")
	else:
		report["transition_blocked"] = True

	report["ok"] = len(errors) == 0
	report["errors"] = errors
	print(report)
