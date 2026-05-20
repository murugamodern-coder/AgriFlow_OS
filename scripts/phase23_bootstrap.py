# Copyright (c) 2026, Murugan and contributors
"""Phase 23 — tenant bootstrap & enterprise onboarding packs."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.project_lifecycle.install import phase20_customer_onboarding as onboarding_mod

ENVIRONMENT_TEMPLATES = {
	"pilot": {
		"segment": "pilot",
		"sla_tier": "standard",
		"min_app_version": "0.23.0",
		"rollout_wave": "pilot_enterprise",
	},
	"ga": {
		"segment": "ga",
		"sla_tier": "standard",
		"min_app_version": "0.23.0",
		"rollout_wave": "ga_enterprise",
	},
	"enterprise": {
		"segment": "enterprise",
		"sla_tier": "enterprise",
		"min_app_version": "0.23.0",
		"rollout_wave": "enterprise",
	},
}


def register_tenant(
	*,
	tenant_key: str,
	customer_name: str,
	site_name: str | None = None,
	segment: str = "ga",
	sla_tier: str = "standard",
	onboarding_id: str | None = None,
) -> dict:
	if not frappe.db.exists("DocType", "Tenant Ops Record"):
		return {"ok": False, "error": "Tenant Ops Record missing"}
	site_name = site_name or frappe.local.site
	if frappe.db.exists("Tenant Ops Record", {"tenant_key": tenant_key}):
		name = frappe.db.get_value("Tenant Ops Record", {"tenant_key": tenant_key}, "name")
		return {"ok": True, "tenant_id": name, "existing": True}
	doc = frappe.get_doc(
		{
			"doctype": "Tenant Ops Record",
			"tenant_key": tenant_key,
			"customer_name": customer_name,
			"site_name": site_name,
			"segment": segment,
			"status": "provisioning",
			"sla_tier": sla_tier,
			"onboarding_link": onboarding_id,
			"last_audit_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	return {"ok": True, "tenant_id": doc.name, "existing": False}


def enterprise_onboarding_pack(template: str = "enterprise", customer_name: str = "") -> dict:
	"""Bootstrap tenant + onboarding wizard in one pack."""
	tpl = ENVIRONMENT_TEMPLATES.get(template) or ENVIRONMENT_TEMPLATES["ga"]
	name = customer_name or f"Enterprise {template} customer"
	key = name.lower().replace(" ", "_")[:40]
	onboard = onboarding_mod.start_onboarding(
		{"customer_name": name, "role_template": "multi_block" if template == "enterprise" else "pilot_block"}
	)
	oid = (onboard.get("data") or {}).get("onboarding_id") if onboard.get("ok") else None
	reg = register_tenant(
		tenant_key=key,
		customer_name=name,
		segment=tpl["segment"],
		sla_tier=tpl["sla_tier"],
		onboarding_id=oid,
	)
	frappe.db.set_value("Tenant Ops Record", reg["tenant_id"], "status", "active")
	return {
		"template": template,
		"onboarding": onboard,
		"tenant": reg,
		"config": tpl,
	}


def environment_template(name: str = "ga") -> dict:
	return {"name": name, **(ENVIRONMENT_TEMPLATES.get(name) or ENVIRONMENT_TEMPLATES["ga"])}


def execute():
	frappe.set_user("Administrator")
	return enterprise_onboarding_pack("enterprise", "Phase 23 Bootstrap Tenant")
