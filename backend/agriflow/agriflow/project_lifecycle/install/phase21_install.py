# Copyright (c) 2026, Murugan and contributors
"""Phase 21 install — ensures Phase 20 commercial artifacts exist."""

from __future__ import annotations

import frappe


def execute():
	checks = []
	for dt in ("Customer Onboarding", "Support Ticket", "Pilot Device Telemetry"):
		checks.append(f"{'exists' if frappe.db.exists('DocType', dt) else 'missing'}:{dt}")
	ok = all(c.startswith("exists") for c in checks)
	return {"ok": ok, "doctypes": checks}
