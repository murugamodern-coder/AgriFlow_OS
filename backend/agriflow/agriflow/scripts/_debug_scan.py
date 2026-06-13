import frappe
meta = frappe.get_meta("Farmer")
print([(df.fieldname, df.options) for df in meta.fields if df.fieldtype == "Link"])
