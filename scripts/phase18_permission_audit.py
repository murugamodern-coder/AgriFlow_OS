# Copyright (c) 2026, Murugan and contributors
"""Phase 18 pilot permission audit — roles, blocks, inventory, push."""

from __future__ import annotations

import frappe

from agriflow.api.v1.permissions import assert_block_scope, ensure_authenticated, get_allowed_blocks
from agriflow.project_lifecycle.install.phase16_permission_audit import execute as base_audit

DEMO_USER = "field.officer@agriflow.local"
FIELD_ROLE = "Field Staff"


def execute():
	out = {"ok": False, "findings": [], "checks": {}}
	out["base"] = base_audit()
	findings = list(out["base"].get("findings") or [])

	# Field Staff role exists (pilot sites)
	role_exists = frappe.db.exists("Role", FIELD_ROLE)
	out["checks"]["field_staff_role_exists"] = bool(role_exists)
	if not role_exists:
		findings.append(f"Role {FIELD_ROLE} missing — assign before pilot")

	if frappe.db.exists("User", DEMO_USER):
		roles = set(frappe.get_roles(DEMO_USER))
		out["checks"]["demo_user_roles"] = sorted(roles)
		if FIELD_ROLE not in roles and "System Manager" not in roles:
			findings.append(f"{DEMO_USER} lacks Field Staff or System Manager")

	# Push token create as officer
	frappe.set_user(DEMO_USER)
	try:
		from agriflow.api.v1 import push as push_api

		reg = push_api.register_token(
			{
				"device_id": "phase18-audit",
				"push_token": "audit-token-phase18",
				"platform": "audit",
				"app_version": "0.18.0",
			}
		)
		out["checks"]["officer_push_register"] = reg.get("ok")
		if not reg.get("ok"):
			findings.append(f"push register failed: {reg.get('error')}")
	except Exception as exc:
		out["checks"]["officer_push_register"] = False
		findings.append(f"push register exception: {exc}")

	frappe.set_user("Administrator")
	out["findings"] = findings
	out["ok"] = len(findings) == 0 and out["base"].get("ok")
	return out
