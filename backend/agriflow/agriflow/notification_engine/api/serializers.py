# Copyright (c) 2026, Murugan and contributors
"""Mobile-friendly notification serializers."""

from __future__ import annotations

import json
from typing import Any


def to_notification_item(row: dict) -> dict[str, Any]:
	payload = row.get("payload_json") or {}
	if isinstance(payload, str):
		try:
			payload = json.loads(payload)
		except json.JSONDecodeError:
			payload = {}
	created = row.get("created_on")
	if hasattr(created, "isoformat"):
		created = created.isoformat()
	read_on = row.get("read_on")
	return {
		"name": row.get("name"),
		"notification_type": row.get("notification_type"),
		"title_i18n_key": row.get("title_i18n_key"),
		"body_preview": row.get("body_preview"),
		"payload": payload,
		"priority": row.get("priority") or "normal",
		"read": bool(read_on),
		"read_on": read_on.isoformat() if read_on and hasattr(read_on, "isoformat") else read_on,
		"created_on": created,
		"farmer_project": row.get("farmer_project"),
		"farmer": row.get("farmer"),
		"block": row.get("block"),
		"timeline_event": row.get("timeline_event") or None,
	}
