# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class District(Document):

	def validate(self):
		if not self.district_code:
			frappe.throw(frappe._("District Code is required"))

