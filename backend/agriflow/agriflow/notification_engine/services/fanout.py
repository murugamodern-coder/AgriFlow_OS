# Copyright (c) 2026, Murugan and contributors
"""Timeline → notification fanout (never blocks timeline)."""

from __future__ import annotations

from typing import Any

import frappe

from agriflow.notification_engine.services.delivery import deliver_one
from agriflow.notification_engine.services.i18n_keys import title_key
from agriflow.notification_engine.services.recipients import (
	resolve_manual_note_recipients,
	resolve_project_block_recipients,
	resolve_task_recipients,
)

FANOUT_EVENT_TYPES = frozenset(
	{
		"task_assigned",
		"task_completed",
		"stage_transition",
		"manual_note",
		"mimis_gate_updated",
		"project_status_changed",
	}
)


def _project_context(project_name: str) -> dict:
	return frappe.db.get_value(
		"Farmer Project",
		project_name,
		["name", "farmer", "block", "district", "project_title", "current_stage"],
		as_dict=True,
	) or {}


def _body_preview(notification_type: str, payload: dict, project: dict) -> str:
	title = (project or {}).get("project_title") or (project or {}).get("name") or ""
	if notification_type == "task_assigned":
		return f"{payload.get('subject') or payload.get('task') or 'Task'} — {title}"[:140]
	if notification_type == "task_reassigned":
		return f"Reassigned: {payload.get('task') or ''} — {title}"[:140]
	if notification_type == "task_completed":
		return f"Completed: {payload.get('task') or ''} — {title}"[:140]
	if notification_type == "project_stage_changed":
		return f"{payload.get('from_stage')} → {payload.get('to_stage')} — {title}"[:140]
	if notification_type == "manual_note":
		text = (payload.get("text") or "")[:80]
		return f"{text} — {title}"[:140]
	return title[:140]


def _payload_with_links(
	notification_type: str, payload: dict, project: dict, task_name: str | None = None
) -> dict:
	pname = project.get("name")
	out = dict(payload or {})
	out["farmer_project"] = pname
	out["project_title"] = project.get("project_title")
	if task_name or out.get("task"):
		tn = task_name or out.get("task")
		out["deep_link"] = f"/projects/{pname}/tasks/{tn}"
	else:
		out["deep_link"] = f"/projects/{pname}/timeline"
	out["notification_type"] = notification_type
	return out


def _is_reassignment(task_name: str) -> bool:
	return frappe.db.count(
		"Project Task Assignment History", {"project_task": task_name}
	) > 1


def _fanout_task_assigned(event: frappe.model.document.Document, project: dict) -> list[dict]:
	payload = event.payload_json or {}
	if isinstance(payload, str):
		import json

		payload = json.loads(payload) if payload else {}
	task_name = payload.get("task") or event.reference_name
	notification_type = "task_reassigned" if task_name and _is_reassignment(task_name) else "task_assigned"
	recipients = resolve_task_recipients(task_name) if task_name else resolve_project_block_recipients(
		event.farmer_project
	)
	results = []
	for user in recipients:
		results.append(
			deliver_one(
				recipient=user,
				notification_type=notification_type,
				title_i18n_key=title_key(notification_type),
				body_preview=_body_preview(notification_type, payload, project),
				payload_json=_payload_with_links(notification_type, payload, project, task_name),
				farmer_project=event.farmer_project,
				farmer=event.farmer,
				block=event.block,
				district=event.district,
				timeline_event=event.name,
				source_doctype="Project Task",
				source_name=task_name,
				priority="normal",
			)
		)
	return results


def _fanout_task_completed(event, project: dict) -> list[dict]:
	payload = event.payload_json or {}
	if isinstance(payload, str):
		import json

		payload = json.loads(payload) if payload else {}
	task_name = payload.get("task") or event.reference_name
	recipients = set()
	if task_name:
		recipients.update(resolve_task_recipients(task_name))
	recipients.update(resolve_project_block_recipients(event.farmer_project))
	results = []
	for user in sorted(recipients):
		results.append(
			deliver_one(
				recipient=user,
				notification_type="task_completed",
				title_i18n_key=title_key("task_completed"),
				body_preview=_body_preview("task_completed", payload, project),
				payload_json=_payload_with_links("task_completed", payload, project, task_name),
				farmer_project=event.farmer_project,
				farmer=event.farmer,
				block=event.block,
				district=event.district,
				timeline_event=event.name,
				source_doctype="Project Task",
				source_name=task_name,
				priority="low",
			)
		)
	return results


def _fanout_stage_transition(event, project: dict) -> list[dict]:
	payload = event.payload_json or {}
	if isinstance(payload, str):
		import json

		payload = json.loads(payload) if payload else {}
	recipients = resolve_project_block_recipients(event.farmer_project)
	results = []
	for user in recipients:
		results.append(
			deliver_one(
				recipient=user,
				notification_type="project_stage_changed",
				title_i18n_key=title_key("project_stage_changed"),
				body_preview=_body_preview("project_stage_changed", payload, project),
				payload_json=_payload_with_links("project_stage_changed", payload, project),
				farmer_project=event.farmer_project,
				farmer=event.farmer,
				block=event.block,
				district=event.district,
				timeline_event=event.name,
				source_doctype="Farmer Project",
				source_name=event.farmer_project,
				priority="high",
			)
		)
	return results


def _fanout_manual_note(event, project: dict) -> list[dict]:
	payload = event.payload_json or {}
	if isinstance(payload, str):
		import json

		payload = json.loads(payload) if payload else {}
	recipients = resolve_manual_note_recipients(event.farmer_project, actor=event.actor)
	results = []
	for user in recipients:
		results.append(
			deliver_one(
				recipient=user,
				notification_type="manual_note",
				title_i18n_key=title_key("manual_note"),
				body_preview=_body_preview("manual_note", payload, project),
				payload_json=_payload_with_links("manual_note", payload, project),
				farmer_project=event.farmer_project,
				farmer=event.farmer,
				block=event.block,
				district=event.district,
				timeline_event=event.name,
				source_doctype="Timeline Event",
				source_name=event.name,
				priority="normal",
			)
		)
	return results


def _fanout_system_alert(event, project: dict, *, subtype: str) -> list[dict]:
	payload = event.payload_json or {}
	if isinstance(payload, str):
		import json

		payload = json.loads(payload) if payload else {}
	payload["alert_subtype"] = subtype
	recipients = resolve_project_block_recipients(event.farmer_project)
	results = []
	for user in recipients:
		results.append(
			deliver_one(
				recipient=user,
				notification_type="system_alert",
				title_i18n_key=title_key("system_alert"),
				body_preview=_body_preview("system_alert", payload, project),
				payload_json=_payload_with_links("system_alert", payload, project),
				farmer_project=event.farmer_project,
				farmer=event.farmer,
				block=event.block,
				district=event.district,
				timeline_event=event.name,
				source_doctype=event.reference_doctype or "Farmer Project",
				source_name=event.reference_name or event.farmer_project,
				priority="normal",
			)
		)
	return results


def deliver_for_timeline_event(timeline_event_id: str) -> list[dict[str, Any]]:
	"""Fan out notifications for one timeline row. Safe to call on replay."""
	if not timeline_event_id or not frappe.db.exists("Timeline Event", timeline_event_id):
		return []
	event = frappe.get_doc("Timeline Event", timeline_event_id)
	if event.is_deleted:
		return []
	if event.event_type not in FANOUT_EVENT_TYPES:
		return []

	project = _project_context(event.farmer_project)
	if not project:
		return []

	if event.event_type == "task_assigned":
		return _fanout_task_assigned(event, project)
	if event.event_type == "task_completed":
		return _fanout_task_completed(event, project)
	if event.event_type == "stage_transition":
		return _fanout_stage_transition(event, project)
	if event.event_type == "manual_note":
		return _fanout_manual_note(event, project)
	if event.event_type in ("mimis_gate_updated", "project_status_changed"):
		return _fanout_system_alert(event, project, subtype=event.event_type)

	return []
