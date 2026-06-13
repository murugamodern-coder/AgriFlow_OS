"""Audit tabSeries locks via bench execute (audit-only)."""
from __future__ import annotations

import json

import frappe


def run_audit() -> dict:
	out: dict = {}

	# 1. Processlist (site user can usually run this)
	out["processlist"] = frappe.db.sql("SHOW FULL PROCESSLIST", as_dict=True)

	# 2-4. InnoDB trx / lock waits (may need PROCESS privilege)
	for key, query in {
		"innodb_trx": """
			SELECT trx_id, trx_state, trx_started,
				TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_seconds,
				trx_mysql_thread_id, trx_query, trx_rows_locked,
				trx_rows_modified, trx_tables_locked
			FROM information_schema.innodb_trx
			ORDER BY trx_started
		""",
		"innodb_lock_waits": """
			SELECT r.trx_mysql_thread_id AS waiting_thread,
				r.trx_query AS waiting_query,
				b.trx_mysql_thread_id AS blocking_thread,
				b.trx_query AS blocking_query,
				TIMESTAMPDIFF(SECOND, b.trx_started, NOW()) AS blocking_age_seconds
			FROM information_schema.innodb_lock_waits w
			JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
			JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id
		""",
	}.items():
		try:
			out[key] = frappe.db.sql(query, as_dict=True)
		except Exception as exc:
			out[key] = {"error": str(exc)}

	# tabSeries FR rows
	out["tabseries_all"] = frappe.db.sql(
		"SELECT name, `current` FROM `tabSeries` ORDER BY name",
		as_dict=True,
	)

	# Farmer autoname from DocType
	out["farmer_autoname"] = frappe.db.get_value("DocType", "Farmer", "autoname")
	out["farmer_count"] = frappe.db.count("Farmer")
	out["last_farmers"] = frappe.get_all(
		"Farmer", fields=["name", "creation"], order_by="creation desc", limit=5
	)

	try:
		status = frappe.db.sql("SHOW ENGINE INNODB STATUS", as_dict=False)
		text = status[0][2] if status else ""
		for marker in ("LATEST DETECTED DEADLOCK", "---TRANSACTION", "LOCK WAIT"):
			idx = text.find(marker)
			if idx >= 0:
				out[f"innodb_status_{marker.strip('-').replace(' ', '_')[:24]}"] = text[
					idx : idx + 2000
				]
	except Exception as exc:
		out["innodb_status_error"] = str(exc)

	# Active non-sleep connections
	active = [
		p
		for p in out["processlist"]
		if p.get("Command") not in ("Sleep", None) or (p.get("Time") or 0) > 5
	]
	out["active_or_long_connections"] = active

	# tabSeries-related
	out["tabseries_queries"] = [
		p
		for p in out["processlist"]
		if p.get("Info") and ("tabSeries" in p["Info"] or "FOR UPDATE" in p["Info"])
	]

	# Sleep + long time (stale connection candidates)
	out["sleep_long"] = [
		p for p in out["processlist"] if p.get("Command") == "Sleep" and (p.get("Time") or 0) > 30
	]

	print(json.dumps(out, indent=2, default=str))
	return out
