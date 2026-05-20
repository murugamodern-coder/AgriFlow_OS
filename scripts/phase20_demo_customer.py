# Copyright (c) 2026, Murugan and contributors
"""Commercial demo tenant — extends Phase 15 seed with onboarding metadata."""

from __future__ import annotations

import frappe

from agriflow.project_lifecycle.install.phase15_seed_demo import execute as seed15
from agriflow.project_lifecycle.install.phase20_customer_onboarding import bootstrap_site_config


def execute():
	frappe.only_for("Administrator")
	bootstrap = bootstrap_site_config()
	seed = seed15()
	# Second demo officer for multi-device pilot demos
	_user_demo2()
	frappe.db.commit()
	return {
		"ok": True,
		"bootstrap": bootstrap,
		"seed": seed,
		"demo_users": [
			{"email": seed.get("demo_user"), "password": seed.get("demo_password")},
			{"email": "pilot.officer2@agriflow.local", "password": "AgriFlow@2026"},
		],
	}


def _user_demo2():
	email = "pilot.officer2@agriflow.local"
	if frappe.db.exists("User", email):
		return
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": "Pilot",
			"last_name": "Officer Two",
			"send_welcome_email": 0,
			"roles": [{"role": "System Manager"}],
		}
	)
	user.insert(ignore_permissions=True)
	user.new_password = "AgriFlow@2026"
	user.save(ignore_permissions=True)
