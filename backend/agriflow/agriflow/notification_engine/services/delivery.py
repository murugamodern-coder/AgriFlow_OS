# Copyright (c) 2026, Murugan and contributors
"""Append-only notification delivery with dedupe."""

from __future__ import annotations

import hashlib
from typing import Any

import frappe
from frappe.utils import now_datetime

from agriflow.notification_engine.services.i18n_keys import title_key
from agriflow.notification_engine.services.preferences import is_in_app_enabled

NOTIFICATION_FLAG = "agriflow_notification_write"
DELIVERY_LOG_FLAG = "agriflow_notification_delivery_log_write"
MUTABLE_FIELDS = frozenset({"read_on", "is_deleted"})


def make_delivery_key(
	*,
	timeline_event: str | None,
	notification_type: str,
	recipient: str,
	source_name: str | None = None,
) -> str:
	if timeline_event:
		raw = f"{timeline_event}|{notification_type}|{recipient}"
	else:
		raw = f"{source_name or ''}|{notification_type}|{recipient}"
	return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def delivery_log_exists(delivery_key: str) -> bool:
	return bool(frappe.db.exists("Notification Delivery Log", {"delivery_key": delivery_key}))


def append_delivery_log(
	*,
	delivery_key: str,
	timeline_event: str | None,
	notification: str | None,
	recipient: str,
	notification_type: str,
	status: str,
) -> str:
	if delivery_log_exists(delivery_key):
		return frappe.db.get_value(
			"Notification Delivery Log", {"delivery_key": delivery_key}, "name"
		)
	doc = frappe.get_doc(
		{
			"doctype": "Notification Delivery Log",
			"delivery_key": delivery_key,
			"timeline_event": timeline_event or "",
			"notification": notification or "",
			"recipient": recipient,
			"notification_type": notification_type,
			"status": status,
			"processed_on": now_datetime(),
		}
	)
	frappe.flags[DELIVERY_LOG_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[DELIVERY_LOG_FLAG] = False
	return doc.name


def deliver_one(
	*,
	recipient: str,
	notification_type: str,
	title_i18n_key: str,
	body_preview: str,
	payload_json: dict,
	farmer_project: str,
	farmer: str,
	block: str | None,
	district: str | None,
	timeline_event: str | None,
	source_doctype: str | None,
	source_name: str | None,
	priority: str = "normal",
) -> dict[str, Any]:
	if not recipient:
		key = make_delivery_key(
			timeline_event=timeline_event,
			notification_type=notification_type,
			recipient="",
			source_name=source_name,
		)
		append_delivery_log(
			delivery_key=key,
			timeline_event=timeline_event,
			notification=None,
			recipient="",
			notification_type=notification_type,
			status="skipped_no_recipient",
		)
		return {"status": "skipped_no_recipient"}

	if not is_in_app_enabled(recipient, notification_type):
		key = make_delivery_key(
			timeline_event=timeline_event,
			notification_type=notification_type,
			recipient=recipient,
			source_name=source_name,
		)
		append_delivery_log(
			delivery_key=key,
			timeline_event=timeline_event,
			notification=None,
			recipient=recipient,
			notification_type=notification_type,
			status="skipped_preference",
		)
		return {"status": "skipped_preference", "recipient": recipient}

	key = make_delivery_key(
		timeline_event=timeline_event,
		notification_type=notification_type,
		recipient=recipient,
		source_name=source_name,
	)
	if delivery_log_exists(key):
		existing = frappe.db.get_value("Notification", {"delivery_key": key}, "name")
		return {"status": "skipped_duplicate", "name": existing, "recipient": recipient}

	doc = frappe.get_doc(
		{
			"doctype": "Notification",
			"delivery_key": key,
			"recipient": recipient,
			"notification_type": notification_type,
			"title_i18n_key": title_i18n_key or title_key(notification_type),
			"body_preview": (body_preview or "")[:140],
			"payload_json": payload_json or {},
			"farmer_project": farmer_project,
			"farmer": farmer,
			"block": block or "",
			"district": district or "",
			"timeline_event": timeline_event or "",
			"source_doctype": source_doctype or "",
			"source_name": source_name or "",
			"priority": priority,
			"created_on": now_datetime(),
			"is_deleted": 0,
		}
	)
	frappe.flags[NOTIFICATION_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[NOTIFICATION_FLAG] = False

	append_delivery_log(
		delivery_key=key,
		timeline_event=timeline_event,
		notification=doc.name,
		recipient=recipient,
		notification_type=notification_type,
		status="delivered",
	)
	return {"status": "delivered", "name": doc.name, "recipient": recipient}


def mark_read(notification_name: str, user: str | None = None) -> None:
	user = user or frappe.session.user
	doc = frappe.get_doc("Notification", notification_name)
	if doc.recipient != user and "System Manager" not in frappe.get_roles(user):
		frappe.throw(frappe._("Not permitted"))
	if doc.read_on:
		return
	frappe.flags[NOTIFICATION_FLAG] = True
	try:
		doc.read_on = now_datetime()
		doc.save(ignore_permissions=True)
	finally:
		frappe.flags[NOTIFICATION_FLAG] = False
