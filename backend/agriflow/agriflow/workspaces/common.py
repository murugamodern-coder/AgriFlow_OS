# Copyright (c) 2026, Murugan and contributors
"""Shared helpers for AgriFlow Frappe v15 Workspace repair."""

from __future__ import annotations

import json
from typing import Any


def shortcut(
	label: str,
	link_to: str,
	*,
	color: str = "Blue",
	doc_view: str = "List",
	fmt: str | None = None,
	stats_filter: str | None = None,
) -> dict[str, Any]:
	row: dict[str, Any] = {
		"color": color,
		"doc_view": doc_view,
		"label": label,
		"link_to": link_to,
		"type": "DocType",
	}
	if fmt:
		row["format"] = fmt
	if stats_filter:
		row["stats_filter"] = stats_filter
	return row


def card_break(label: str, link_count: int) -> dict[str, Any]:
	return {
		"hidden": 0,
		"is_query_report": 0,
		"label": label,
		"link_count": link_count,
		"onboard": 0,
		"type": "Card Break",
	}


def workspace_link(label: str, link_to: str, *, onboard: int = 1) -> dict[str, Any]:
	return {
		"dependencies": "",
		"hidden": 0,
		"is_query_report": 0,
		"label": label,
		"link_count": 0,
		"link_to": link_to,
		"link_type": "DocType",
		"onboard": onboard,
		"type": "Link",
	}


def build_content(
	prefix: str,
	shortcut_labels: list[str],
	cards: list[tuple[str, int]],
	*,
	shortcuts_header: str = "Your Shortcuts",
	links_header: str = "Masters & Reports",
	shortcut_col: int = 3,
	card_col: int = 4,
) -> str:
	blocks: list[dict[str, Any]] = [
		{
			"id": f"{prefix}_hdr_shortcuts",
			"type": "header",
			"data": {
				"text": f'<span class="h4"><b>{shortcuts_header}</b></span>',
				"col": 12,
			},
		},
	]
	for index, label in enumerate(shortcut_labels):
		slug = label.lower().replace(" ", "_")
		blocks.append(
			{
				"id": f"{prefix}_sc_{index}_{slug}",
				"type": "shortcut",
				"data": {"shortcut_name": label, "col": shortcut_col},
			}
		)
	blocks.append(
		{
			"id": f"{prefix}_hdr_links",
			"type": "header",
			"data": {
				"text": f'<span class="h4"><b>{links_header}</b></span>',
				"col": 12,
			},
		}
	)
	for card_name, _count in cards:
		slug = card_name.lower().replace(" ", "_")
		blocks.append(
			{
				"id": f"{prefix}_card_{slug}",
				"type": "card",
				"data": {"card_name": card_name, "col": card_col},
			}
		)
	return json.dumps(blocks)


def workspace_doc(
	*,
	name: str,
	module: str,
	icon: str,
	indicator_color: str,
	sequence_id: float,
	shortcuts: list[dict[str, Any]],
	links: list[dict[str, Any]],
	content: str,
) -> dict[str, Any]:
	return {
		"doctype": "Workspace",
		"name": name,
		"label": name,
		"title": name,
		"module": module,
		"icon": icon,
		"indicator_color": indicator_color,
		"public": 1,
		"is_hidden": 0,
		"for_user": "",
		"parent_page": "",
		"restrict_to_domain": "",
		"sequence_id": sequence_id,
		"app": "agriflow",
		"content": content,
		"shortcuts": shortcuts,
		"links": links,
		"charts": [],
		"quick_lists": [],
		"number_cards": [],
		"custom_blocks": [],
		"roles": [],
	}


def repair_workspace(data: dict[str, Any]) -> dict[str, Any]:
	"""Apply Workspace UI definition to an existing or new Workspace record."""
	import frappe

	name = data["name"]

	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
		ws.update(
			{
				"label": data["label"],
				"title": data["title"],
				"module": data["module"],
				"icon": data["icon"],
				"indicator_color": data["indicator_color"],
				"public": data["public"],
				"is_hidden": data["is_hidden"],
				"sequence_id": data["sequence_id"],
				"app": data["app"],
				"content": data["content"],
			}
		)
	else:
		ws = frappe.get_doc(data)

	for fieldname in ("shortcuts", "links"):
		ws.set(fieldname, [])
		for row in data[fieldname]:
			ws.append(fieldname, row)

	ws.set("charts", [])
	ws.set("quick_lists", [])
	ws.set("number_cards", [])
	ws.set("custom_blocks", [])

	ws.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"ok": True,
		"workspace": ws.name,
		"shortcuts": len(ws.shortcuts),
		"links": len(ws.links),
		"content_blocks": len(frappe.parse_json(ws.content or "[]")),
	}
