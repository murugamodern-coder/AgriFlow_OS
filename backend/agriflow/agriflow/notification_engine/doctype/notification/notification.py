# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.notification_engine.services.delivery import MUTABLE_FIELDS, NOTIFICATION_FLAG


class Notification(Document):
	def validate(self):
		if self.is_new():
			return
		if frappe.flags.get(NOTIFICATION_FLAG):
			return
		for df in self.meta.fields:
			fn = df.fieldname
			if fn in MUTABLE_FIELDS:
				continue
			if self.has_value_changed(fn):
				frappe.throw(_("Notification content is immutable"))
