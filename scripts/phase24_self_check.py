# Copyright (c) 2026, Murugan and contributors
"""Phase 24 — operational self-check & scheduler watchdog."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.project_lifecycle.install.phase22_backup_verify import verify_backup_readiness
from agriflow.project_lifecycle.install.phase24_cache_tuning import cache_tuning_summary
from agriflow.project_lifecycle.install.phase24_indexes import ensure_performance_indexes
from agriflow.project_lifecycle.install.phase24_perf_analytics import dashboard_latency_probe


def operational_self_check() -> dict:
	checks = []
	latency = dashboard_latency_probe()
	slow_sla = latency.get("sla_summary_ms", 0) > 2000
	checks.append({"id": "dashboard_sla_latency", "ok": not slow_sla, "ms": latency.get("sla_summary_ms")})
	backup = verify_backup_readiness()
	checks.append({"id": "backup_readiness", "ok": backup.get("ok", False)})
	errors = frappe.db.count("Error Log", {"creation": (">=", frappe.utils.add_days(now_datetime(), -1))})
	checks.append({"id": "errors_24h", "ok": errors < 50, "count": errors})
	indexes = ensure_performance_indexes()
	checks.append({"id": "indexes", "ok": any("created" in i or "exists" in i for i in indexes), "detail": indexes[:3]})
	return {
		"ok": all(c["ok"] for c in checks),
		"checked_at": str(now_datetime()),
		"checks": checks,
		"latency_ms": latency,
		"cache": cache_tuning_summary(),
	}


def execute():
	frappe.set_user("Administrator")
	return operational_self_check()
