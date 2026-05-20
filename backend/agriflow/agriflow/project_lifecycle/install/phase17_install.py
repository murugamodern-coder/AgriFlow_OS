# Copyright (c) 2026, Murugan and contributors
"""Install Phase 17 pilot DocTypes and register whitelisted methods."""

from __future__ import annotations

import json
from pathlib import Path

import frappe

def _doctype_json_path(folder: str) -> Path:
	# install/phase17_install.py -> project_lifecycle/doctype/<folder>/
	base = Path(__file__).resolve().parent.parent / "doctype"
	return base / folder / f"{folder}.json"


def _import_doctype(json_path: Path) -> str:
	from frappe.modules.import_file import import_file_by_path

	name = json.loads(json_path.read_text(encoding="utf-8"))["name"]
	if frappe.db.exists("DocType", name):
		return f"exists:{name}"
	import_file_by_path(str(json_path), force=True)
	frappe.db.commit()
	return f"imported:{name}"


def execute():
	results = []
	for folder in ("pilot_device_telemetry", "pilot_operational_feedback", "operational_log"):
		jp = _doctype_json_path(folder)
		if not jp.exists():
			results.append(f"missing:{jp}")
			continue
		results.append(_import_doctype(jp))
	return {"ok": True, "doctypes": results}


if __name__ == "__main__":
	print(execute())
