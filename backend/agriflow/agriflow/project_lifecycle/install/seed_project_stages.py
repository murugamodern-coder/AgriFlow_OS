# Copyright (c) 2026, Murugan and contributors

def after_migrate():
	import frappe
	from frappe.core.doctype.data_import.data_import import import_doc

	if frappe.db.count("Project Stage", {"is_active": 1}) >= 12:
		return
	path = frappe.get_app_path("agriflow", "fixtures", "project_stage.json")
	import_doc(path)
