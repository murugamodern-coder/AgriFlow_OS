# Copyright (c) 2026, Murugan and contributors
"""Resolve notification recipients."""

from __future__ import annotations

import frappe

FALLBACK_ROLES = frozenset({"Field Staff", "Office Manager"})
BYPASS_ROLES = frozenset({"Administrator", "System Manager"})


def _user_has_block(user: str, block: str) -> bool:
	if not block:
		return False
	roles = set(frappe.get_roles(user))
	if roles & BYPASS_ROLES:
		return True
	return bool(
		frappe.db.exists(
			"User Permission",
			{"user": user, "allow": "Block", "for_value": block},
		)
	)


def users_for_block_roles(block: str, roles: frozenset[str] | None = None) -> list[str]:
	if not block:
		return []
	roles = roles or FALLBACK_ROLES
	users = frappe.db.sql(
		"""
		SELECT DISTINCT hr.parent
		FROM `tabHas Role` hr
		INNER JOIN `tabUser` u ON u.name = hr.parent
		WHERE hr.role IN %(roles)s AND u.enabled = 1 AND u.name NOT IN ('Guest', 'Administrator')
		""",
		{"roles": tuple(roles)},
		pluck=True,
	)
	return sorted({u for u in users if _user_has_block(u, block)})


def resolve_task_recipients(task_name: str) -> list[str]:
	task = frappe.db.get_value(
		"Project Task",
		task_name,
		["assigned_to", "block", "farmer_project"],
		as_dict=True,
	)
	if not task:
		return []
	recipients: set[str] = set()
	if task.assigned_to:
		recipients.add(task.assigned_to)
	else:
		recipients.update(users_for_block_roles(task.block))
	return sorted(recipients)


def resolve_project_block_recipients(project_name: str) -> list[str]:
	block = frappe.db.get_value("Farmer Project", project_name, "block")
	return users_for_block_roles(block) if block else []


def resolve_manual_note_recipients(project_name: str, *, actor: str | None = None) -> list[str]:
	recipients = set(resolve_project_block_recipients(project_name))
	if actor:
		recipients.add(actor)
	open_tasks = frappe.get_all(
		"Project Task",
		filters={
			"farmer_project": project_name,
			"is_deleted": 0,
			"status": ("in", ["open", "assigned", "in_progress", "blocked"]),
			"assigned_to": ("is", "set"),
		},
		pluck="assigned_to",
	)
	recipients.update(t for t in open_tasks if t)
	return sorted(recipients)
