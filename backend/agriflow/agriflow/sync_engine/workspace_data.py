# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Sync Engine."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def sync_engine_workspace_doc() -> dict:
	shortcuts = [
		shortcut("Sync Session", "Sync Session", color="Blue"),
		shortcut("Sync Mutation Log", "Sync Mutation Log", color="Orange"),
	]
	links = [
		card_break("Sessions", 1),
		workspace_link("Sync Session", "Sync Session"),
		card_break("Audit", 1),
		workspace_link("Sync Mutation Log", "Sync Mutation Log"),
	]
	content = build_content(
		"agriflow_sync",
		["Sync Session", "Sync Mutation Log"],
		[("Sessions", 1), ("Audit", 1)],
		links_header="Sessions & Audit",
	)
	return workspace_doc(
		name="Sync Engine",
		module="Sync Engine",
		icon="retweet",
		indicator_color="blue",
		sequence_id=30.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
