# Copyright (c) 2026, Murugan and contributors
"""Phase 20 — operational analytics (trends, health, SLA)."""

from __future__ import annotations

from datetime import datetime

import frappe
from frappe.utils import add_days, now_datetime


def sync_trend_days(days: int = 14) -> list[dict]:
	since = add_days(now_datetime(), -days)
	return frappe.db.sql(
		"""
		SELECT DATE(processed_on) AS day,
			SUM(status = 'success') AS success_cnt,
			SUM(status = 'skipped') AS skipped_cnt,
			SUM(status IN ('failed','conflict','dependency_failed')) AS fail_cnt,
			COUNT(*) AS total
		FROM `tabSync Mutation Log`
		WHERE processed_on >= %(since)s
		GROUP BY DATE(processed_on)
		ORDER BY day
		""",
		{"since": since},
		as_dict=True,
	)


def queue_growth_trend(days: int = 14) -> list[dict]:
	"""Proxy queue trend from telemetry heartbeats."""
	since = add_days(now_datetime(), -days)
	return frappe.db.sql(
		"""
		SELECT DATE(reported_at) AS day,
			SUM(queue_pending) AS pending_sum,
			SUM(queue_conflict) AS conflict_sum,
			COUNT(DISTINCT device_id) AS devices
		FROM `tabPilot Device Telemetry`
		WHERE reported_at >= %(since)s
		GROUP BY DATE(reported_at)
		ORDER BY day
		""",
		{"since": since},
		as_dict=True,
	)


def push_success_rate(days: int = 7) -> dict:
	since = add_days(now_datetime(), -days)
	rows = frappe.db.sql(
		"""
		SELECT status, COUNT(*) AS cnt
		FROM `tabPush Delivery Log`
		WHERE recorded_on >= %(since)s
		GROUP BY status
		""",
		{"since": since},
		as_dict=True,
	)
	by_status = {r.status: r.cnt for r in rows}
	sent = by_status.get("sent", 0) + by_status.get("simulated_sent", 0)
	total = sum(by_status.values()) or 1
	return {
		"window_days": days,
		"by_status": by_status,
		"success_rate": round(sent / total, 4),
		"total": total,
	}


def inventory_utilization_summary() -> dict:
	"""Allocation-level utilization snapshot."""
	if not frappe.db.exists("DocType", "Inventory Allocation"):
		return {"ok": False, "reason": "no_inventory_module"}
	rows = frappe.db.sql(
		"""
		SELECT
			COUNT(*) AS allocations,
			SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active,
			SUM(CASE WHEN consumed_qty > 0 THEN 1 ELSE 0 END) AS with_consumption
		FROM `tabInventory Allocation`
		WHERE docstatus < 2
		""",
		as_dict=True,
	)
	row = rows[0] if rows else {}
	active = int(row.get("active") or 0)
	with_cons = int(row.get("with_consumption") or 0)
	return {
		"ok": True,
		"allocations": int(row.get("allocations") or 0),
		"active": active,
		"with_consumption": with_cons,
		"utilization_rate": round(with_cons / active, 4) if active else 0.0,
	}


def device_health_scores(stale_hours: int = 48) -> list[dict]:
	"""Score devices 0–100; flag stale if no heartbeat within stale_hours."""
	rows = frappe.db.sql(
		"""
		SELECT t1.device_id, t1.user, t1.app_version, t1.queue_pending, t1.queue_conflict,
			t1.queue_failed, t1.reported_at
		FROM `tabPilot Device Telemetry` t1
		INNER JOIN (
			SELECT device_id, MAX(reported_at) AS max_reported
			FROM `tabPilot Device Telemetry`
			GROUP BY device_id
		) t2 ON t1.device_id = t2.device_id AND t1.reported_at = t2.max_reported
		ORDER BY t1.reported_at DESC
		LIMIT 100
		""",
		as_dict=True,
	)
	now = now_datetime()
	out = []
	for r in rows:
		score = 100
		pending = int(r.queue_pending or 0)
		conflict = int(r.queue_conflict or 0)
		failed = int(r.queue_failed or 0)
		score -= min(30, pending * 5)
		score -= 15 if conflict else 0
		score -= 10 if failed else 0
		last = r.reported_at
		hours_ago = (now - last).total_seconds() / 3600 if last else 9999
		stale = hours_ago > stale_hours
		if stale:
			score -= 25
		score = max(0, min(100, score))
		out.append(
			{
				"device_id": r.device_id,
				"user": r.user,
				"app_version": r.app_version,
				"health_score": score,
				"stale": stale,
				"hours_since_report": round(hours_ago, 1),
				"queue_pending": pending,
				"queue_conflict": conflict,
			}
		)
	return sorted(out, key=lambda x: x["health_score"])


def officer_productivity(days: int = 7) -> list[dict]:
	since = add_days(now_datetime(), -days)
	sync_rows = frappe.db.sql(
		"""
		SELECT user, COUNT(*) AS sync_sessions
		FROM `tabSync Session`
		WHERE started_on >= %(since)s
		GROUP BY user
		""",
		{"since": since},
		as_dict=True,
	)
	feedback = frappe.db.sql(
		"""
		SELECT submitted_by AS user, COUNT(*) AS feedback_count
		FROM `tabPilot Operational Feedback`
		WHERE submitted_on >= %(since)s
		GROUP BY submitted_by
		""",
		{"since": since},
		as_dict=True,
	) if frappe.db.exists("DocType", "Pilot Operational Feedback") else []
	by_user: dict[str, dict] = {}
	for s in sync_rows:
		by_user[s.user] = {"user": s.user, "sync_sessions": s.sync_sessions, "feedback_count": 0}
	for f in feedback:
		u = f.user
		if u not in by_user:
			by_user[u] = {"user": u, "sync_sessions": 0, "feedback_count": 0}
		by_user[u]["feedback_count"] = f.feedback_count
	return sorted(by_user.values(), key=lambda x: -x["sync_sessions"])


def sla_summary() -> dict:
	"""SLA-style rollup for commercial dashboard."""
	sync = sync_trend_days(7)
	push = push_success_rate(7)
	health = device_health_scores()
	stale_count = sum(1 for d in health if d["stale"])
	avg_health = round(sum(d["health_score"] for d in health) / len(health), 1) if health else 0
	fail_days = [d for d in sync if d.total and (d.fail_cnt or 0) / d.total > 0.1]
	return {
		"sync_days_tracked": len(sync),
		"push_success_rate": push["success_rate"],
		"avg_device_health": avg_health,
		"stale_devices": stale_count,
		"devices_tracked": len(health),
		"sla_breach_days": len(fail_days),
		"target_push_success": 0.95,
		"target_avg_health": 70,
		"target_stale_devices": 0,
	}
