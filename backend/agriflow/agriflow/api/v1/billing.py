# Copyright (c) 2026, Murugan and contributors
"""Billing APIs — Cash & Carry, Project Sale, item search (Week 3 Phase 3.1)."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt, nowdate

from agriflow.api.v1.response import fail, success


def _selling_defaults(company: str) -> dict:
	price_list = (
		frappe.db.get_single_value("Selling Settings", "selling_price_list")
		or frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name")
		or "Standard Selling"
	)
	currency = frappe.db.get_value("Price List", price_list, "currency") or "INR"
	return {
		"selling_price_list": price_list,
		"price_list_currency": currency,
		"plc_conversion_rate": 1,
		"cost_center": frappe.db.get_value("Company", company, "cost_center"),
	}


def _default_company() -> str:
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		frappe.throw(_("Default Company not configured. Run bootstrap_billing_setup."))
	return company


def _default_warehouse() -> str:
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	if not warehouse:
		frappe.throw(_("Default Warehouse not configured. Run bootstrap_billing_setup."))
	return warehouse


def _invoice_items(items: list[dict]) -> list[dict]:
	warehouse = _default_warehouse()
	return [
		{
			"item_code": it["item_code"],
			"qty": flt(it["qty"]),
			"rate": flt(it["rate"]),
			"warehouse": warehouse,
		}
		for it in items
	]


@frappe.whitelist()
def get_or_create_walkin_customer():
	"""Return the default walk-in customer (singleton)."""
	name = "Walk-in Customer"
	if not frappe.db.exists("Customer", name):
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_group": "Individual",
				"territory": "India",
				"customer_type": "Individual",
			}
		)
		customer.insert(ignore_permissions=True)
		frappe.db.commit()
	return name


@frappe.whitelist()
def create_cash_carry_invoice(items, customer_name="", customer_mobile="", payment_mode="Cash"):
	"""Create a Cash & Carry Sales Invoice in one call."""
	if isinstance(items, str):
		items = json.loads(items)

	walkin = get_or_create_walkin_customer()
	company = _default_company()

	invoice = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"company": company,
			"customer": walkin,
			"agriflow_sale_mode": "Cash & Carry",
			"agriflow_walkin_customer_name": customer_name or "Walk-in",
			"agriflow_walkin_mobile": customer_mobile or "",
			"agriflow_payment_mode_extra": payment_mode,
			"agriflow_created_via": "Mobile App",
			"due_date": nowdate(),
			"is_pos": 1,
			"update_stock": 1,
			"items": _invoice_items(items),
			**_selling_defaults(company),
		}
	)

	invoice.insert(ignore_permissions=True)
	invoice.set_missing_values()
	income_account = frappe.get_cached_value("Company", company, "default_income_account")
	for row in invoice.items:
		if not row.income_account and income_account:
			row.income_account = income_account
	invoice.set_paid_amount()
	if not invoice.payments:
		invoice.append(
			"payments",
			{
				"mode_of_payment": payment_mode or "Cash",
				"amount": invoice.grand_total,
			},
		)
	invoice.save(ignore_permissions=True)
	invoice.submit()

	return {
		"name": invoice.name,
		"total": invoice.grand_total,
		"items_count": len(invoice.items),
	}


@frappe.whitelist()
def create_project_invoice(project_name, items, subsidy_amount, farmer_portion, payment_mode="Cash"):
	"""Create a Project Sale invoice linked to Farmer Project."""
	if isinstance(items, str):
		items = json.loads(items)

	project = frappe.get_doc("Farmer Project", project_name)
	farmer = project.farmer

	if not farmer:
		frappe.throw(_("Farmer not set on project"))

	customer_name = f"FARMER-{farmer}"
	if not frappe.db.exists("Customer", customer_name):
		farmer_doc = frappe.get_doc("Farmer", farmer)
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_group": "Individual",
				"territory": "India",
				"mobile_no": farmer_doc.mobile,
				"customer_type": "Individual",
			}
		)
		customer.insert(ignore_permissions=True)

	company = _default_company()
	invoice = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"company": company,
			"customer": customer_name,
			"agriflow_sale_mode": "Project Sale",
			"agriflow_farmer_project": project_name,
			"agriflow_farmer": farmer,
			"agriflow_subsidy_amount": flt(subsidy_amount),
			"agriflow_farmer_portion": flt(farmer_portion),
			"agriflow_payment_mode_extra": payment_mode,
			"agriflow_created_via": "Mobile App",
			"due_date": nowdate(),
			"items": _invoice_items(items),
			**_selling_defaults(company),
		}
	)

	invoice.insert(ignore_permissions=True)
	return {
		"name": invoice.name,
		"draft": True,
		"total": invoice.grand_total,
		"subsidy_portion": invoice.agriflow_subsidy_amount,
		"farmer_portion": invoice.agriflow_farmer_portion,
	}


@frappe.whitelist()
def list_recent_invoices(limit=20, sale_mode=None):
	"""List recent invoices for dashboard."""
	filters = {}
	if sale_mode:
		filters["agriflow_sale_mode"] = sale_mode

	return frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=[
			"name",
			"customer",
			"grand_total",
			"status",
			"agriflow_sale_mode",
			"agriflow_farmer_project",
			"agriflow_walkin_customer_name",
			"agriflow_payment_mode_extra",
			"posting_date",
			"creation",
		],
		order_by="creation desc",
		limit_page_length=limit,
	)


@frappe.whitelist()
def get_item_search(search="", limit=20):
	"""Search items for POS screen."""
	return frappe.get_all(
		"Item",
		filters={"disabled": 0, "item_name": ["like", f"%{search}%"]}
		if search
		else {"disabled": 0},
		fields=["name", "item_name", "stock_uom", "standard_rate", "image"],
		order_by="item_name",
		limit_page_length=limit,
	)


@frappe.whitelist()
def get_invoice_pdf(**kwargs):
	"""Generate PDF for sales invoice as base64.
	
	Auto-selects print format based on agriflow_sale_mode:
	- "Cash & Carry" -> Agriflow Cash and Carry
	- "Project Sale" -> Agriflow Project Sale
	- (other)        -> Standard
	"""
	import base64
	from frappe.utils.pdf import get_pdf
	
	from frappe import _
	
	# Handle parameter passing from different sources
	invoice_name = kwargs.get("invoice_name") or (frappe.form_dict or {}).get("invoice_name") or ""
	print_format = kwargs.get("print_format") or (frappe.form_dict or {}).get("print_format") or ""
	
	# Support POST with JSON body (data parameter)
	import json as _json
	if not invoice_name and frappe.request and frappe.request.data:
		try:
			body = _json.loads(frappe.request.data)
			invoice_name = body.get("invoice_name", "")
			print_format = body.get("print_format", "")
		except (ValueError, TypeError, AttributeError):
			pass
	
	if not invoice_name:
		return fail("VAL_REQUIRED_FIELD", _("invoice_name required"), http_status=400)
	
	if not frappe.db.exists("Sales Invoice", invoice_name):
		return fail("INVOICE_NOT_FOUND", _("Invoice not found"), http_status=404)
	
	if not frappe.has_permission("Sales Invoice", "read", doc=invoice_name):
		return fail("PERMISSION_DENIED", _("Not allowed"), http_status=403)
	
	# Auto-select print format based on sale mode if not explicitly provided
	if not print_format:
		sale_mode = frappe.db.get_value("Sales Invoice", invoice_name, "agriflow_sale_mode") or ""
		if sale_mode == "Project Sale":
			print_format = "Agriflow Project Sale"
		elif sale_mode == "Cash & Carry":
			print_format = "Agriflow Cash and Carry"
		else:
			print_format = "Standard"
	
	try:
		html = frappe.get_print(
			"Sales Invoice",
			invoice_name,
			print_format=print_format,
			as_pdf=False,
		)
		pdf_bytes = get_pdf(html)
		pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
		
		return success({
			"invoice_name": invoice_name,
			"pdf_base64": pdf_b64,
			"filename": f"{invoice_name}.pdf",
			"size_bytes": len(pdf_bytes),
			"print_format_used": print_format,
		})
	except Exception as exc:
		frappe.log_error(title="get_invoice_pdf", message=str(exc))
		return fail("PDF_GENERATION_FAILED", str(exc), http_status=500)
