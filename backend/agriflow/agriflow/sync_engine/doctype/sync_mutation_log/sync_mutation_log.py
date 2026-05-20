# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

LOG_FLAG = "agriflow_sync_mutation_log_write"


class SyncMutationLog(Document):
	def validate(self):
		if not frappe.flags.get(LOG_FLAG) and not self.is_new():
			frappe.throw(_("Sync mutation logs are immutable"))

	def on_trash(self):
		if frappe.session.user != "Administrator":
			frappe.throw(_("Sync mutation logs cannot be deleted"))
