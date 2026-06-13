# Copyright (c) 2026, Murugan and contributors
"""Frappe v15 Workspace definition for Task Engine."""

from __future__ import annotations

from agriflow.workspaces.common import (
	build_content,
	card_break,
	shortcut,
	workspace_doc,
	workspace_link,
)


def task_engine_workspace_doc() -> dict:
	shortcuts = [
		shortcut("Project Task", "Project Task", color="Blue"),
		shortcut(
			"Task Assignment History",
			"Project Task Assignment History",
			color="Purple",
		),
	]
	links = [
		card_break("Tasks", 1),
		workspace_link("Project Task", "Project Task"),
		card_break("History", 1),
		workspace_link("Project Task Assignment History", "Project Task Assignment History"),
	]
	content = build_content(
		"agriflow_task",
		["Project Task", "Task Assignment History"],
		[("Tasks", 1), ("History", 1)],
		links_header="Tasks & History",
	)
	return workspace_doc(
		name="Task Engine",
		module="Task Engine",
		icon="checklist",
		indicator_color="green",
		sequence_id=40.0,
		shortcuts=shortcuts,
		links=links,
		content=content,
	)
