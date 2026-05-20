# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Block(Document):

	def validate(self):
		if self.district and frappe.db.exists("District", self.district):
			if not frappe.db.get_value("District", self.district, "is_active"):
				frappe.throw(frappe._("District is inactive"))
		if self.block_code and self.district:
			existing = frappe.db.exists(
				"Block",
				{"block_code": self.block_code, "district": self.district, "name": ("!=", self.name)},
			)
			if existing:
				frappe.throw(frappe._("Block Code must be unique within the District"))

