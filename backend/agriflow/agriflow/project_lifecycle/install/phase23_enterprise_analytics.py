# Copyright (c) 2026, Murugan and contributors
"""Phase 23 — enterprise tenant analytics (optimized, cached)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, now_datetime

from agriflow.project_lifecycle.install.phase20_analytics import push_success_rate, sla_summary
from agriflow.project_lifecycle.install.phase22_ga_analytics import (
	customer_health_scores,
	customer_readiness_score,
	queue_anomaly_detection,
	push_anomaly_detection,
)


def _cache_get(key: str, ttl_sec: int, builder):
	val = frappe.cache().get_value(key)
	if val is not None:
		return val
	val = builder()
	frappe.cache().set_value(key, val, expires_in_sec=ttl_sec)
	return val


def list_tenant_ops_records(limit: int = 100) -> list[dict]:
	if not frappe.db.exists("DocType", "Tenant Ops Record"):
		return []
	return frappe.get_all(
		"Tenant Ops Record",
		fields=[
			"name",
			"tenant_key",
			"customer_name",
			"site_name",
			"segment",
			"status",
			"sla_tier",
			"health_score",
			"onboarding_link",
			"last_audit_on",
		],
		order_by="modified desc",
		limit=limit,
	)


def tenant_health_scores() -> list[dict]:
	"""Tenant-level health — registry row + onboarding-derived score."""
	registry = {r.tenant_key: r for r in list_tenant_ops_records(200)}
	health = customer_health_scores()
	out = []
	seen = set()
	for h in health:
		key = (h.get("site_name") or h.get("customer_name") or "").lower().replace(" ", "_")
		reg = registry.get(key)
		score = h.get("health_score") or 0
		if reg and reg.health_score:
			score = round((score + float(reg.health_score)) / 2, 1)
		segment = reg.segment if reg else ("enterprise" if h.get("status") == "live" else "ga")
		out.append(
			{
				"tenant_key": key,
				"tenant_id": reg.name if reg else None,
				"customer_name": h.get("customer_name"),
				"site_name": h.get("site_name"),
				"segment": segment,
				"status": reg.status if reg else h.get("status"),
				"sla_tier": reg.sla_tier if reg else "standard",
				"health_score": score,
				"health_band": h.get("health_band"),
				"progress_pct": h.get("progress_pct"),
			}
		)
		seen.add(key)
	for key, reg in registry.items():
		if key in seen:
			continue
		out.append(
			{
				"tenant_key": key,
				"tenant_id": reg.name,
				"customer_name": reg.customer_name,
				"site_name": reg.site_name,
				"segment": reg.segment,
				"status": reg.status,
				"sla_tier": reg.sla_tier,
				"health_score": reg.health_score or 0,
				"health_band": "amber",
				"progress_pct": 0,
			}
		)
	return sorted(out, key=lambda x: x["health_score"])


def tenant_sla_dashboard(tenant_key: str | None = None) -> dict:
	"""Per-tenant or site-wide SLA (cached 180s)."""
	cache_key = f"agriflow_tenant_sla:{frappe.local.site}:{tenant_key or 'all'}"
	return _cache_get(
		cache_key,
		180,
		lambda: {
			"tenant_key": tenant_key,
			"site": frappe.local.site,
			"sla": sla_summary(),
			"push_7d": push_success_rate(7),
			"queue_anomaly": queue_anomaly_detection(),
			"push_anomaly": push_anomaly_detection(),
		},
	)


def tenant_readiness_summaries() -> list[dict]:
	tenants = tenant_health_scores()
	summaries = []
	for t in tenants[:50]:
		oid = None
		if t.get("tenant_id"):
			oid = frappe.db.get_value("Tenant Ops Record", t["tenant_id"], "onboarding_link")
		readiness = customer_readiness_score(onboarding_id=oid) if oid else customer_readiness_score()
		summaries.append(
			{
				**t,
				"readiness_score": readiness.get("score") or readiness.get("aggregate_score"),
				"go_live_ready": readiness.get("go_live_ready", False),
			}
		)
	return summaries


def customer_segment_report() -> dict:
	tenants = tenant_health_scores()
	segments = {"pilot": 0, "ga": 0, "enterprise": 0}
	statuses = {}
	for t in tenants:
		segments[t.get("segment") or "ga"] = segments.get(t.get("segment") or "ga", 0) + 1
		st = t.get("status") or "unknown"
		statuses[st] = statuses.get(st, 0) + 1
	return {
		"total_tenants": len(tenants),
		"by_segment": segments,
		"by_status": statuses,
		"avg_health": round(
			sum(t.get("health_score") or 0 for t in tenants) / max(1, len(tenants)),
			1,
		),
	}


def scheduler_health_summary() -> dict:
	"""Scheduler / background job health proxy."""
	errors_24h = frappe.db.count(
		"Error Log",
		{"creation": (">=", add_days(now_datetime(), -1))},
	)
	scheduled = []
	if frappe.db.exists("DocType", "Scheduled Job Type"):
		scheduled = frappe.get_all(
			"Scheduled Job Type",
			filters={"stopped": 0},
			fields=["method", "frequency"],
			limit=20,
		)
	return {
		"errors_last_24h": errors_24h,
		"scheduled_jobs_active": len(scheduled),
		"scheduled_jobs_sample": scheduled[:10],
		"recommended_hooks": [
			"phase23_automation.execute (daily)",
			"phase23_retention.execute (weekly)",
			"phase19_fcm_delivery.execute (hourly)",
		],
	}


def retry_analytics(days: int = 7) -> dict:
	since = add_days(now_datetime(), -days)
	if not frappe.db.exists("DocType", "Sync Mutation Log"):
		return {"days": days, "rows": []}
	rows = frappe.db.sql(
		"""
		SELECT status, COUNT(*) AS cnt
		FROM `tabSync Mutation Log`
		WHERE processed_on >= %(since)s
		GROUP BY status
		""",
		{"since": since},
		as_dict=True,
	)
	total = sum(r.cnt for r in rows)
	failed = sum(r.cnt for r in rows if r.status in ("failed", "conflict", "dependency_failed"))
	return {
		"window_days": days,
		"by_status": rows,
		"total": total,
		"failure_rate": round(failed / total, 4) if total else 0,
	}


def cross_tenant_governance() -> dict:
	return {
		"site": frappe.local.site,
		"tenant_count": len(list_tenant_ops_records()),
		"segment_report": customer_segment_report(),
		"sla": tenant_sla_dashboard(),
		"scheduler": scheduler_health_summary(),
	}
