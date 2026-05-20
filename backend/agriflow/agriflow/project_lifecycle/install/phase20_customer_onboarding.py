# Copyright (c) 2026, Murugan and contributors
"""Customer onboarding wizard + site bootstrap automation."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.response import fail, parse_data, success

ONBOARDING_STEPS = [
	{"id": "site_config", "title": "Configure site JWT and secrets"},
	{"id": "roles", "title": "Apply role template"},
	{"id": "demo_seed", "title": "Load demo dataset"},
	{"id": "verify", "title": "Run commercial verify script"},
	{"id": "pilot_users", "title": "Create pilot officer accounts"},
	{"id": "mobile_apk", "title": "Distribute mobile APK"},
	{"id": "ops_training", "title": "Ops dashboard training"},
]


def _wizard_template(role_template: str) -> list[dict]:
	return [{**s, "completed": False} for s in ONBOARDING_STEPS]


def _steps_wrap(steps: list[dict]) -> dict:
	"""Frappe JSON fields accept objects only, not bare lists."""
	return {"items": steps}


def _steps_unwrap(raw) -> list[dict]:
	if isinstance(raw, dict):
		return raw.get("items") or []
	if isinstance(raw, list):
		return raw
	return []


@frappe.whitelist(allow_guest=False)
def start_onboarding(data=None):
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	if not frappe.db.exists("DocType", "Customer Onboarding"):
		return fail("VAL_INVALID", "Run phase20_install first")
	payload = parse_data(data)
	name = (payload.get("customer_name") or "").strip()
	if not name:
		return fail("VAL_INVALID", "customer_name required")
	steps = _wizard_template(payload.get("role_template") or "pilot_block")
	doc = frappe.get_doc(
		{
			"doctype": "Customer Onboarding",
			"customer_name": name,
			"site_name": payload.get("site_name") or frappe.local.site,
			"status": "in_progress",
			"current_step": ONBOARDING_STEPS[0]["id"],
			"role_template": payload.get("role_template") or "pilot_block",
			"started_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	doc.steps_json = _steps_wrap(steps)
	doc.save(ignore_permissions=True)
	return success({"onboarding_id": doc.name, "steps": steps})


@frappe.whitelist(allow_guest=False)
def complete_step(data=None):
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	payload = parse_data(data)
	oid = payload.get("onboarding_id")
	step_id = payload.get("step_id")
	doc = frappe.get_doc("Customer Onboarding", oid)
	steps = _steps_unwrap(doc.steps_json)
	for s in steps:
		if s.get("id") == step_id:
			s["completed"] = True
	done = sum(1 for s in steps if s.get("completed"))
	doc.steps_json = _steps_wrap(steps)
	doc.current_step = step_id
	if done >= len(steps):
		doc.status = "ready"
		doc.completed_on = now_datetime()
	doc.save(ignore_permissions=True)
	return success(
		{"onboarding_id": doc.name, "status": doc.status, "completed": done, "total": len(steps)}
	)


@frappe.whitelist(allow_guest=False)
def onboarding_checklist_admin():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	return success(
		{
			"steps": ONBOARDING_STEPS,
			"role_templates": [
				{"id": "pilot_block", "roles": ["Field Staff", "Store Keeper"]},
				{"id": "multi_block", "roles": ["Field Staff", "Block Admin", "Store Keeper"]},
				{"id": "demo", "roles": ["System Manager", "Field Staff"]},
			],
			"readiness_commands": [
				"bench --site <site> set-config agriflow_auth_mode jwt",
				"bench --site <site> execute agriflow.project_lifecycle.install.phase20_demo_customer.execute",
				"bench --site <site> execute agriflow.project_lifecycle.install.phase20_verify_commercial.execute",
			],
		}
	)


def bootstrap_site_config(site: str | None = None) -> dict:
	"""Apply standard commercial site config (current site if omitted)."""
	site = site or frappe.local.site
	frappe.conf.agriflow_auth_mode = "jwt"
	# JWT secret should be set via: bench --site <site> set-config agriflow_jwt_secret <hex>
	results = {
		"site": site,
		"jwt_mode": "jwt",
		"rollout_wave": frappe.conf.get("agriflow_rollout_wave") or "pilot_a",
		"min_app_version": frappe.conf.get("agriflow_min_app_version") or "0.20.0",
	}
	return results


def execute():
	"""bench execute — bootstrap current site for commercial demo."""
	frappe.only_for("Administrator")
	return bootstrap_site_config()
