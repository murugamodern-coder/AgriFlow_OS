# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Notification Engine."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def notification_engine_workspace_doc() -> dict:
	shortcuts = [
		shortcut("Notification", "Notification", color="Blue"),
		shortcut("Notification Preference", "Notification Preference", color="Green"),
		shortcut("Delivery Log", "Notification Delivery Log", color="Orange"),
	]
	links = [
		card_break("Inbox", 1),
		workspace_link("Notification", "Notification"),
		card_break("Configuration", 2),
		workspace_link("Notification Preference", "Notification Preference"),
		workspace_link("Notification Delivery Log", "Notification Delivery Log"),
	]
	content = build_content(
		"agriflow_notify",
		["Notification", "Notification Preference", "Delivery Log"],
		[("Inbox", 1), ("Configuration", 2)],
		links_header="Inbox & Configuration",
	)
	return workspace_doc(
		name="Notification Engine",
		module="Notification Engine",
		icon="notification",
		indicator_color="purple",
		sequence_id=35.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
