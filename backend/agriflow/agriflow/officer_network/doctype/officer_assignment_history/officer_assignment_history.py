# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OfficerAssignmentHistory(Document):

	def validate(self):
		from agriflow.officer_network.services.officer_assignment import validate_assignment

		validate_assignment(self)

	def before_save(self):
		self.is_active = 0 if self.valid_to else 1

