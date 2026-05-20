# Copyright (c) 2026, Murugan and contributors
"""Phase 22 — GA scale analytics (health, anomalies, support workload)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime, time_diff_in_hours

from agriflow.project_lifecycle.install.phase20_analytics import (
	push_success_rate,
	sla_summary,
	sync_trend_days,
)
from agriflow.project_lifecycle.install.phase21_analytics import (
	deployment_readiness_score,
	multi_customer_onboarding_status,
	stale_device_followups,
	support_response_metrics,
)


def _cache_get(key: str, ttl_sec: int, builder):
	val = frappe.cache().get_value(key)
	if val is not None:
		return val
	val = builder()
	frappe.cache().set_value(key, val, expires_in_sec=ttl_sec)
	return val


def customer_health_scores() -> list[dict]:
	"""Per-customer health from onboarding progress + site readiness proxy."""
	customers = multi_customer_onboarding_status(limit=100)
	readiness = deployment_readiness_score()
	base = readiness.get("score") or 70
	out = []
	for c in customers:
		score = base
		if c.get("status") == "live":
			score = min(100, score + 10)
		elif c.get("status") == "ready":
			score = min(100, score + 5)
		progress = c.get("progress_pct") or 0
		score = round(min(100, max(0, (score * 0.6) + (progress * 0.4))), 1)
		band = "green" if score >= 80 else "amber" if score >= 60 else "red"
		out.append({**c, "health_score": score, "health_band": band})
	return sorted(out, key=lambda x: x["health_score"])


def cross_customer_sla() -> dict:
	"""Aggregate SLA across current site (multi-site = one bench site per customer)."""
	return _cache_get("agriflow_ga_cross_sla", 120, lambda: {
		"site": frappe.local.site,
		"sla": sla_summary(),
		"sync_trends_14d": sync_trend_days(14),
		"push_7d": push_success_rate(7),
		"customer_count": len(multi_customer_onboarding_status()),
	})


def queue_anomaly_detection() -> dict:
	from agriflow.api.v1.pilot_ops import _queue_backlog_metrics

	backlog = _queue_backlog_metrics()
	pending = backlog.get("total_pending") or 0
	conflicts = backlog.get("total_conflicts") or 0
	anomaly = pending > 15 or conflicts > 3
	return {
		"anomaly": anomaly,
		"severity": "high" if pending > 25 else "medium" if anomaly else "low",
		"pending": pending,
		"conflicts": conflicts,
		"devices": backlog.get("devices") or [],
	}


def push_anomaly_detection() -> dict:
	push = push_success_rate(7)
	rate = push.get("success_rate") or 1.0
	anomaly = rate < 0.9
	return {
		"anomaly": anomaly,
		"success_rate": rate,
		"sent": push.get("sent"),
		"failed": push.get("failed"),
		"severity": "high" if rate < 0.8 else "medium" if anomaly else "low",
	}


def support_workload_dashboard() -> dict:
	metrics = support_response_metrics(14)
	by_assignee = []
	if frappe.db.exists("DocType", "Support Ticket"):
		try:
			by_assignee = frappe.db.sql(
				"""
				SELECT assigned_to AS user, COUNT(*) AS open_count
				FROM `tabSupport Ticket`
				WHERE status IN ('open', 'escalated')
				GROUP BY assigned_to
				""",
				as_dict=True,
			)
		except Exception:
			by_assignee = []
	return {**metrics, "by_assignee": by_assignee}


def onboarding_completion_metrics() -> dict:
	customers = multi_customer_onboarding_status(limit=200)
	if not customers:
		return {"total": 0, "avg_progress_pct": 0, "live": 0, "ready": 0, "in_progress": 0}
	live = sum(1 for c in customers if c.get("status") == "live")
	ready = sum(1 for c in customers if c.get("status") == "ready")
	in_prog = sum(1 for c in customers if c.get("status") == "in_progress")
	avg = round(sum(c.get("progress_pct") or 0 for c in customers) / len(customers), 1)
	return {
		"total": len(customers),
		"avg_progress_pct": avg,
		"live": live,
		"ready": ready,
		"in_progress": in_prog,
	}


def pilot_to_production_conversion() -> dict:
	"""Track onboarding status funnel pilot → ready → live."""
	customers = multi_customer_onboarding_status(limit=200)
	return {
		"total_onboardings": len(customers),
		"ready_for_ga": sum(1 for c in customers if c.get("status") == "ready"),
		"live_production": sum(1 for c in customers if c.get("status") == "live"),
		"conversion_rate": round(
			sum(1 for c in customers if c.get("status") == "live") / max(1, len(customers)),
			3,
		),
	}


def customer_readiness_score(onboarding_id: str | None = None) -> dict:
	"""GA customer-readiness: onboarding + deployment readiness composite."""
	readiness = deployment_readiness_score()
	if onboarding_id and frappe.db.exists("Customer Onboarding", onboarding_id):
		doc = frappe.get_doc("Customer Onboarding", onboarding_id)
		from agriflow.project_lifecycle.install.phase20_customer_onboarding import _steps_unwrap

		steps = _steps_unwrap(doc.steps_json)
		done = sum(1 for s in steps if s.get("completed"))
		total = len(steps) or 1
		onboard_pct = 100 * done / total
		score = round((readiness["score"] * 0.5) + (onboard_pct * 0.5), 1)
		return {
			"onboarding_id": onboarding_id,
			"customer_name": doc.customer_name,
			"score": score,
			"band": "green" if score >= 80 else "amber" if score >= 60 else "red",
			"onboarding_pct": round(onboard_pct, 1),
			"deployment_score": readiness["score"],
			"go_live_ready": score >= 80 and doc.status in ("ready", "live"),
		}
	health = customer_health_scores()
	avg = round(sum(h["health_score"] for h in health) / len(health), 1) if health else readiness["score"]
	return {
		"aggregate_score": avg,
		"deployment": readiness,
		"customers": health[:25],
		"onboarding_metrics": onboarding_completion_metrics(),
	}
