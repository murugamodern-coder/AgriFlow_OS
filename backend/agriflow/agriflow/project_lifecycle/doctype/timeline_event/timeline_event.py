# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

TIMELINE_FLAG = "agriflow_timeline_write"


class TimelineEvent(Document):
	def validate(self):
		if not self.is_new() and not frappe.flags.get(TIMELINE_FLAG):
			frappe.throw(_("Timeline events are immutable and cannot be modified"))

	def on_trash(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Timeline events cannot be deleted"))
