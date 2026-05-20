# Copyright (c) 2026, Murugan and contributors
"""Backup drill validation — site config + DB connectivity check."""

from __future__ import annotations

import frappe


def execute():
	site = frappe.local.site
	db_name = frappe.conf.db_name
	tables = frappe.db.sql("SHOW TABLES LIKE 'tabSync Session'", as_list=True)
	sync_sessions = frappe.db.count("Sync Session") if tables else 0
	telemetry = (
		frappe.db.count("Pilot Device Telemetry")
		if frappe.db.exists("DocType", "Pilot Device Telemetry")
		else 0
	)
	return {
		"ok": bool(db_name and tables),
		"site": site,
		"database": db_name,
		"sync_session_table": bool(tables),
		"sync_sessions": sync_sessions,
		"telemetry_rows": telemetry,
		"backup_command": f"bench --site {site} backup --with-files",
		"restore_note": "Use bench restore after staging backup drill",
	}
