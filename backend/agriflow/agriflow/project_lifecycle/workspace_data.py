# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Project Lifecycle."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def project_lifecycle_workspace_doc() -> dict:
	shortcuts = [
		shortcut("Farmer Project", "Farmer Project", color="Blue"),
		shortcut("Timeline Event", "Timeline Event", color="Green"),
		shortcut("Project Stage", "Project Stage", color="Orange"),
		shortcut("Support Ticket", "Support Ticket", color="Red"),
	]
	links = [
		card_break("Workflow", 3),
		workspace_link("Farmer Project", "Farmer Project"),
		workspace_link("Timeline Event", "Timeline Event"),
		workspace_link("Project Stage", "Project Stage"),
		card_break("Operations", 3),
		workspace_link("Customer Onboarding", "Customer Onboarding"),
		workspace_link("Support Ticket", "Support Ticket"),
		workspace_link("Device Push Token", "Device Push Token"),
	]
	content = build_content(
		"agriflow_lifecycle",
		["Farmer Project", "Timeline Event", "Project Stage", "Support Ticket"],
		[("Workflow", 3), ("Operations", 3)],
		links_header="Workflow & Operations",
	)
	return workspace_doc(
		name="Project Lifecycle",
		module="Project Lifecycle",
		icon="milestones",
		indicator_color="blue",
		sequence_id=25.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
