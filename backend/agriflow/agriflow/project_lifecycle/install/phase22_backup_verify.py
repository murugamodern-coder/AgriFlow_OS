# Copyright (c) 2026, Murugan and contributors
"""Phase 22 — backup verification automation (extends Phase 19 drill)."""

from __future__ import annotations

from pathlib import Path

import frappe


def verify_backup_readiness() -> dict:
	"""Pre-backup / restore-readiness checks without running bench backup."""
	site = frappe.local.site
	site_path = Path(frappe.get_site_path())
	private_files = site_path / "private" / "files"
	public_files = site_path / "public" / "files"
	checks = {
		"database_connected": bool(frappe.conf.db_name),
		"sync_session_table": bool(
			frappe.db.sql("SHOW TABLES LIKE 'tabSync Session'", as_list=True)
		),
		"private_files_dir": private_files.is_dir(),
		"public_files_dir": public_files.is_dir(),
	}
	row_counts = {
		"sync_sessions": frappe.db.count("Sync Session"),
		"telemetry": frappe.db.count("Pilot Device Telemetry")
		if frappe.db.exists("DocType", "Pilot Device Telemetry")
		else 0,
		"onboardings": frappe.db.count("Customer Onboarding")
		if frappe.db.exists("DocType", "Customer Onboarding")
		else 0,
	}
	ok = all(checks.values())
	return {
		"ok": ok,
		"site": site,
		"checks": checks,
		"row_counts": row_counts,
		"backup_command": f"bench --site {site} backup --with-files",
		"restore_command": f"bench --site {site} restore <backup-path>",
		"verification_note": "Run backup on staging weekly; restore drill quarterly",
	}


def execute():
	return verify_backup_readiness()
