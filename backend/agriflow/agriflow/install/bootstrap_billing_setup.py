# Copyright (c) 2026, Murugan and contributors
"""Ensure ERPNext company/warehouse defaults for billing POS tests."""

from __future__ import annotations

import frappe
from frappe.utils import getdate, nowdate


def _ensure_country_fixtures():
	if frappe.db.exists("UOM", "Nos"):
		return
	from erpnext.setup.setup_wizard.operations.install_fixtures import install

	install("India")


def _ensure_company():
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if company and frappe.db.exists("Company", company):
		return company

	from erpnext.setup.setup_wizard.operations.company_setup import create_fiscal_year_and_company

	year = getdate().year
	create_fiscal_year_and_company(
		{
			"fy_start_date": f"{year}-04-01",
			"fy_end_date": f"{year + 1}-03-31",
			"company_name": "AgriFlow",
			"company_abbr": "AF",
			"currency": "INR",
			"country": "India",
			"chart_of_accounts": "Standard",
		}
	)
	company = "AgriFlow"
	frappe.db.set_single_value("Global Defaults", "default_company", company)
	return company


def run():
	_ensure_country_fixtures()
	company = _ensure_company()
	comp = frappe.get_doc("Company", company)
	if frappe.db.count("Account", {"company": company}) < 5:
		from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts

		create_charts(company, comp.chart_of_accounts or "Standard")
		comp.reload()

	abbr = comp.abbr or "AF"
	_named_accounts = {
		"default_income_account": f"Sales - {abbr}",
		"default_expense_account": f"Cost of Goods Sold - {abbr}",
		"default_cash_account": f"Cash - {abbr}",
		"default_receivable_account": f"Debtors - {abbr}",
		"stock_received_but_not_billed": f"Stock Received But Not Billed - {abbr}",
		"default_inventory_account": f"Stock In Hand - {abbr}",
	}
	for field, account_name in _named_accounts.items():
		if comp.get(field):
			continue
		account = frappe.db.get_value("Account", account_name, "name")
		if account:
			comp.db_set(field, account)

	if not comp.cost_center:
		cost_center = frappe.db.get_value(
			"Cost Center",
			{"company": company, "cost_center_name": ("like", "Main%"), "is_group": 0},
			"name",
		)
		if cost_center:
			comp.db_set("cost_center", cost_center)

	comp.reload()
	warehouse = frappe.db.get_value(
		"Warehouse",
		{"company": company, "is_group": 0, "warehouse_name": ("like", "%Stores%")},
		"name",
	) or frappe.db.get_value(
		"Warehouse",
		{"company": company, "is_group": 0, "warehouse_type": "Stores"},
		"name",
	) or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")

	if warehouse:
		frappe.db.set_single_value("Stock Settings", "default_warehouse", warehouse)

	if not frappe.db.exists("Price List", "Standard Selling"):
		try:
			frappe.get_doc(
				{
					"doctype": "Price List",
					"price_list_name": "Standard Selling",
					"selling": 1,
					"currency": "INR",
					"enabled": 1,
				}
			).insert(ignore_permissions=True)
		except frappe.DuplicateEntryError:
			pass
	if frappe.db.exists("Price List", "Standard Selling"):
		frappe.db.set_single_value("Selling Settings", "selling_price_list", "Standard Selling")

	if frappe.db.exists("Mode of Payment", "Cash"):
		mop = frappe.get_doc("Mode of Payment", "Cash")
	else:
		mop = frappe.new_doc("Mode of Payment")
		mop.mode_of_payment = "Cash"
		mop.type = "Cash"
	cash_account = comp.default_cash_account or frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Cash", "is_group": 0},
		"name",
	)
	if cash_account and not any(row.company == company for row in mop.accounts):
		mop.set("accounts", [])
		mop.append("accounts", {"company": company, "default_account": cash_account})
		mop.save(ignore_permissions=True)

	for uom in ("Bag", "Hour"):
		if not frappe.db.exists("UOM", uom):
			frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)

	frappe.db.commit()
	print(
		"COMPANY",
		company,
		"WAREHOUSE",
		warehouse,
		"ACCOUNTS",
		frappe.db.count("Account", {"company": company}),
		"INCOME",
		comp.default_income_account,
		"CASH",
		comp.default_cash_account,
		"COST",
		comp.cost_center,
	)
	_configure_item_accounts(company, warehouse)


def _configure_item_accounts(company: str, warehouse: str | None):
	income_account = frappe.db.get_value("Company", company, "default_income_account")
	expense_account = frappe.db.get_value("Company", company, "default_expense_account")
	if not income_account:
		return
	for item_code in frappe.get_all("Item", pluck="name"):
		item = frappe.get_doc("Item", item_code)
		default_row = next((row for row in item.item_defaults if row.company == company), None)
		if default_row:
			default_row.income_account = income_account
			default_row.expense_account = expense_account
			default_row.default_warehouse = warehouse
		else:
			item.append(
				"item_defaults",
				{
					"company": company,
					"default_warehouse": warehouse,
					"income_account": income_account,
					"expense_account": expense_account,
				},
			)
		item.save(ignore_permissions=True)


def ensure_item_stock(item_codes: list[str], qty: float = 1000):
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	if not company or not warehouse:
		run()
		company = frappe.db.get_single_value("Global Defaults", "default_company")
		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

	items = []
	for code in item_codes:
		if frappe.db.get_value("Bin", {"item_code": code, "warehouse": warehouse}, "actual_qty"):
			continue
		items.append({"item_code": code, "qty": qty, "t_warehouse": warehouse, "basic_rate": 1})

	if not items:
		return

	se = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"company": company,
			"posting_date": nowdate(),
			"items": items,
		}
	)
	se.insert(ignore_permissions=True)
	se.submit()
	frappe.db.commit()
