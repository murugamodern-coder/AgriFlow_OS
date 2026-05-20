# Copyright (c) 2026, Murugan and contributors
"""Unread counts and inbox queries."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import get_datetime

from agriflow.api.v1.permissions import get_allowed_blocks


def unread_count(user: str | None = None) -> int:
	user = user or frappe.session.user
	return frappe.db.count(
		"Notification",
		{
			"recipient": user,
			"read_on": ("is", "not set"),
			"is_deleted": 0,
		},
	)


def list_notifications(
	*,
	user: str | None = None,
	unread_only: bool = False,
	notification_type: str | None = None,
	since: str | None = None,
	cursor: str | None = None,
	limit: int = 25,
) -> dict[str, Any]:
	user = user or frappe.session.user
	limit = min(max(int(limit or 25), 1), 100)
	allowed = get_allowed_blocks()

	filters: dict[str, Any] = {"recipient": user, "is_deleted": 0}
	if unread_only:
		filters["read_on"] = ("is", "not set")
	if notification_type:
		filters["notification_type"] = notification_type
	if since:
		filters["created_on"] = (">=", get_datetime(since))

	if allowed is not None:
		if not allowed:
			return {
				"items": [],
				"cursor": None,
				"has_more": False,
				"unread_count": 0,
			}
		filters["block"] = ("in", list(allowed))

	if cursor:
		row = frappe.db.get_value(
			"Notification", cursor, ["created_on", "name"], as_dict=True
		)
		if row:
			filters["name"] = ("<", row.name)

	rows = frappe.get_all(
		"Notification",
		filters=filters,
		fields=[
			"name",
			"notification_type",
			"title_i18n_key",
			"body_preview",
			"payload_json",
			"priority",
			"read_on",
			"created_on",
			"farmer_project",
			"timeline_event",
		],
		order_by="created_on desc, name desc",
		limit=limit + 1,
	)

	has_more = len(rows) > limit
	if has_more:
		rows = rows[:limit]
	next_cursor = rows[-1].name if rows and has_more else None

	return {
		"items": rows,
		"cursor": next_cursor,
		"has_more": has_more,
		"unread_count": unread_count(user),
	}
