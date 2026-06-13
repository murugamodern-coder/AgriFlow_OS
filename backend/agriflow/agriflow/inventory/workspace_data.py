# Copyright (c) 2026, Murugan and contributors
"""Canonical Frappe v15 Workspace definition for the Inventory module."""

from __future__ import annotations

import json


def inventory_workspace_shortcuts() -> list[dict]:
	return [
		{
			"color": "Blue",
			"doc_view": "List",
			"format": "{} Active",
			"label": "Inventory Item",
			"link_to": "Inventory Item",
			"stats_filter": '[["Inventory Item","is_active","=",1]]',
			"type": "DocType",
		},
		{
			"color": "Green",
			"doc_view": "List",
			"label": "Warehouse",
			"link_to": "Warehouse",
			"type": "DocType",
		},
		{
			"color": "Orange",
			"doc_view": "List",
			"label": "Stock Ledger Entry",
			"link_to": "Stock Ledger Entry",
			"type": "DocType",
		},
		{
			"color": "Purple",
			"doc_view": "List",
			"label": "Project Material Allocation",
			"link_to": "Project Material Allocation",
			"type": "DocType",
		},
	]


def inventory_workspace_links() -> list[dict]:
	return [
		{
			"hidden": 0,
			"is_query_report": 0,
			"label": "Masters",
			"link_count": 2,
			"onboard": 0,
			"type": "Card Break",
		},
		{
			"dependencies": "",
			"hidden": 0,
			"is_query_report": 0,
			"label": "Inventory Item",
			"link_count": 0,
			"link_to": "Inventory Item",
			"link_type": "DocType",
			"onboard": 1,
			"type": "Link",
		},
		{
			"dependencies": "",
			"hidden": 0,
			"is_query_report": 0,
			"label": "Warehouse",
			"link_count": 0,
			"link_to": "Warehouse",
			"link_type": "DocType",
			"onboard": 1,
			"type": "Link",
		},
		{
			"hidden": 0,
			"is_query_report": 0,
			"label": "Transactions",
			"link_count": 2,
			"onboard": 0,
			"type": "Card Break",
		},
		{
			"dependencies": "",
			"hidden": 0,
			"is_query_report": 0,
			"label": "Stock Ledger Entry",
			"link_count": 0,
			"link_to": "Stock Ledger Entry",
			"link_type": "DocType",
			"onboard": 1,
			"type": "Link",
		},
		{
			"dependencies": "",
			"hidden": 0,
			"is_query_report": 0,
			"label": "Project Material Allocation",
			"link_count": 0,
			"link_to": "Project Material Allocation",
			"link_type": "DocType",
			"onboard": 1,
			"type": "Link",
		},
	]


def inventory_workspace_content() -> str:
	"""Block layout JSON for /app/inventory — shortcuts must match shortcuts[].label."""
	blocks = [
		{
			"id": "agriflow_inv_hdr_shortcuts",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>Your Shortcuts</b></span>',
				"col": 12,
			},
		},
		{
			"id": "agriflow_inv_sc_item",
			"type": "shortcut",
			"data": {"shortcut_name": "Inventory Item", "col": 3},
		},
		{
			"id": "agriflow_inv_sc_wh",
			"type": "shortcut",
			"data": {"shortcut_name": "Warehouse", "col": 3},
		},
		{
			"id": "agriflow_inv_sc_sle",
			"type": "shortcut",
			"data": {"shortcut_name": "Stock Ledger Entry", "col": 3},
		},
		{
			"id": "agriflow_inv_sc_pma",
			"type": "shortcut",
			"data": {"shortcut_name": "Project Material Allocation", "col": 3},
		},
		{
			"id": "agriflow_inv_hdr_links",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>Masters & Transactions</b></span>',
				"col": 12,
			},
		},
		{
			"id": "agriflow_inv_card_masters",
			"type": "card",
			"data": {"card_name": "Masters", "col": 4},
		},
		{
			"id": "agriflow_inv_card_txn",
			"type": "card",
			"data": {"card_name": "Transactions", "col": 4},
		},
	]
	return json.dumps(blocks)


def inventory_workspace_doc() -> dict:
	"""Full Workspace document payload (Workspace DocType only)."""
	return {
		"doctype": "Workspace",
		"name": "Inventory",
		"label": "Inventory",
		"title": "Inventory",
		"module": "Inventory",
		"icon": "stock",
		"indicator_color": "green",
		"public": 1,
		"is_hidden": 0,
		"for_user": "",
		"parent_page": "",
		"restrict_to_domain": "",
		"sequence_id": 20.0,
		"app": "agriflow",
		"content": inventory_workspace_content(),
		"shortcuts": inventory_workspace_shortcuts(),
		"links": inventory_workspace_links(),
		"charts": [],
		"quick_lists": [],
		"number_cards": [],
		"custom_blocks": [],
		"roles": [],
	}
