# Copyright (c) 2026, Murugan and contributors
"""Apply Farmer geography link_filters from DocType JSON without full migrate."""

from __future__ import annotations

import frappe

FILTERS = {
	"district": '[["District","state","=","eval:doc.state"]]',
	"block": '[["Block","district","=","eval:doc.district"]]',
	"village": '[["Village","block","=","eval:doc.block"]]',
}


def apply_farmer_link_filters() -> dict:
	doc = frappe.get_doc("DocType", "Farmer")
	updated: list[str] = []
	for field in doc.fields:
		target = FILTERS.get(field.fieldname)
		if target and field.link_filters != target:
			field.link_filters = target
			updated.append(field.fieldname)
	if updated:
		doc.save(ignore_permissions=True)
		frappe.clear_cache(doctype="Farmer")
	return {"updated_fields": updated}
