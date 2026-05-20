# Copyright (c) 2026, Murugan and contributors
"""Lightweight sync pull payloads."""

from __future__ import annotations

from typing import Any


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def project_sync_item(row) -> dict[str, Any]:
	return {
		"name": row.name,
		"farmer": row.farmer,
		"project_title": row.get("project_title") if isinstance(row, dict) else row.project_title,
		"current_stage": row.current_stage,
		"stage_sequence": row.stage_sequence,
		"status": row.status,
		"doc_version": row.doc_version,
		"block": row.block,
		"cluster": row.cluster,
		"village": row.village,
		"officer": row.officer,
		"client_id": row.get("client_id") if isinstance(row, dict) else row.client_id,
		"is_deleted": row.get("is_deleted") or 0,
		"modified": _iso(row.modified),
	}


def tombstone(name: str, modified, is_deleted: int = 1) -> dict[str, Any]:
	return {"name": name, "is_deleted": is_deleted, "modified": _iso(modified)}
