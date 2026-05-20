# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Farmer Project aggregate root — create and stage transitions."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import now_datetime

from agriflow.project_lifecycle.services.timeline import get_timeline_service
from agriflow.project_lifecycle.utils.stages import (
	get_next_stage_key,
	get_stage_map,
	user_may_transition_to,
	validate_stage_key,
)

LIFECYCLE_FLAG = "agriflow_lifecycle_write"
MIMIS_GATE_APPROVED = frozenset({"approved", "waived"})


class ProjectLifecycleService:
	def create_project(
		self,
		farmer: str,
		*,
		project_type: str = "subsidy",
		district: str | None = None,
		block: str | None = None,
		cluster: str | None = None,
		village: str | None = None,
		officer: str | None = None,
		assigned_to: str | None = None,
		priority: str = "medium",
		remarks: str | None = None,
		client_id: str | None = None,
		created_via: str = "desk",
	) -> frappe.model.document.Document:
		self._ensure_one_active_subsidy_project(farmer)
		farmer_doc = frappe.get_doc("Farmer", farmer)
		district = district or farmer_doc.district
		block = block or farmer_doc.block
		village = village or farmer_doc.village
		cluster = cluster or farmer_doc.cluster
		village_name = frappe.db.get_value("Village", village, "village_name") or village
		project_title = f"{farmer_doc.farmer_name} - {village_name}"

		doc = frappe.get_doc(
			{
				"doctype": "Farmer Project",
				"project_title": project_title,
				"farmer": farmer,
				"project_type": project_type,
				"current_stage": "lead_captured",
				"stage_sequence": 1,
				"district": district,
				"block": block,
				"cluster": cluster,
				"village": village,
				"officer": officer,
				"status": "active",
				"started_on": frappe.utils.today(),
				"assigned_to": assigned_to,
				"priority": priority,
				"remarks": remarks,
				"mimis_gate_status": "pending",
				"client_id": client_id,
				"doc_version": 1,
				"created_via": created_via,
				"stage_history": [
					{
						"from_stage": "",
						"to_stage": "lead_captured",
						"from_sequence": 0,
						"to_sequence": 1,
						"transitioned_on": now_datetime(),
						"transitioned_by": frappe.session.user,
						"notes": _("Project created"),
					}
				],
			}
		)
		frappe.flags[LIFECYCLE_FLAG] = True
		try:
			doc.insert(ignore_permissions=True)
		finally:
			frappe.flags[LIFECYCLE_FLAG] = False
		get_timeline_service().emit_project_created(doc)
		return doc

	def transition(
		self,
		project_name: str,
		target_stage: str,
		*,
		doc_version: int | None = None,
		notes: str | None = None,
		client_id: str | None = None,
		user: str | None = None,
		is_correction: bool = False,
	) -> dict[str, Any]:
		user = user or frappe.session.user
		validate_stage_key(target_stage)
		if not user_may_transition_to(user, target_stage):
			frappe.throw(_("You do not have permission to transition to stage {0}").format(target_stage))

		project = frappe.get_doc("Farmer Project", project_name)
		if project.is_deleted:
			frappe.throw(_("Project is deleted"))

		if project.status == "cancelled":
			frappe.throw(_("Cancelled projects cannot transition"))
		if project.status == "on_hold":
			frappe.throw(_("On-hold projects cannot transition until resumed"))
		if project.status == "completed":
			frappe.throw(_("Completed projects cannot transition"))

		if doc_version is not None and int(project.doc_version or 0) != int(doc_version):
			frappe.throw(
				_("Stale doc_version. Server has {0}, client sent {1}").format(
					project.doc_version, doc_version
				)
			)

		expected_next = get_next_stage_key(project.current_stage)
		if not is_correction and target_stage != expected_next:
			frappe.throw(
				_("Invalid transition. Expected next stage {0}, got {1}").format(
					expected_next, target_stage
				)
			)

		stage_map = get_stage_map()
		target_seq = stage_map[target_stage].sequence
		if not is_correction and target_seq != (project.stage_sequence or 0) + 1:
			frappe.throw(_("Stage sequence must advance by exactly 1"))

		self._validate_mimis_gate(project, target_stage)
		self._validate_officer_for_stage(project, target_seq)

		from_stage = project.current_stage
		from_sequence = project.stage_sequence or 0
		history_row = {
			"from_stage": from_stage or "",
			"to_stage": target_stage,
			"from_sequence": from_sequence,
			"to_sequence": target_seq,
			"transitioned_on": now_datetime(),
			"transitioned_by": user,
			"notes": notes or "",
			"client_id": client_id,
			"is_correction": 1 if is_correction else 0,
		}
		project.append("stage_history", history_row)
		project.current_stage = target_stage
		project.stage_sequence = target_seq
		project.doc_version = (project.doc_version or 1) + 1

		if target_stage == "subsidy_released":
			project.status = "completed"

		frappe.flags[LIFECYCLE_FLAG] = True
		try:
			project.save(ignore_permissions=True)
		finally:
			frappe.flags[LIFECYCLE_FLAG] = False

		history_row_name = project.stage_history[-1].name if project.stage_history else None
		get_timeline_service().emit_stage_transition(
			project,
			from_stage=from_stage,
			to_stage=target_stage,
			from_sequence=from_sequence,
			to_sequence=target_seq,
			history_row_name=history_row_name,
			notes=notes,
			client_id=client_id,
			actor=user,
			created_on=history_row.get("transitioned_on"),
		)
		self._log_transition(project.name, from_stage, target_stage, user)
		from agriflow.task_engine.services.templates import generate_stage_tasks

		generate_stage_tasks(project.name, target_stage)
		return {
			"name": project.name,
			"current_stage": project.current_stage,
			"stage_sequence": project.stage_sequence,
			"doc_version": project.doc_version,
			"status": project.status,
			"stage_history_row": history_row,
		}

	def _ensure_one_active_subsidy_project(self, farmer: str, exclude: str | None = None) -> None:
		filters = {
			"farmer": farmer,
			"project_type": "subsidy",
			"status": "active",
			"is_deleted": 0,
		}
		if exclude:
			filters["name"] = ("!=", exclude)
		if frappe.db.exists("Farmer Project", filters):
			frappe.throw(_("Farmer already has an active subsidy project"))

	def _validate_mimis_gate(self, project, target_stage: str) -> None:
		if target_stage != "mimis_registered":
			return
		if (project.mimis_gate_status or "pending") not in MIMIS_GATE_APPROVED:
			frappe.throw(
				_("MIMIS gate not passed. Set mimis_gate_status to approved or waived before MIMIS registration stage.")
			)

	def _validate_officer_for_stage(self, project, target_seq: int) -> None:
		if target_seq < 4:
			return
		if not project.officer:
			frappe.throw(_("Officer is required from MIMIS Registered stage onward"))
		if not project.cluster:
			return
		active = frappe.db.get_value(
			"Officer Assignment History",
			{"cluster": project.cluster, "is_active": 1},
			"officer",
		)
		if active and active != project.officer:
			msg = _("Officer {0} does not match active assignment for cluster {1}").format(
				project.officer, project.cluster
			)
			if target_seq >= 7:
				frappe.throw(msg)
			frappe.msgprint(msg, indicator="orange", alert=True)

	def _log_transition(self, project_name: str, from_stage: str, to_stage: str, user: str) -> None:
		frappe.logger("agriflow.lifecycle").info(
			"transition %s %s -> %s by %s", project_name, from_stage, to_stage, user
		)


def get_lifecycle_service() -> ProjectLifecycleService:
	return ProjectLifecycleService()
