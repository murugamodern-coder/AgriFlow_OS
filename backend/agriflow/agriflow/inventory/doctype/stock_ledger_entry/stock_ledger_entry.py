# Copyright (c) 2026
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.inventory.services.ledger import LEDGER_WRITE_FLAG


class StockLedgerEntry(Document):
	def validate(self):
		if not self.is_new() and not frappe.flags.get(LEDGER_WRITE_FLAG):
			frappe.throw(_("Stock Ledger Entry is immutable"))

	def on_update(self):
		if not frappe.flags.get(LEDGER_WRITE_FLAG):
			frappe.throw(_("Stock Ledger Entry cannot be updated"))

	def on_trash(self):
		frappe.throw(_("Stock Ledger Entry cannot be deleted"))
