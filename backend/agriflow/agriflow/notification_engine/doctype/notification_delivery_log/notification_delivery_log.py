# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.notification_engine.services.delivery import DELIVERY_LOG_FLAG


class NotificationDeliveryLog(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_("Notification Delivery Log is append-only"))

	def on_update(self):
		if not frappe.flags.get(DELIVERY_LOG_FLAG):
			frappe.throw(_("Notification Delivery Log is immutable"))
