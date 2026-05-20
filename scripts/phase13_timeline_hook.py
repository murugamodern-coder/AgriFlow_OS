# Copyright (c) 2026, Murugan and contributors
"""Optional timeline emits — OFF by default."""

from __future__ import annotations

import frappe

EMIT_TIMELINE_MATERIAL = False


def maybe_emit_material_event(
	event_type: str,
	farmer_project: str,
	*,
	payload: dict | None = None,
) -> str | None:
	if not EMIT_TIMELINE_MATERIAL:
		return None
	try:
		from agriflow.project_lifecycle.services.timeline import get_timeline_service

		return get_timeline_service().emit(
			event_type,
			farmer_project,
			payload=payload or {},
			event_source="inventory",
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "inventory.timeline")
		return None
