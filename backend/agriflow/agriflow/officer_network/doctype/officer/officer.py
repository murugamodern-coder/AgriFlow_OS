# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Officer(Document):

	def validate(self):
		if self.officer_code:
			existing = frappe.db.exists("Officer", {"officer_code": self.officer_code, "name": ("!=", self.name)})
			if existing:
				frappe.throw(frappe._("Officer Code must be unique"))

