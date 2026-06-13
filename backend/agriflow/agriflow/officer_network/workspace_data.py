# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Officer Network."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def officer_network_workspace_doc() -> dict:
	shortcuts = [
		shortcut("Officer", "Officer", color="Blue"),
		shortcut("Village", "Village", color="Green"),
		shortcut("Block", "Block", color="Orange"),
		shortcut("District", "District", color="Purple"),
	]
	links = [
		card_break("Geography", 4),
		workspace_link("District", "District"),
		workspace_link("Block", "Block"),
		workspace_link("Cluster", "Cluster"),
		workspace_link("Village", "Village"),
		card_break("Officers", 2),
		workspace_link("Officer", "Officer"),
		workspace_link("Officer Assignment History", "Officer Assignment History"),
	]
	content = build_content(
		"agriflow_officer",
		["Officer", "Village", "Block", "District"],
		[("Geography", 4), ("Officers", 2)],
		links_header="Geography & Officers",
	)
	return workspace_doc(
		name="Officer Network",
		module="Officer Network",
		icon="organization",
		indicator_color="orange",
		sequence_id=15.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
