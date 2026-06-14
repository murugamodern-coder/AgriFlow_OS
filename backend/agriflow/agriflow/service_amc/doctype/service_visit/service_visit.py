"""Service Visit controller."""

from __future__ import annotations
import frappe
from frappe.model.document import Document


class ServiceVisit(Document):
    def validate(self):
        if self.visit_number and not (1 <= self.visit_number <= 6):
            frappe.throw(f"Visit number must be 1-6 for 3-year AMC")
        
        if self.completed and not self.actual_visit_date:
            self.actual_visit_date = frappe.utils.today()
        
        if self.completed and self.visit_status not in ["Completed"]:
            self.visit_status = "Completed"