# Copyright (c) 2026, Murugan and contributors
"""Phase 23 multi-tenant enterprise simulation."""

from __future__ import annotations

import frappe

from agriflow.api.v1 import enterprise as ent_api


def execute():
	frappe.set_user("Administrator")
	out = {"ok": True, "tenants": []}

	for tpl, name in (
		("pilot", "Ent Sim Pilot Co"),
		("ga", "Ent Sim GA Co"),
		("enterprise", "Ent Sim Enterprise Co"),
	):
		pack = ent_api.enterprise_onboarding_pack_api(
			{"template": tpl, "customer_name": name}
		)
		out["tenants"].append({"template": tpl, "pack_ok": pack.get("ok")})

	out["dashboard_ok"] = ent_api.enterprise_operations_dashboard().get("ok")
	out["sla_ok"] = ent_api.tenant_sla_dashboard_api().get("ok")
	out["automation_ok"] = ent_api.run_enterprise_automation().get("ok")
	out["retention_dry"] = ent_api.run_retention_policy(dry_run=1).get("ok")
	out["audit_ok"] = ent_api.export_enterprise_audit(format="json").get("ok")
	return out
