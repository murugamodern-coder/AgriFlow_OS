# Copyright (c) 2026, Murugan and contributors
"""FCM delivery worker — legacy HTTP API + queue processor."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import now_datetime

FCM_LEGACY_URL = "https://fcm.googleapis.com/fcm/send"


def _server_key() -> str:
	return (frappe.conf.get("agriflow_fcm_server_key") or "").strip()


def send_fcm_message(
	*,
	token: str,
	title: str,
	body: str,
	data: dict[str, str] | None = None,
) -> tuple[bool, str]:
	"""Send one FCM message. Uses simulate mode when key is empty or 'simulate'."""
	key = _server_key()
	if not key or key.lower() == "simulate":
		return True, "simulated_sent"

	if token.startswith("debug-push-"):
		return True, "debug_token_skipped"

	try:
		import requests
	except ImportError:
		return False, "requests package required for FCM"

	payload = {
		"to": token,
		"notification": {"title": title, "body": body},
		"data": {k: str(v) for k, v in (data or {}).items()},
		"priority": "high",
	}
	try:
		resp = requests.post(
			FCM_LEGACY_URL,
			headers={
				"Authorization": f"key={key}",
				"Content-Type": "application/json",
			},
			json=payload,
			timeout=15,
		)
		body_text = resp.text[:500]
		if resp.status_code == 200:
			result = resp.json()
			if result.get("success", 0) >= 1 or result.get("message_id"):
				return True, body_text
			return False, body_text
		return False, f"http_{resp.status_code}:{body_text}"
	except Exception as exc:
		frappe.log_error(title="FCM send failed", message=str(exc))
		return False, str(exc)[:500]


def send_fcm_with_retry(
	*,
	token: str,
	title: str,
	body: str,
	data: dict[str, str] | None = None,
	max_attempts: int = 3,
) -> tuple[bool, str]:
	"""Phase 20 — retry transient FCM failures."""
	last_msg = ""
	for attempt in range(1, max_attempts + 1):
		ok, msg = send_fcm_message(token=token, title=title, body=body, data=data)
		if ok:
			return True, msg if attempt == 1 else f"{msg} (retry {attempt})"
		last_msg = msg
		if "http_5" not in msg and "timeout" not in msg.lower():
			break
	return False, last_msg


def deliver_to_user(
	*,
	notification_id: str,
	user: str,
	title: str,
	body: str,
	deep_link: str | None = None,
) -> list[dict[str, Any]]:
	"""Fan-out push to all active tokens for user; update Push Delivery Log."""
	tokens = frappe.get_all(
		"Device Push Token",
		filters={"user": user, "is_active": 1},
		fields=["device_id", "push_token"],
	)
	results = []
	data = {"deep_link": deep_link or "", "notification_id": notification_id}
	for t in tokens:
		ok, msg = send_fcm_with_retry(
			token=t.push_token,
			title=title,
			body=body,
			data=data,
		)
		status = "sent" if ok else "failed"
		doc = frappe.get_doc(
			{
				"doctype": "Push Delivery Log",
				"notification": notification_id,
				"device_id": t.device_id,
				"user": user,
				"status": status,
				"provider_response": msg,
				"recorded_on": now_datetime(),
			}
		)
		doc.insert(ignore_permissions=True)
		log_id = doc.name
		results.append(
			{
				"device_id": t.device_id,
				"status": status,
				"log_id": log_id,
			}
		)
	return results


def process_queued_pushes(limit: int = 50) -> dict[str, Any]:
	"""Process Push Delivery Log rows stuck in queued (scheduler worker)."""
	key = _server_key()
	if not key:
		return {"processed": 0, "reason": "fcm_not_configured"}

	rows = frappe.get_all(
		"Push Delivery Log",
		filters={"status": "queued"},
		fields=["name", "notification", "user", "device_id"],
		limit=limit,
		order_by="recorded_on asc",
	)
	processed = 0
	for row in rows:
		token = frappe.db.get_value(
			"Device Push Token",
			{"device_id": row.device_id, "user": row.user, "is_active": 1},
			"push_token",
		)
		if not token:
			frappe.db.set_value("Push Delivery Log", row.name, "status", "failed")
			frappe.db.set_value(
				"Push Delivery Log",
				row.name,
				"provider_response",
				"no_active_token",
			)
			continue
		ok, msg = send_fcm_with_retry(
			token=token,
			title="AgriFlow",
			body=row.notification or "Update",
			data={"notification_id": row.notification or ""},
		)
		frappe.db.set_value(
			"Push Delivery Log",
			row.name,
			{
				"status": "sent" if ok else "failed",
				"provider_response": msg,
			},
		)
		processed += 1
	frappe.db.commit()
	return {"processed": processed, "queued_seen": len(rows)}


def execute():
	"""bench execute entry — process FCM queue."""
	frappe.conf.agriflow_fcm_server_key = frappe.conf.get("agriflow_fcm_server_key") or "simulate"
	return process_queued_pushes()
