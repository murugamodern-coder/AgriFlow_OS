# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

ASSIGNMENT_FLAG = "agriflow_task_assignment_write"


class ProjectTaskAssignmentHistory(Document):
	def validate(self):
		if not frappe.flags.get(ASSIGNMENT_FLAG) and not self.is_new():
			frappe.throw(_("Assignment history rows are immutable"))

	def on_trash(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Assignment history cannot be deleted"))
