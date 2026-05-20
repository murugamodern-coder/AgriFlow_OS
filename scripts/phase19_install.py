# Copyright (c) 2026, Murugan and contributors
"""Install Phase 19 operational incident DocType."""

from __future__ import annotations

import json
from pathlib import Path

import frappe


def _import_doctype(json_path: Path) -> str:
	from frappe.modules.import_file import import_file_by_path

	name = json.loads(json_path.read_text(encoding="utf-8"))["name"]
	if frappe.db.exists("DocType", name):
		return f"exists:{name}"
	import_file_by_path(str(json_path), force=True)
	frappe.db.commit()
	return f"imported:{name}"


def execute():
	base = Path(__file__).resolve().parent.parent / "doctype"
	jp = base / "operational_incident" / "operational_incident.json"
	if not jp.exists():
		return {"ok": False, "error": f"missing {jp}"}
	return {"ok": True, "doctype": _import_doctype(jp)}
