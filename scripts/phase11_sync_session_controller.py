# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe.model.document import Document


class SyncSession(Document):
	def validate(self):
		if not self.sync_token:
			if not self.name:
				self.set_new_name()
			self.sync_token = self.name
