"""M9 Profit Dashboard API."""

from __future__ import annotations
import frappe
from frappe import _
from datetime import datetime, timedelta

from agriflow.api.v1.response import fail, success


@frappe.whitelist()
def daily_sales_summary(**kwargs):
    """Get sales summary for a date range."""
    from_date = kwargs.get("from_date") or frappe.form_dict.get("from_date")
    to_date = kwargs.get("to_date") or frappe.form_dict.get("to_date")
    
    if not from_date:
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    # Cash & Carry sales
    cash_carry = frappe.db.sql("""
        SELECT 
            COUNT(name) as invoice_count,
            COALESCE(SUM(grand_total), 0) as total_revenue
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s
            AND docstatus = 1
            AND agriflow_sale_mode = 'Cash & Carry'
    """, (from_date, to_date), as_dict=True)
    
    # Project Sales
    project_sales = frappe.db.sql("""
        SELECT 
            COUNT(name) as invoice_count,
            COALESCE(SUM(grand_total), 0) as total_revenue,
            COALESCE(SUM(agriflow_subsidy_amount), 0) as total_subsidy,
            COALESCE(SUM(agriflow_farmer_portion), 0) as total_farmer_portion
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s
            AND docstatus = 1
            AND agriflow_sale_mode = 'Project Sale'
    """, (from_date, to_date), as_dict=True)
    
    cc = cash_carry[0] if cash_carry else {"invoice_count": 0, "total_revenue": 0}
    ps = project_sales[0] if project_sales else {
        "invoice_count": 0, "total_revenue": 0,
        "total_subsidy": 0, "total_farmer_portion": 0
    }
    
    return success({
        "from_date": from_date,
        "to_date": to_date,
        "cash_carry": {
            "invoice_count": cc["invoice_count"],
            "total_revenue": float(cc["total_revenue"] or 0),
        },
        "project_sales": {
            "invoice_count": ps["invoice_count"],
            "total_revenue": float(ps["total_revenue"] or 0),
            "total_subsidy": float(ps["total_subsidy"] or 0),
            "total_farmer_portion": float(ps["total_farmer_portion"] or 0),
        },
        "total_invoices": cc["invoice_count"] + ps["invoice_count"],
        "total_revenue": float(cc["total_revenue"] or 0) + float(ps["total_revenue"] or 0),
    })


@frappe.whitelist()
def workflow_funnel(**kwargs):
    """Count of projects per workflow stage (funnel view)."""
    results = frappe.db.sql("""
        SELECT 
            workflow_state as stage,
            COUNT(name) as count,
            COALESCE(SUM(estimated_value), 0) as total_value
        FROM `tabFarmer Project`
        GROUP BY workflow_state
        ORDER BY count DESC
    """, as_dict=True)
    
    return success({
        "stages": [
            {
                "stage": r["stage"],
                "count": r["count"],
                "total_value": float(r["total_value"] or 0),
            }
            for r in results
        ],
        "total_projects": sum(r["count"] for r in results),
    })


@frappe.whitelist()
def scheme_performance(**kwargs):
    """Performance by scheme type."""
    results = frappe.db.sql("""
        SELECT 
            scheme_type,
            COUNT(name) as project_count,
            COALESCE(SUM(estimated_value), 0) as total_value,
            COALESCE(AVG(estimated_value), 0) as avg_value
        FROM `tabFarmer Project`
        WHERE scheme_type IS NOT NULL AND scheme_type != ''
        GROUP BY scheme_type
        ORDER BY total_value DESC
    """, as_dict=True)
    
    return success({
        "schemes": [
            {
                "scheme_type": r["scheme_type"],
                "project_count": r["project_count"],
                "total_value": float(r["total_value"] or 0),
                "avg_value": float(r["avg_value"] or 0),
            }
            for r in results
        ],
    })


@frappe.whitelist()
def top_farmers(**kwargs):
    """Top farmers by project count or value."""
    limit = int(kwargs.get("limit") or frappe.form_dict.get("limit") or 10)
    sort_by = kwargs.get("sort_by") or frappe.form_dict.get("sort_by") or "value"
    
    order_clause = "total_value DESC" if sort_by == "value" else "project_count DESC"
    
    results = frappe.db.sql(f"""
        SELECT 
            f.name, f.farmer_name, f.mobile,
            COUNT(fp.name) as project_count,
            COALESCE(SUM(fp.estimated_value), 0) as total_value
        FROM `tabFarmer` f
        LEFT JOIN `tabFarmer Project` fp ON fp.farmer = f.name
        GROUP BY f.name
        HAVING project_count > 0
        ORDER BY {order_clause}
        LIMIT %s
    """, (limit,), as_dict=True)
    
    return success({
        "farmers": [
            {
                "name": r["name"],
                "farmer_name": r["farmer_name"],
                "mobile": r["mobile"],
                "project_count": r["project_count"],
                "total_value": float(r["total_value"] or 0),
            }
            for r in results
        ],
    })


@frappe.whitelist()
def dashboard_summary(**kwargs):
    """High-level dashboard summary for owner."""
    today = datetime.now().strftime("%Y-%m-%d")
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    
    # Today's invoices
    today_count = frappe.db.count("Sales Invoice", filters={
        "posting_date": today,
        "docstatus": 1,
    })
    
    # Month's revenue
    month_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as revenue
        FROM `tabSales Invoice`
        WHERE posting_date >= %s AND docstatus = 1
    """, (month_start,), as_dict=True)
    
    # Totals
    total_farmers = frappe.db.count("Farmer")
    total_projects = frappe.db.count("Farmer Project")
    active_projects = frappe.db.count("Farmer Project", filters={
        "workflow_state": ["not in", ["Subsidy Released", "Cancelled"]]
    })
    
    # Pending service visits
    pending_visits = 0
    try:
        pending_visits = frappe.db.count("Service Visit", filters={
            "visit_status": ["in", ["Scheduled", "Rescheduled"]]
        })
    except Exception:
        pending_visits = 0
    
    return success({
        "totals": {
            "farmers": total_farmers,
            "projects": total_projects,
            "active_projects": active_projects,
            "pending_visits": pending_visits,
        },
        "today": {
            "invoice_count": today_count,
        },
        "month_to_date": {
            "revenue": float(month_revenue[0]["revenue"] or 0) if month_revenue else 0,
        },
    })