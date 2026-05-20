# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe.model.document import Document

from agriflow.farmer_registry.utils.validation import validate_geography_chain
from agriflow.project_lifecycle.services.lifecycle import LIFECYCLE_FLAG
from agriflow.project_lifecycle.services.timeline import get_timeline_service


class FarmerProject(Document):
	def before_save(self):
		if self.is_new():
			return
		prev = frappe.db.get_value(
			"Farmer Project",
			self.name,
			["status", "mimis_gate_status", "mimis_reconciliation_ref"],
			as_dict=True,
		)
		self._timeline_prev = prev or {}

	def validate(self):
		if self.is_deleted:
			self.status = "cancelled" if self.status == "active" else self.status

		validate_geography_chain(self.district, self.block, self.village, self.cluster)
		if self.cluster and self.village:
			vc = frappe.db.get_value("Village", self.village, "cluster")
			if vc and vc != self.cluster:
				frappe.throw(frappe._("Cluster must match Village"))

		if self.status == "active" and self.project_type == "subsidy" and self.farmer:
			existing = frappe.db.exists(
				"Farmer Project",
				{
					"farmer": self.farmer,
					"project_type": "subsidy",
					"status": "active",
					"is_deleted": 0,
					"name": ("!=", self.name or ""),
				},
			)
			if existing:
				frappe.throw(frappe._("Only one active subsidy project per farmer"))

		if not frappe.flags.get(LIFECYCLE_FLAG):
			self._block_direct_stage_mutation()
			self._block_history_tampering()

		if self.client_id:
			dup = frappe.db.exists(
				"Farmer Project",
				{"client_id": self.client_id, "name": ("!=", self.name or "")},
			)
			if dup:
				frappe.throw(frappe._("Client ID already exists"))

	def on_update(self):
		if self.is_new() or frappe.flags.get(LIFECYCLE_FLAG):
			return
		prev = getattr(self, "_timeline_prev", None) or {}
		timeline = get_timeline_service()

		if prev.get("mimis_gate_status") != self.mimis_gate_status:
			if self.mimis_gate_status in ("approved", "waived") and not self.mimis_approved_on:
				self.db_set("mimis_approved_on", frappe.utils.now_datetime(), update_modified=False)
			timeline.emit_mimis_gate_updated(
				self.name,
				from_status=prev.get("mimis_gate_status") or "pending",
				to_status=self.mimis_gate_status,
				mimis_reconciliation_ref=self.mimis_reconciliation_ref,
			)

		if prev.get("status") != self.status:
			timeline.emit_project_status_changed(
				self.name,
				from_status=prev.get("status"),
				to_status=self.status,
				current_stage=self.current_stage,
				stage_sequence=self.stage_sequence or 0,
			)

	def _block_direct_stage_mutation(self):
		if self.is_new():
			return
		prev = frappe.db.get_value(
			"Farmer Project",
			self.name,
			["current_stage", "stage_sequence"],
			as_dict=True,
		)
		if not prev:
			return
		if self.current_stage != prev.current_stage or int(self.stage_sequence or 0) != int(
			prev.stage_sequence or 0
		):
			frappe.throw(
				frappe._("Stage changes must use ProjectLifecycleService or transition_for_desk")
			)

	def _block_history_tampering(self):
		if frappe.session.user == "Administrator":
			return
		prev_len = frappe.db.count("Project Stage History", {"parent": self.name})
		new_len = len(self.stage_history or [])
		if new_len < prev_len:
			frappe.throw(frappe._("Stage history rows cannot be deleted"))
		if new_len > prev_len + 1:
			frappe.throw(frappe._("Stage history rows can only be appended via lifecycle service"))
