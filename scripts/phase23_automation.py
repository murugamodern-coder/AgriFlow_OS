# Copyright (c) 2026, Murugan and contributors
"""Phase 23 — enterprise operational automation & remediation."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.project_lifecycle.install.phase19_ops_alerts import execute as ops_alerts
from agriflow.project_lifecycle.install.phase22_backup_verify import verify_backup_readiness
from agriflow.project_lifecycle.install.phase22_ga_escalations import (
	auto_escalate_sla_breaches,
	auto_escalate_stale_devices,
	run_anomaly_escalations,
)
from agriflow.project_lifecycle.install.phase23_enterprise_analytics import (
	scheduler_health_summary,
	tenant_health_scores,
)


def remediate_stale_devices(max_devices: int = 10) -> dict:
	"""Auto-acknowledge follow-up + log for ops (non-destructive)."""
	from agriflow.project_lifecycle.install.phase21_analytics import stale_device_followups

	remediated = []
	for d in stale_device_followups()[:max_devices]:
		did = d.get("device_id")
		if not did or d.get("follow_up_status") == "acknowledged":
			continue
		frappe.cache().set_value(f"agriflow_stale_ack:{did}", "auto_remediated")
		if frappe.db.exists("DocType", "Operational Log"):
			frappe.get_doc(
				{
					"doctype": "Operational Log",
					"event_type": "stale_device_remediation",
					"source": "enterprise_automation",
					"device_id": did,
					"payload_json": {"action": "auto_ack", "health": d.get("health_score")},
					"recorded_on": now_datetime(),
				}
			).insert(ignore_permissions=True)
		remediated.append(did)
	return {"remediated": remediated, "count": len(remediated)}


def run_inventory_reconcile_automation() -> dict:
	try:
		from agriflow.project_lifecycle.install.phase16_inventory_reconcile import (
			execute as inv_reconcile,
		)

		return {"ok": True, "result": inv_reconcile()}
	except Exception as exc:
		return {"ok": False, "error": str(exc)[:200]}


def run_operational_audit() -> dict:
	"""Snapshot audit for compliance export."""
	health = tenant_health_scores()
	backup = verify_backup_readiness()
	return {
		"audited_on": str(now_datetime()),
		"site": frappe.local.site,
		"tenant_count": len(health),
		"tenants_below_60": sum(1 for t in health if (t.get("health_score") or 0) < 60),
		"backup": backup,
		"scheduler": scheduler_health_summary(),
	}


def execute():
	"""Daily enterprise automation (scheduler entry)."""
	frappe.set_user("Administrator")
	return {
		"sla_escalations": auto_escalate_sla_breaches(),
		"stale_escalations": auto_escalate_stale_devices(),
		"anomalies": run_anomaly_escalations(),
		"stale_remediation": remediate_stale_devices(),
		"ops_alerts": ops_alerts(),
		"inventory": run_inventory_reconcile_automation(),
		"audit": run_operational_audit(),
	}
