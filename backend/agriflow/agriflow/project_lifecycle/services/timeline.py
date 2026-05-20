# Copyright (c) 2026, Murugan and contributors
"""Unified timeline activity stream — append-only Timeline Event rows."""

from __future__ import annotations

import json
from typing import Any, Literal

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.utils import cstr, get_fullname, now_datetime

TIMELINE_FLAG = "agriflow_timeline_write"
MAX_NOTE_LEN = 2000
MAX_PAYLOAD_KEYS = 32
VALID_EVENT_TYPES = frozenset(
	{
		"project_created",
		"stage_transition",
		"mimis_gate_updated",
		"project_status_changed",
		"manual_note",
		"task_created",
		"task_assigned",
		"task_status_changed",
		"task_completed",
	}
)


class TimelineService:
	def emit(
		self,
		event_type: str,
		farmer_project: str,
		*,
		payload: dict | None = None,
		event_source: str = "lifecycle",
		reference_doctype: str | None = None,
		reference_name: str | None = None,
		client_id: str | None = None,
		created_on: str | None = None,
		actor: str | None = None,
		skip_idempotency: bool = False,
	) -> str:
		"""Insert one immutable timeline event; returns event name."""
		self._validate_payload(payload)
		project = frappe.db.get_value(
			"Farmer Project",
			farmer_project,
			["farmer", "district", "block", "name"],
			as_dict=True,
		)
		if not project:
			frappe.throw(_("Farmer Project not found"))

		if client_id and not skip_idempotency:
			existing = frappe.db.exists(
				"Timeline Event",
				{
					"client_id": client_id,
					"event_type": event_type,
					"farmer_project": farmer_project,
					"is_deleted": 0,
				},
			)
			if existing:
				try:
					from agriflow.notification_engine.services.fanout import deliver_for_timeline_event

					deliver_for_timeline_event(existing)
				except Exception:
					frappe.log_error(frappe.get_traceback(), "notification.fanout")
				return existing

		actor = actor or frappe.session.user
		actor_name = get_fullname(actor) or actor

		doc = frappe.get_doc(
			{
				"doctype": "Timeline Event",
				"farmer_project": farmer_project,
				"farmer": project.farmer,
				"event_type": event_type,
				"event_source": event_source,
				"created_on": created_on or now_datetime(),
				"actor": actor,
				"actor_name": actor_name,
				"payload_json": payload or {},
				"reference_doctype": reference_doctype,
				"reference_name": reference_name,
				"district": project.district,
				"block": project.block,
				"client_id": client_id,
				"is_deleted": 0,
			}
		)
		frappe.flags[TIMELINE_FLAG] = True
		try:
			doc.insert(ignore_permissions=True)
		finally:
			frappe.flags[TIMELINE_FLAG] = False
		event_id = doc.name
		try:
			from agriflow.notification_engine.services.fanout import deliver_for_timeline_event

			deliver_for_timeline_event(event_id)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "notification.fanout")
		return event_id

	def query(
		self,
		*,
		farmer_project: str | None = None,
		farmer: str | None = None,
		event_types: list[str] | None = None,
		since: str | None = None,
		since_exclusive: bool = False,
		limit: int = 50,
		cursor: str | None = None,
		order: Literal["desc", "asc"] = "desc",
	) -> dict[str, Any]:
		"""Keyset pagination on (created_on, name). Raw cursor = event name."""
		limit = min(max(int(limit or 50), 1), 100)
		if event_types:
			invalid = [e for e in event_types if e not in VALID_EVENT_TYPES]
			if invalid:
				frappe.throw(_("Invalid event_types: {0}").format(", ".join(invalid)))

		te = frappe.qb.DocType("Timeline Event")
		q = (
			frappe.qb.from_(te)
			.select(
				te.name,
				te.farmer_project,
				te.farmer,
				te.event_type,
				te.event_source,
				te.created_on,
				te.actor,
				te.actor_name,
				te.payload_json,
				te.reference_doctype,
				te.reference_name,
				te.client_id,
			)
			.where(te.is_deleted == 0)
		)

		if farmer_project:
			q = q.where(te.farmer_project == farmer_project)
		if farmer:
			q = q.where(te.farmer == farmer)
		if event_types:
			q = q.where(te.event_type.isin(event_types))
		if since:
			if since_exclusive:
				q = q.where(te.created_on > since)
			else:
				q = q.where(te.created_on >= since)

		if cursor:
			cursor_row = frappe.db.get_value(
				"Timeline Event",
				cursor,
				["created_on", "name"],
				as_dict=True,
			)
			if cursor_row:
				if order == "desc":
					q = q.where(
						(te.created_on < cursor_row.created_on)
						| (
							(te.created_on == cursor_row.created_on)
							& (te.name < cursor_row.name)
						)
					)
				else:
					q = q.where(
						(te.created_on > cursor_row.created_on)
						| (
							(te.created_on == cursor_row.created_on)
							& (te.name > cursor_row.name)
						)
					)

		if order == "desc":
			q = q.orderby(te.created_on, order=Order.desc).orderby(te.name, order=Order.desc)
		else:
			q = q.orderby(te.created_on, order=Order.asc).orderby(te.name, order=Order.asc)

		rows = q.limit(limit + 1).run(as_dict=True)

		next_cursor = None
		has_more = len(rows) > limit
		if has_more:
			rows = rows[:limit]
			next_cursor = rows[-1].name

		return {
			"items": [self.to_mobile_event(r) for r in rows],
			"next_cursor": next_cursor,
			"has_more": has_more,
			"limit": limit,
		}

	def build_project_feed(self, farmer_project: str, *, limit: int = 100) -> list[dict[str, Any]]:
		result = self.query(farmer_project=farmer_project, limit=limit)
		return result["items"]

	def to_mobile_event(self, row) -> dict[str, Any]:
		payload = row.payload_json
		if isinstance(payload, str):
			try:
				payload = json.loads(payload)
			except json.JSONDecodeError:
				payload = {}
		if not isinstance(payload, dict):
			payload = {}
		created_on = row.created_on
		if hasattr(created_on, "isoformat"):
			created_on = created_on.isoformat()
		return {
			"id": row.name,
			"event_type": row.event_type,
			"event_source": row.event_source,
			"created_on": created_on,
			"actor": {"user": row.actor, "display_name": row.actor_name or row.actor},
			"farmer_project": row.farmer_project,
			"farmer": row.farmer,
			"payload": payload,
			"reference": {
				"doctype": row.reference_doctype,
				"name": row.reference_name,
			},
			"client_id": row.client_id,
		}

	def emit_project_created(self, project) -> str:
		return self.emit(
			"project_created",
			project.name,
			payload={
				"project_type": project.project_type,
				"current_stage": project.current_stage,
				"stage_sequence": project.stage_sequence,
			},
			event_source=project.created_via or "lifecycle",
			reference_doctype="Farmer Project",
			reference_name=project.name,
			client_id=f"{project.client_id}-created" if project.client_id else None,
		)

	def emit_stage_transition(
		self,
		project,
		*,
		from_stage: str,
		to_stage: str,
		from_sequence: int,
		to_sequence: int,
		history_row_name: str | None,
		notes: str | None = None,
		client_id: str | None = None,
		actor: str | None = None,
		created_on: str | None = None,
	) -> str:
		return self.emit(
			"stage_transition",
			project.name,
			payload={
				"from_stage": from_stage or "",
				"to_stage": to_stage,
				"from_sequence": from_sequence,
				"to_sequence": to_sequence,
				"history_row": history_row_name,
				"notes": (notes or "")[:MAX_NOTE_LEN],
			},
			event_source="lifecycle",
			reference_doctype="Project Stage History",
			reference_name=history_row_name,
			client_id=client_id,
			actor=actor,
			created_on=created_on,
		)

	def emit_mimis_gate_updated(
		self,
		project_name: str,
		*,
		from_status: str,
		to_status: str,
		mimis_reconciliation_ref: str | None = None,
	) -> str:
		return self.emit(
			"mimis_gate_updated",
			project_name,
			payload={
				"from_status": from_status,
				"to_status": to_status,
				"mimis_reconciliation_ref": mimis_reconciliation_ref,
			},
			event_source="mimis",
		)

	def emit_project_status_changed(
		self,
		project_name: str,
		*,
		from_status: str,
		to_status: str,
		current_stage: str,
		stage_sequence: int,
	) -> str:
		return self.emit(
			"project_status_changed",
			project_name,
			payload={
				"from_status": from_status,
				"to_status": to_status,
				"current_stage": current_stage,
				"stage_sequence": stage_sequence,
			},
			event_source="lifecycle",
		)

	def emit_manual_note(self, farmer_project: str, text: str, *, client_id: str | None = None) -> str:
		return self.emit(
			"manual_note",
			farmer_project,
			payload={"text": cstr(text)[:MAX_NOTE_LEN], "visibility": "internal"},
			event_source="desk",
			client_id=client_id,
		)

	def _validate_payload(self, payload: dict | None) -> None:
		if not payload:
			return
		if len(payload) > MAX_PAYLOAD_KEYS:
			frappe.throw(_("Timeline payload has too many keys"))
		encoded = json.dumps(payload, default=str)
		if len(encoded) > 8000:
			frappe.throw(_("Timeline payload is too large"))



	def emit_task_created(self, task) -> str:
		return self.emit(
			"task_created",
			task.farmer_project,
			payload={
				"task": task.name,
				"subject": task.subject,
				"task_type": task.task_type,
				"status": task.status,
				"priority": task.priority,
				"due_date": str(task.due_date) if task.due_date else None,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
			client_id=_task_timeline_client_id(task, "created"),
		)

	def emit_task_assigned(
		self,
		task,
		*,
		officer: str,
		assigned_to: str | None = None,
		reason: str | None = None,
	) -> str:
		return self.emit(
			"task_assigned",
			task.farmer_project,
			payload={
				"task": task.name,
				"officer": officer,
				"assigned_to": assigned_to,
				"reason": reason,
				"status": task.status,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)

	def emit_task_status_changed(
		self,
		task,
		*,
		from_status: str,
		to_status: str,
		note: str | None = None,
	) -> str:
		return self.emit(
			"task_status_changed",
			task.farmer_project,
			payload={
				"task": task.name,
				"from_status": from_status,
				"to_status": to_status,
				"note": (note or "")[:MAX_NOTE_LEN],
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)

	def emit_task_completed(self, task) -> str:
		return self.emit(
			"task_completed",
			task.farmer_project,
			payload={
				"task": task.name,
				"visit_outcome": (task.visit_outcome or "")[:MAX_NOTE_LEN],
				"completed_on": str(task.completed_on) if task.completed_on else None,
			},
			event_source="task_engine",
			reference_doctype="Project Task",
			reference_name=task.name,
		)


def _task_timeline_client_id(task, suffix: str) -> str | None:
	"""Timeline client_id max 36 chars — use task name hash when needed."""
	base = (task.client_id or task.name or "")[:32]
	if not base:
		return None
	key = f"{base}-{suffix}"
	return key if len(key) <= 36 else base[: max(0, 36 - len(suffix) - 1)] + "-" + suffix

def get_timeline_service() -> TimelineService:
	return TimelineService()
