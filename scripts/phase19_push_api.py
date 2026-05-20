# Copyright (c) 2026, Murugan and contributors
"""Push API — token registry, FCM delivery, metrics (Phase 19)."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.project_lifecycle.install.phase19_fcm_delivery import (
	deliver_to_user,
	process_queued_pushes,
)


def _ensure_push_doctypes():
	for dt in ("Device Push Token", "Push Delivery Log"):
		if not frappe.db.exists("DocType", dt):
			frappe.throw(f"Missing {dt}. Run phase18_install.execute", frappe.ValidationError)


@frappe.whitelist(allow_guest=False)
def register_token(data=None):
	ensure_authenticated()
	_ensure_push_doctypes()
	payload = parse_data(data)
	device_id = (payload.get("device_id") or "").strip()
	token = (payload.get("push_token") or "").strip()
	if not device_id or not token:
		return fail("VAL_INVALID", "device_id and push_token required")

	existing = frappe.db.get_value(
		"Device Push Token",
		{"device_id": device_id, "user": frappe.session.user},
		"name",
	)
	row = {
		"doctype": "Device Push Token",
		"device_id": device_id,
		"user": frappe.session.user,
		"platform": payload.get("platform") or "android",
		"push_token": token,
		"app_version": payload.get("app_version") or "",
		"is_active": 1,
		"last_seen": now_datetime(),
	}
	if existing:
		doc = frappe.get_doc("Device Push Token", existing)
		doc.update(row)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc(row)
		doc.insert(ignore_permissions=True)

	return success({"token_id": doc.name})


def queue_push_delivery(
	*,
	notification_id: str,
	user: str,
	device_id: str,
	status: str = "queued",
	provider_response: str | None = None,
) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Push Delivery Log",
			"notification": notification_id,
			"device_id": device_id,
			"user": user,
			"status": status,
			"provider_response": provider_response or "",
			"recorded_on": now_datetime(),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist(allow_guest=False)
def delivery_metrics():
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	_ensure_push_doctypes()
	rows = frappe.db.sql(
		"""
		SELECT status, COUNT(*) AS cnt
		FROM `tabPush Delivery Log`
		WHERE recorded_on >= DATE_SUB(NOW(), INTERVAL 7 DAY)
		GROUP BY status
		""",
		as_dict=True,
	)
	active_tokens = frappe.db.count("Device Push Token", {"is_active": 1})
	key = frappe.conf.get("agriflow_fcm_server_key") or ""
	return success(
		{
			"by_status": {r.status: r.cnt for r in rows},
			"active_tokens": active_tokens,
			"fcm_configured": bool(key),
			"fcm_mode": "simulate" if key.lower() == "simulate" else ("live" if key else "off"),
		}
	)


@frappe.whitelist(allow_guest=False)
def process_queue():
	"""Admin/scheduler — drain queued FCM deliveries."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("System Manager required", frappe.PermissionError)
	return success(process_queued_pushes())


def fanout_push(
	notification_name: str,
	user: str,
	deep_link: str | None = None,
	*,
	title: str | None = None,
	body: str | None = None,
) -> list[dict]:
	"""Deliver push via FCM (or simulate). Replaces phase18 stub."""
	_ensure_push_doctypes()
	return deliver_to_user(
		notification_id=notification_name,
		user=user,
		title=title or "AgriFlow",
		body=body or "You have a new update",
		deep_link=deep_link,
	)


def fanout_push_stub(notification_name: str, user: str, deep_link: str | None = None) -> list:
	"""Backward-compatible alias for verify scripts."""
	return fanout_push(notification_name, user, deep_link)
