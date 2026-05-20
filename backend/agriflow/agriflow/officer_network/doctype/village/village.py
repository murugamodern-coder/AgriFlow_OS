# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Village(Document):

	def validate(self):
		if self.cluster and self.block:
			cluster_block = frappe.db.get_value("Cluster", self.cluster, "block")
			if cluster_block != self.block:
				frappe.throw(frappe._("Block must match the selected Cluster"))
		if self.village_code and self.block:
			existing = frappe.db.exists(
				"Village",
				{"village_code": self.village_code, "block": self.block, "name": ("!=", self.name)},
			)
			if existing:
				frappe.throw(frappe._("Village Code must be unique within the Block"))

