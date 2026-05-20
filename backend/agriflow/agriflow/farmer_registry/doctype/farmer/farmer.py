# Copyright (c) 2026, Murugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from agriflow.farmer_registry.utils.validation import (
	has_active_farmer_project,
	normalize_mobile,
	validate_aadhaar_last4,
	validate_geography_chain,
	validate_mobile_digits,
	validate_mobile_unique_per_district,
)


class Farmer(Document):
	def before_validate(self):
		self.mobile_normalized = normalize_mobile(self.mobile)
		if self.alternate_mobile:
			self.alternate_mobile = normalize_mobile(self.alternate_mobile) or None

	def before_save(self):
		if not self.is_new():
			self.doc_version = (self.doc_version or 1) + 1
		elif not self.doc_version:
			self.doc_version = 1

	def validate(self):
		validate_mobile_digits(self.mobile)
		if self.alternate_mobile:
			validate_mobile_digits(self.alternate_mobile, "Alternate Mobile")

		validate_aadhaar_last4(self.aadhaar_last4)
		validate_geography_chain(self.district, self.block, self.village, self.cluster)
		validate_mobile_unique_per_district(self.mobile_normalized, self.district, self.name)

		if self.is_deleted:
			self.is_active = 0

		if not self.is_active and self.name and has_active_farmer_project(self.name):
			frappe.throw(
				frappe._("Cannot deactivate farmer with an active Farmer Project"),
				frappe.ValidationError,
			)

		if self.client_id:
			existing_client = frappe.db.exists(
				"Farmer",
				{"client_id": self.client_id, "name": ("!=", self.name or "")},
			)
			if existing_client:
				frappe.throw(frappe._("Client ID already exists"))
