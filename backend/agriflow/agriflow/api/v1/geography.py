# Copyright (c) 2026, Murugan and contributors
"""Geography cascading dropdown APIs."""

from __future__ import annotations

import frappe

from agriflow.api.v1.permissions import ensure_authenticated
from agriflow.api.v1.response import fail, parse_data, success


def _payload(data=None, **kwargs):
	payload = parse_data(data)
	for key, value in kwargs.items():
		if value is not None and value != "":
			payload[key] = value
	return payload


@frappe.whitelist()
def get_states(data=None):
	"""All active states (Tamil Nadu for now)."""
	try:
		ensure_authenticated()
		rows = frappe.get_all(
			"Geo State",
			filters={"is_active": 1},
			fields=["name", "state_name", "lgd_code"],
			order_by="state_name",
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def get_districts(state=None, data=None):
	"""Districts in a state."""
	try:
		ensure_authenticated()
		payload = _payload(data, state=state)
		state_name = payload.get("state")
		if not state_name:
			return fail("VAL_INVALID", "state is required", http_status=400)
		rows = frappe.get_all(
			"District",
			filters={"state": state_name, "is_active": 1},
			fields=["name", "district_name", "lgd_code"],
			order_by="district_name",
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def get_blocks(district=None, data=None):
	"""Blocks in a district."""
	try:
		ensure_authenticated()
		payload = _payload(data, district=district)
		district_name = payload.get("district")
		if not district_name:
			return fail("VAL_INVALID", "district is required", http_status=400)
		rows = frappe.get_all(
			"Block",
			filters={"district": district_name, "is_active": 1},
			fields=["name", "block_name", "lgd_code"],
			order_by="block_name",
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def get_villages(block=None, search=None, limit=50, data=None):
	"""Villages in a block with optional search."""
	try:
		ensure_authenticated()
		payload = _payload(data, block=block, search=search)
		block_name = payload.get("block")
		if not block_name:
			return fail("VAL_INVALID", "block is required", http_status=400)
		limit_val = min(max(int(payload.get("limit", limit)), 1), 100)
		filters: dict = {"block": block_name, "is_active": 1}
		search_text = (payload.get("search") or "").strip()
		if search_text:
			filters["village_name"] = ["like", f"%{search_text}%"]
		rows = frappe.get_all(
			"Village",
			filters=filters,
			fields=["name", "village_name", "lgd_code", "pincode"],
			order_by="village_name",
			limit_page_length=limit_val,
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def get_clusters(block=None, data=None):
	"""Optional clusters for a block."""
	try:
		ensure_authenticated()
		payload = _payload(data, block=block)
		filters: dict = {"is_active": 1}
		if payload.get("block"):
			filters["block"] = payload["block"]
		rows = frappe.get_all(
			"Cluster",
			filters=filters,
			fields=["name", "cluster_name"],
			order_by="cluster_name",
			limit_page_length=200,
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)


@frappe.whitelist()
def get_officers(data=None):
	"""Optional officers for assignment."""
	try:
		ensure_authenticated()
		rows = frappe.get_all(
			"Officer",
			filters={"is_active": 1},
			fields=["name", "officer_name", "officer_code"],
			order_by="officer_name",
			limit_page_length=200,
		)
		return success({"items": rows})
	except frappe.AuthenticationError as exc:
		return fail("AUTH_REQUIRED", str(exc), http_status=401)
