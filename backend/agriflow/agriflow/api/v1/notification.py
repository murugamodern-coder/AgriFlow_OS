# Copyright (c) 2026, Murugan and contributors
"""Notification inbox APIs — not part of sync.pull."""

from __future__ import annotations

import builtins

import frappe

_pylist = builtins.list
from frappe import _

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success
from agriflow.notification_engine.api.serializers import to_notification_item
from agriflow.notification_engine.services.delivery import mark_read as set_notification_read
from agriflow.notification_engine.services.unread import list_notifications
from agriflow.notification_engine.services.unread import unread_count as count_unread


@frappe.whitelist()
def list(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		out = list_notifications(
			unread_only=bool(payload.get("unread_only")),
			notification_type=payload.get("notification_type"),
			since=payload.get("since"),
			cursor=payload.get("cursor"),
			limit=payload.get("limit", 25),
		)
		items = [to_notification_item(r) for r in out["items"]]
		return success(
			{
				"items": items,
				"cursor": out["cursor"],
				"has_more": out["has_more"],
				"unread_count": out["unread_count"],
			}
		)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def unread_count(data=None):
	try:
		ensure_authenticated()
		return success({"count": count_unread()})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def mark_read(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		targets: list[str] = []
		if payload.get("name"):
			targets.append(str(payload["name"]))
		extra = payload.get("names")
		if isinstance(extra, _pylist):
			targets.extend(str(x) for x in extra)
		elif extra:
			targets.append(str(extra))
		names = targets
		if not names:
			return fail("VAL_INVALID", _("name or names required"), http_status=400)
		for n in names:
			set_notification_read(n)
		return success({"marked": names, "unread_count": count_unread()})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)


@frappe.whitelist()
def mark_all_read(data=None):
	try:
		ensure_authenticated()
		payload = parse_data(data)
		filters = {
			"recipient": frappe.session.user,
			"read_on": ("is", "not set"),
			"is_deleted": 0,
		}
		if payload.get("notification_type"):
			filters["notification_type"] = payload["notification_type"]
		rows = frappe.get_all("Notification", filters=filters, pluck="name", limit=500)
		for n in rows:
			set_notification_read(n)
		return success({"marked_count": len(rows), "unread_count": count_unread()})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
