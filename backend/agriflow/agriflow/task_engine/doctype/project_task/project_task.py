# Copyright (c) 2026, Murugan and contributors
import frappe
from frappe import _
from frappe.model.document import Document

from agriflow.task_engine.services.lifecycle import TaskLifecycleService

TASK_WRITE_FLAG = "agriflow_task_write"


class ProjectTask(Document):
	def validate(self):
		if frappe.flags.get(TASK_WRITE_FLAG):
			return
		if not self.is_new():
			TaskLifecycleService().validate_direct_save(self)

	def before_save(self):
		if frappe.flags.get(TASK_WRITE_FLAG):
			return
		if not self.is_new():
			self.doc_version = (self.doc_version or 1) + 1
