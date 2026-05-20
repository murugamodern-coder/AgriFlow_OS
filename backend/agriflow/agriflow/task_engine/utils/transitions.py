# Copyright (c) 2026, Murugan and contributors
"""Allowed Project Task status transitions."""

from __future__ import annotations

TERMINAL = frozenset({"completed", "cancelled"})
OPEN_QUEUE = frozenset({"open", "assigned", "in_progress", "blocked"})

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
	"open": frozenset({"assigned", "cancelled"}),
	"assigned": frozenset({"in_progress", "open", "blocked", "cancelled"}),
	"in_progress": frozenset({"blocked", "completed", "cancelled"}),
	"blocked": frozenset({"in_progress", "cancelled"}),
	"completed": frozenset(),
	"cancelled": frozenset(),
}


def can_transition(from_status: str, to_status: str) -> bool:
	return to_status in ALLOWED_TRANSITIONS.get(from_status or "open", frozenset())
