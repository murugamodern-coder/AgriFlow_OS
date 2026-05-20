# Copyright (c) 2026, Murugan and contributors
"""Phase 17 — pilot ops: telemetry, feedback, admin dashboard aggregates."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import add_days, get_datetime, now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.project_lifecycle.install.phase16_inventory_reconcile import execute as inventory_reconcile
def _ensure_pilot_doctypes():
	for dt in ("Pilot Device Telemetry", "Pilot Operational Feedback", "Operational Log"):
		if not frappe.db.exists("DocType", dt):
			frappe.throw(f"Missing DocType {dt}. Run phase17_install.execute first.", frappe.ValidationError)


def _record_log(
	event_type: str,
	*,
	source: str = "api",
	device_id: str | None = None,
	user: str | None = None,
	request_id: str | None = None,
	correlation_id: str | None = None,
	payload: dict | None = None,
) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Operational Log",
			"event_type": event_type,
			"source": source,
			"device_id": device_id or "",
			"user": user or frappe.session.user,
			"request_id": request_id or "",
			"correlation_id": correlation_id or "",
			"payload_json": payload or {},
			"recorded_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _admin_only():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication required", frappe.AuthenticationError)
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Pilot dashboard requires System Manager", frappe.PermissionError)


@frappe.whitelist(allow_guest=False)
def heartbeat(data: str | dict | None = None):
	"""Mobile device heartbeat — queue depth, version, last sync."""
	ensure_authenticated()
	_ensure_pilot_doctypes()
	payload = parse_data(data)
	device_id = (payload.get("device_id") or "").strip()
	if not device_id:
		return fail("VAL_INVALID", "device_id required")

	row = {
		"doctype": "Pilot Device Telemetry",
		"device_id": device_id,
		"user": frappe.session.user,
		"app_version": payload.get("app_version") or "",
		"build_number": str(payload.get("build_number") or ""),
		"platform": payload.get("platform") or "",
		"queue_pending": int(payload.get("queue_pending") or 0),
		"queue_conflict": int(payload.get("queue_conflict") or 0),
		"queue_failed": int(payload.get("queue_failed") or 0),
		"last_sync_at": payload.get("last_sync_at"),
		"last_correlation_id": payload.get("last_correlation_id") or "",
		"reported_at": now_datetime(),
		"diagnostics_json": payload.get("diagnostics") or {},
	}
	doc = frappe.get_doc(row)
	doc.insert(ignore_permissions=True)
	_record_log(
		"heartbeat",
		device_id=device_id,
		payload={"app_version": row["app_version"], "queue_pending": row["queue_pending"]},
	)
	return success({"telemetry_id": doc.name})


@frappe.whitelist(allow_guest=False)
def diagnostic_upload(data: str | dict | None = None):
	"""Crash / diagnostic bundle from mobile (no PII in payload by contract)."""
	ensure_authenticated()
	_ensure_pilot_doctypes()
	payload = parse_data(data)
	device_id = (payload.get("device_id") or "").strip()
	if not device_id:
		return fail("VAL_INVALID", "device_id required")

	diag = payload.get("diagnostics") or payload
	doc = frappe.get_doc(
		{
			"doctype": "Pilot Device Telemetry",
			"device_id": device_id,
			"user": frappe.session.user,
			"app_version": payload.get("app_version") or "",
			"build_number": str(payload.get("build_number") or ""),
			"platform": payload.get("platform") or "",
			"queue_pending": int(payload.get("queue_pending") or 0),
			"queue_conflict": int(payload.get("queue_conflict") or 0),
			"queue_failed": int(payload.get("queue_failed") or 0),
			"reported_at": now_datetime(),
			"diagnostics_json": diag,
		}
	)
	doc.insert(ignore_permissions=True)
	_record_log("diagnostic_upload", device_id=device_id, payload={"kind": payload.get("kind", "diagnostic")})
	return success({"telemetry_id": doc.name})


@frappe.whitelist(allow_guest=False)
def feedback_submit(data: str | dict | None = None):
	"""Structured pilot UX / ops feedback from field officers."""
	ensure_authenticated()
	_ensure_pilot_doctypes()
	payload = parse_data(data)
	body = (payload.get("body") or "").strip()
	if not body:
		return fail("VAL_INVALID", "body required")
	category = payload.get("category") or "other"
	if category not in ("sync", "ux", "inventory", "task", "network", "other"):
		category = "other"

	doc = frappe.get_doc(
		{
			"doctype": "Pilot Operational Feedback",
			"submitted_by": frappe.session.user,
			"device_id": payload.get("device_id") or "",
			"app_version": payload.get("app_version") or "",
			"category": category,
			"severity": payload.get("severity") or "medium",
			"body": body,
			"farmer_project": payload.get("farmer_project"),
			"workflow_status": "new",
			"submitted_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	_record_log("feedback_submit", device_id=payload.get("device_id"), payload={"category": category, "name": doc.name})
	return success({"feedback_id": doc.name})


def _sync_health_window(days: int = 7) -> dict[str, Any]:
	since = add_days(now_datetime(), -days)
	sessions = frappe.db.count("Sync Session", {"started_on": [">=", since]})
	completed = frappe.db.count("Sync Session", {"started_on": [">=", since], "completed_on": ["is", "set"]})
	by_status = frappe.db.sql(
		"""
		SELECT status, COUNT(*) AS cnt
		FROM `tabSync Mutation Log`
		WHERE processed_on >= %(since)s
		GROUP BY status
		""",
		{"since": since},
		as_dict=True,
	)
	failed = sum(r.cnt for r in by_status if r.status in ("failed", "conflict", "dependency_failed"))
	success = sum(r.cnt for r in by_status if r.status in ("success", "skipped"))
	total = failed + success
	return {
		"window_days": days,
		"sessions_opened": sessions,
		"sessions_completed": completed,
		"mutations_total": total,
		"mutations_by_status": {r.status: r.cnt for r in by_status},
		"failure_rate": round(failed / total, 4) if total else 0.0,
	}


def _queue_backlog_metrics() -> dict[str, Any]:
	"""Server-side proxy: recent failed/conflict mutations + device queue from telemetry."""
	since = add_days(now_datetime(), -1)
	rows = frappe.db.sql(
		"""
		SELECT device_id, user, queue_pending, queue_conflict, queue_failed, app_version, reported_at
		FROM `tabPilot Device Telemetry`
		WHERE reported_at >= %(since)s
		ORDER BY reported_at DESC
		""",
		{"since": since},
		as_dict=True,
	)
	latest_by_device: dict[str, dict] = {}
	for r in rows:
		if r.device_id not in latest_by_device:
			latest_by_device[r.device_id] = r
	devices = list(latest_by_device.values())
	return {
		"devices_reporting_24h": len(devices),
		"total_pending": sum(int(d.queue_pending or 0) for d in devices),
		"total_conflicts": sum(int(d.queue_conflict or 0) for d in devices),
		"total_failed": sum(int(d.queue_failed or 0) for d in devices),
		"per_device": devices[:50],
	}


def _officer_activity(days: int = 7) -> list[dict]:
	since = add_days(now_datetime(), -days)
	return frappe.db.sql(
		"""
		SELECT user,
			COUNT(*) AS sync_sessions,
			MAX(started_on) AS last_session
		FROM `tabSync Session`
		WHERE started_on >= %(since)s
		GROUP BY user
		ORDER BY sync_sessions DESC
		LIMIT 30
		""",
		{"since": since},
		as_dict=True,
	)


def _app_version_matrix() -> list[dict]:
	return frappe.db.sql(
		"""
		SELECT app_version, build_number, platform, COUNT(*) AS reports,
			MAX(reported_at) AS last_seen
		FROM `tabPilot Device Telemetry`
		WHERE app_version != ''
		GROUP BY app_version, build_number, platform
		ORDER BY last_seen DESC
		LIMIT 20
		""",
		as_dict=True,
	)


def _feedback_summary() -> dict:
	new_count = frappe.db.count("Pilot Operational Feedback", {"workflow_status": "new"})
	by_cat = frappe.db.sql(
		"""
		SELECT category, COUNT(*) AS cnt
		FROM `tabPilot Operational Feedback`
		GROUP BY category
		""",
		as_dict=True,
	)
	return {"open": new_count, "by_category": {r.category: r.cnt for r in by_cat}}


@frappe.whitelist(allow_guest=False)
def sync_health():
	_admin_only()
	return success(_sync_health_window())


@frappe.whitelist(allow_guest=False)
def queue_backlog():
	_admin_only()
	return success(_queue_backlog_metrics())


@frappe.whitelist(allow_guest=False)
def inventory_health():
	_admin_only()
	return success(inventory_reconcile())


@frappe.whitelist(allow_guest=False)
def officer_activity():
	_admin_only()
	return success({"officers": _officer_activity()})


@frappe.whitelist(allow_guest=False)
def dashboard():
	"""Aggregated pilot ops view for staging / production monitoring."""
	_admin_only()
	return success(
		{
			"generated_at": str(now_datetime()),
			"sync_health": _sync_health_window(),
			"queue_backlog": _queue_backlog_metrics(),
			"inventory": inventory_reconcile(),
			"officer_activity": _officer_activity(),
			"app_versions": _app_version_matrix(),
			"feedback": _feedback_summary(),
			"recent_logs": frappe.get_all(
				"Operational Log",
				fields=["name", "event_type", "user", "device_id", "recorded_on"],
				order_by="recorded_on desc",
				limit=25,
			),
		}
	)


@frappe.whitelist(allow_guest=False)
def onboarding_checklist():
	"""Officer onboarding steps — returned as structured checklist (client renders)."""
	ensure_authenticated()
	return success(
		{
			"steps": [
				{"id": "login", "title_key": "onboardingLogin", "required": True},
				{"id": "sync_initial", "title_key": "onboardingInitialSync", "required": True},
				{"id": "review_tasks", "title_key": "onboardingReviewTasks", "required": True},
				{"id": "offline_test", "title_key": "onboardingOfflineTest", "required": False},
				{"id": "feedback_channel", "title_key": "onboardingFeedback", "required": False},
			],
			"support_contact": "",
			"pilot_site": frappe.local.site,
		}
	)
