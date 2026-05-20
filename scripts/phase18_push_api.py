# Copyright (c) 2026, Murugan and contributors
"""Push notification foundation — token registry + delivery metrics (no FCM HTTP in dev)."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success


def _ensure_push_doctypes():
	for dt in ("Device Push Token", "Push Delivery Log"):
		if not frappe.db.exists("DocType", dt):
			frappe.throw(f"Missing {dt}. Run phase18_install.execute", frappe.ValidationError)


@frappe.whitelist(allow_guest=False)
def register_token(data=None):
	"""Register or refresh FCM/device push token for officer handset."""
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
	"""Internal — record delivery attempt for metrics."""
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
	"""Admin — notification delivery counts (last 7 days)."""
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
	return success(
		{
			"by_status": {r.status: r.cnt for r in rows},
			"active_tokens": active_tokens,
			"fcm_configured": bool(frappe.conf.get("agriflow_fcm_server_key")),
		}
	)


def fanout_push_stub(notification_name: str, user: str, deep_link: str | None = None) -> list[str]:
	"""Foundation stub — logs queued delivery per active token (wire FCM HTTP when key set)."""
	_ensure_push_doctypes()
	tokens = frappe.get_all(
		"Device Push Token",
		filters={"user": user, "is_active": 1},
		fields=["name", "device_id", "push_token"],
	)
	log_ids = []
	fcm_key = frappe.conf.get("agriflow_fcm_server_key")
	for t in tokens:
		status = "queued" if fcm_key else "skipped_offline"
		msg = "FCM not configured — logged only" if not fcm_key else "queued for FCM worker"
		log_ids.append(
			queue_push_delivery(
				notification_id=notification_name,
				user=user,
				device_id=t.device_id,
				status=status,
				provider_response=msg,
			)
		)
	return log_ids
