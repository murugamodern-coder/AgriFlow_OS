# Copyright (c) 2026, Murugan and contributors
"""Per-user notification preferences."""

from __future__ import annotations

import json

import frappe

from agriflow.notification_engine.services.i18n_keys import NOTIFICATION_TYPES

PREF_FLAG = "agriflow_notification_preference_write"

DEFAULT_PREFS = {t: {"in_app": True} for t in NOTIFICATION_TYPES}


def get_preferences(user: str | None = None) -> dict:
	user = user or frappe.session.user
	raw = frappe.db.get_value("Notification Preference", {"user": user}, "preferences_json")
	if not raw:
		return dict(DEFAULT_PREFS)
	if isinstance(raw, str):
		try:
			raw = json.loads(raw)
		except json.JSONDecodeError:
			return dict(DEFAULT_PREFS)
	return {**DEFAULT_PREFS, **(raw or {})}


def is_in_app_enabled(user: str, notification_type: str) -> bool:
	prefs = get_preferences(user)
	entry = prefs.get(notification_type) or {}
	return bool(entry.get("in_app", True))


def ensure_preference_row(user: str) -> None:
	if frappe.db.exists("Notification Preference", {"user": user}):
		return
	doc = frappe.get_doc(
		{
			"doctype": "Notification Preference",
			"user": user,
			"preferences_json": DEFAULT_PREFS,
		}
	)
	frappe.flags[PREF_FLAG] = True
	try:
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags[PREF_FLAG] = False
