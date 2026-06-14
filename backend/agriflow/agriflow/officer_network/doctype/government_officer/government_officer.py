"""Government Officer controller."""

from __future__ import annotations
import frappe
from frappe.model.document import Document


class GovernmentOfficer(Document):
    def validate(self):
        if self.mobile and len(self.mobile) < 10:
            frappe.throw("Mobile must be at least 10 digits")