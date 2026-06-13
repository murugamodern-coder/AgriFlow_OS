# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Farmer Registry."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def farmer_registry_workspace_doc() -> dict:
	shortcuts = [
		shortcut(
			"Farmer",
			"Farmer",
			color="Green",
			fmt="{} Active",
			stats_filter='[["Farmer","is_active","=",1]]',
		),
	]
	links = [
		card_break("Masters", 1),
		workspace_link("Farmer", "Farmer"),
	]
	content = build_content(
		"agriflow_farmer",
		["Farmer"],
		[("Masters", 1)],
		links_header="Registry",
		shortcut_col=4,
	)
	return workspace_doc(
		name="Farmer Registry",
		module="Farmer Registry",
		icon="users",
		indicator_color="green",
		sequence_id=10.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
