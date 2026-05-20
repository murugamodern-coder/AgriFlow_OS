# Copyright (c) 2026, Murugan and contributors
"""Phase 21 — pilot operations analytics (readiness, support, follow-ups)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime, time_diff_in_hours

from agriflow.project_lifecycle.install.phase20_analytics import (
	device_health_scores,
	push_success_rate,
	sla_summary,
)
from agriflow.project_lifecycle.install.phase20_customer_onboarding import _steps_unwrap


def multi_customer_onboarding_status(limit: int = 50) -> list[dict]:
	"""Track all pilot customers in onboarding pipeline."""
	if not frappe.db.exists("DocType", "Customer Onboarding"):
		return []
	rows = frappe.get_all(
		"Customer Onboarding",
		fields=[
			"name",
			"customer_name",
			"site_name",
			"status",
			"current_step",
			"role_template",
			"steps_json",
			"started_on",
			"completed_on",
		],
		order_by="modified desc",
		limit=limit,
	)
	out = []
	for r in rows:
		steps = _steps_unwrap(r.steps_json)
		done = sum(1 for s in steps if s.get("completed"))
		total = len(steps) or 1
		out.append(
			{
				"onboarding_id": r.name,
				"customer_name": r.customer_name,
				"site_name": r.site_name,
				"status": r.status,
				"current_step": r.current_step,
				"role_template": r.role_template,
				"progress_pct": round(100 * done / total, 1),
				"steps_completed": done,
				"steps_total": total,
				"started_on": str(r.started_on) if r.started_on else None,
				"completed_on": str(r.completed_on) if r.completed_on else None,
			}
		)
	return out


def deployment_readiness_score() -> dict:
	"""0–100 score for go-live readiness (pilot ops)."""
	sla = sla_summary()
	push = push_success_rate(7)
	score = 100
	score -= max(0, int((1 - push.get("success_rate", 0)) * 40))
	score -= min(30, (sla.get("stale_devices") or 0) * 5)
	score -= min(20, (sla.get("sla_breach_days") or 0) * 5)
	open_incidents = (
		frappe.db.count(
			"Operational Incident",
			{"status": ("in", ("open", "investigating"))},
		)
		if frappe.db.exists("DocType", "Operational Incident")
		else 0
	)
	score -= min(25, open_incidents * 5)
	onboard_ready = frappe.db.count("Customer Onboarding", {"status": "ready"})
	onboard_live = frappe.db.count("Customer Onboarding", {"status": "live"})
	score = max(0, min(100, score))
	band = "green" if score >= 80 else "amber" if score >= 60 else "red"
	return {
		"score": score,
		"band": band,
		"push_success_rate": push.get("success_rate"),
		"open_incidents": open_incidents,
		"customers_ready": onboard_ready,
		"customers_live": onboard_live,
		"sla": sla,
	}


def support_response_metrics(days: int = 14) -> dict:
	"""Support ticket SLA-style metrics for pilot ops."""
	if not frappe.db.exists("DocType", "Support Ticket"):
		return {"ok": False, "reason": "no_support_ticket"}
	since = add_days(now_datetime(), -days)
	open_count = frappe.db.count("Support Ticket", {"status": ("in", ("open", "escalated"))})
	escalated = frappe.db.count("Support Ticket", {"status": "escalated"})
	resolved_recent = frappe.db.count(
		"Support Ticket",
		{"status": "resolved", "resolved_on": (">=", since)},
	)
	open_rows = frappe.get_all(
		"Support Ticket",
		filters={"status": ("in", ("open", "escalated"))},
		fields=["name", "opened_on", "priority"],
		limit=100,
	)
	ages = []
	for row in open_rows:
		if row.opened_on:
			ages.append(time_diff_in_hours(now_datetime(), row.opened_on))
	avg_age_h = round(sum(ages) / len(ages), 1) if ages else 0
	critical_open = sum(1 for r in open_rows if r.priority in ("high", "critical"))
	return {
		"open_tickets": open_count,
		"escalated": escalated,
		"resolved_last_days": resolved_recent,
		"avg_open_age_hours": avg_age_h,
		"critical_open": critical_open,
		"target_first_response_hours": 4,
		"target_resolution_hours": 48,
	}


def stale_device_followups(stale_hours: int = 48) -> list[dict]:
	"""Devices needing ops follow-up (stale heartbeat or low health)."""
	devices = device_health_scores(stale_hours=stale_hours)
	followups = []
	for d in devices:
		if d.get("stale") or (d.get("health_score") or 100) < 50:
			action = "call_officer" if d.get("stale") else "queue_review"
			followups.append(
				{
					**d,
					"suggested_action": action,
					"follow_up_status": frappe.cache().get_value(
						f"agriflow_stale_ack:{d.get('device_id')}"
					)
					or "pending",
				}
			)
	return followups


def rollout_status_summary() -> dict:
	"""APK / version adoption for rollout cadence."""
	from agriflow.api.v1.pilot_ops import _app_version_matrix

	min_ver = frappe.conf.get("agriflow_min_app_version") or "0.21.0"
	wave = frappe.conf.get("agriflow_rollout_wave") or "pilot_a"
	versions = _app_version_matrix()
	return {
		"rollout_wave": wave,
		"min_app_version": min_ver,
		"version_matrix": versions,
		"devices_below_min": sum(
			1
			for v in versions
			if (v.get("app_version") or "0") < min_ver
		),
	}
