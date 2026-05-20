# Copyright (c) 2026, Murugan and contributors
"""Farmer API — list for mobile demo (read-only)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from agriflow.api.v1.permissions import assert_block_scope, ensure_authenticated, get_allowed_blocks
from agriflow.api.v1.response import fail, parse_data, success


def _iso(dt) -> str | None:
	if not dt:
		return None
	return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


@frappe.whitelist()
def list(data=None):
	"""agriflow.api.v1.farmer.list — scoped farmer search."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		limit = min(max(int(payload.get("limit", 50)), 1), 100)
		filters: dict[str, Any] = {"is_deleted": 0, "is_active": 1}
		if payload.get("block"):
			filters["block"] = payload["block"]
		if payload.get("village"):
			filters["village"] = payload["village"]
		search = (payload.get("search") or "").strip()
		allowed = get_allowed_blocks()
		if allowed is not None:
			filters["block"] = ("in", list(allowed))
		rows = frappe.get_all(
			"Farmer",
			filters=filters,
			fields=[
				"name",
				"farmer_name",
				"mobile",
				"block",
				"village",
				"district",
				"cluster",
				"doc_version",
				"modified",
			],
			order_by="modified desc",
			limit_page_length=limit,
		)
		if search:
			needle = search.lower()
			rows = [
				r
				for r in rows
				if needle in (r.farmer_name or "").lower()
				or needle in (r.mobile or "").lower()
				or needle in (r.name or "").lower()
			]
		for row in rows:
			row["modified"] = _iso(row.modified)
			if row.block:
				assert_block_scope(row.block)
		return success({"items": rows, "has_more": False, "cursor": None})
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)


@frappe.whitelist()
def get(data=None):
	"""agriflow.api.v1.farmer.get — farmer profile for timeline header."""
	try:
		ensure_authenticated()
		payload = parse_data(data)
		name = payload.get("name")
		if not name:
			return fail("VAL_INVALID", _("name is required"), http_status=400)
		if not frappe.db.exists("Farmer", {"name": name, "is_deleted": 0}):
			return fail("NOT_FOUND", _("Farmer not found"), http_status=404)
		row = frappe.get_doc("Farmer", name)
		if row.block:
			assert_block_scope(row.block)
		block_name = frappe.db.get_value("Block", row.block, "block_name") if row.block else None
		village_name = frappe.db.get_value("Village", row.village, "village_name") if row.village else None
		cluster_name = frappe.db.get_value("Cluster", row.cluster, "cluster_name") if row.cluster else None
		return success(
			{
				"name": row.name,
				"farmer_name": row.farmer_name,
				"father_name": row.father_name,
				"mobile": row.mobile,
				"alternate_mobile": row.alternate_mobile,
				"block": row.block,
				"block_name": block_name,
				"village": row.village,
				"village_name": village_name,
				"cluster": row.cluster,
				"cluster_name": cluster_name,
				"district": row.district,
				"land_extent_acres": row.land_extent_acres,
				"primary_survey_number": row.primary_survey_number,
				"tags": row.tags,
				"notes": row.notes,
				"doc_version": row.doc_version,
			}
		)
	except frappe.PermissionError as exc:
		return fail("PERM_DENIED", str(exc), http_status=403)
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
	except frappe.DoesNotExistError as exc:
		return fail("NOT_FOUND", str(exc), http_status=404)
	except frappe.ValidationError as exc:
		return fail("VAL_INVALID", str(exc), http_status=400)
