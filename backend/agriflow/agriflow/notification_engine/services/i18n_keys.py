# Copyright (c) 2026, Murugan and contributors
"""Notification title i18n keys."""

from __future__ import annotations

TITLE_KEYS: dict[str, str] = {
	"task_assigned": "notification.task_assigned.title",
	"task_reassigned": "notification.task_reassigned.title",
	"task_completed": "notification.task_completed.title",
	"task_overdue": "notification.task_overdue.title",
	"project_stage_changed": "notification.project_stage_changed.title",
	"manual_note": "notification.manual_note.title",
	"system_alert": "notification.system_alert.title",
}

NOTIFICATION_TYPES = frozenset(TITLE_KEYS.keys())


def title_key(notification_type: str) -> str:
	return TITLE_KEYS.get(notification_type, "notification.generic.title")
