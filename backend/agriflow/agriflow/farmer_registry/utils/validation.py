# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

"""Farmer validation helpers."""

from __future__ import annotations

import re

import frappe
from frappe import _


_MOBILE_RE = re.compile(r"\D+")


def normalize_mobile(value: str | None) -> str:
	"""Strip non-digits; return digits-only string (may be empty)."""
	if not value:
		return ""
	return _MOBILE_RE.sub("", str(value).strip())


def validate_mobile_digits(mobile: str, field_label: str = "Mobile") -> None:
	digits = normalize_mobile(mobile)
	if len(digits) != 10:
		frappe.throw(_("{0} must be exactly 10 digits").format(field_label))


def validate_aadhaar_last4(value: str | None) -> None:
	if not value:
		return
	clean = str(value).strip()
	if not clean.isdigit() or len(clean) > 4:
		frappe.throw(_("Aadhaar (last 4) must be up to 4 digits only"))


def validate_geography_chain(district: str, block: str, village: str, cluster: str | None = None) -> None:
	if not (district and block and village):
		return

	if not frappe.db.exists("District", district):
		frappe.throw(_("District not found"))
	if not frappe.db.get_value("District", district, "is_active"):
		frappe.throw(_("District is inactive"))

	if not frappe.db.exists("Block", block):
		frappe.throw(_("Block not found"))
	block_district = frappe.db.get_value("Block", block, "district")
	if block_district != district:
		frappe.throw(_("Block must belong to the selected District"))
	if not frappe.db.get_value("Block", block, "is_active"):
		frappe.throw(_("Block is inactive"))

	if not frappe.db.exists("Village", village):
		frappe.throw(_("Village not found"))
	village_block = frappe.db.get_value("Village", village, "block")
	if village_block != block:
		frappe.throw(_("Village must belong to the selected Block"))
	if not frappe.db.get_value("Village", village, "is_active"):
		frappe.throw(_("Village is inactive"))

	if cluster:
		village_cluster = frappe.db.get_value("Village", village, "cluster")
		if village_cluster and village_cluster != cluster:
			frappe.throw(_("Cluster must match the selected Village"))


def validate_mobile_unique_per_district(mobile_normalized: str, district: str, name: str | None) -> None:
	if not mobile_normalized or not district:
		return
	filters = {
		"mobile_normalized": mobile_normalized,
		"district": district,
		"is_deleted": 0,
	}
	if name:
		filters["name"] = ("!=", name)
	existing = frappe.db.exists("Farmer", filters)
	if existing:
		frappe.throw(_("Mobile number already registered for this district"))


def has_active_farmer_project(farmer_name: str) -> bool:
	if not frappe.db.table_exists("tabFarmer Project"):
		return False
	return bool(
		frappe.db.exists(
			"Farmer Project",
			{"farmer": farmer_name, "status": "active"},
		)
	)
