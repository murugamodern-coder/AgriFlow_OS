# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Cluster(Document):

	def validate(self):
		if self.block and self.district:
			block_district = frappe.db.get_value("Block", self.block, "district")
			if block_district != self.district:
				frappe.throw(frappe._("District must match the selected Block"))
		if self.cluster_code and self.block:
			existing = frappe.db.exists(
				"Cluster",
				{"cluster_code": self.cluster_code, "block": self.block, "name": ("!=", self.name)},
			)
			if existing:
				frappe.throw(frappe._("Cluster Code must be unique within the Block"))

