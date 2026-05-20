# Copyright (c) 2026, Murugan and contributors
"""Phase 22 — release/upgrade governance and GA checklists."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

GA_ROLLOUT_CHECKLIST = [
	{"id": "backup_verified", "title": "Backup verification passed"},
	{"id": "staging_smoke", "title": "Staging smoke tests passed"},
	{"id": "min_version_set", "title": "Min app version configured"},
	{"id": "rollback_plan", "title": "Rollback plan documented"},
	{"id": "ops_console", "title": "Ops dashboards reviewed"},
	{"id": "support_sla", "title": "Support SLA owners assigned"},
	{"id": "customer_signoff", "title": "Customer go-live signoff"},
]

GO_LIVE_CHECKLIST = [
	{"id": "onboarding_complete", "title": "Onboarding wizard complete"},
	{"id": "roles_applied", "title": "Role templates applied"},
	{"id": "demo_or_prod_data", "title": "Production data loaded or verified"},
	{"id": "field_training", "title": "Field officer training complete"},
	{"id": "apk_distributed", "title": "APK distributed to devices"},
	{"id": "sla_baseline", "title": "SLA baseline captured"},
]

ROLLBACK_CHECKLIST = [
	{"id": "stop_rollout", "title": "Stop new APK rollout"},
	{"id": "restore_backup", "title": "Restore last verified backup if needed"},
	{"id": "revert_min_version", "title": "Revert min app version config"},
	{"id": "notify_customers", "title": "Notify affected customers"},
	{"id": "incident_postmortem", "title": "Open incident postmortem"},
]


def production_rollout_checklist() -> dict:
	return {"items": GA_ROLLOUT_CHECKLIST, "rollback": ROLLBACK_CHECKLIST}


def go_live_checklist() -> dict:
	return {"items": GO_LIVE_CHECKLIST}


def request_upgrade_approval(release_version: str, min_app_version: str, wave: str = "ga") -> dict:
	if not frappe.db.exists("DocType", "GA Release Signoff"):
		return {"ok": False, "error": "GA Release Signoff missing"}
	existing = frappe.db.get_value(
		"GA Release Signoff",
		{"release_version": release_version, "status": ("in", ("draft", "pending_approval", "approved"))},
		"name",
	)
	if existing:
		return {"ok": True, "signoff_id": existing, "status": frappe.db.get_value("GA Release Signoff", existing, "status")}
	doc = frappe.get_doc(
		{
			"doctype": "GA Release Signoff",
			"release_version": release_version,
			"status": "pending_approval",
			"min_app_version": min_app_version,
			"rollout_wave": wave,
			"checklist_json": {"items": list(GA_ROLLOUT_CHECKLIST), "completed_ids": []},
		}
	)
	doc.insert(ignore_permissions=True)
	return {"ok": True, "signoff_id": doc.name, "status": doc.status}


def approve_release_signoff(signoff_id: str, approve: bool = True) -> dict:
	doc = frappe.get_doc("GA Release Signoff", signoff_id)
	if approve:
		doc.status = "approved"
		doc.signed_by = frappe.session.user
		doc.signed_on = now_datetime()
	else:
		doc.status = "draft"
	doc.save(ignore_permissions=True)
	return {"ok": True, "signoff_id": doc.name, "status": doc.status}


def record_release_deployed(signoff_id: str) -> dict:
	frappe.db.set_value("GA Release Signoff", signoff_id, "status", "released")
	if frappe.db.get_value("GA Release Signoff", signoff_id, "min_app_version"):
		min_v = frappe.db.get_value("GA Release Signoff", signoff_id, "min_app_version")
		frappe.conf.agriflow_min_app_version = min_v
	return {"ok": True, "signoff_id": signoff_id, "status": "released"}


def record_rollback(signoff_id: str, notes: str = "") -> dict:
	frappe.db.set_value(
		"GA Release Signoff",
		signoff_id,
		{"status": "rolled_back", "rollback_notes": notes},
	)
	return {"ok": True, "signoff_id": signoff_id, "rollback_checklist": ROLLBACK_CHECKLIST}
