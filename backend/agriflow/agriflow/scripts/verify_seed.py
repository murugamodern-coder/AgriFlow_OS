"""Verify seed data counts."""
import frappe


def run():
    farmer_count = frappe.db.count("Farmer")
    project_count = frappe.db.count("Farmer Project")
    try:
        invoice_count = frappe.db.count("Sales Invoice")
    except Exception:
        invoice_count = "N/A (table missing)"
    try:
        service_count = frappe.db.count("Service Visit")
    except Exception:
        service_count = "N/A (table missing)"

    print(f"Farmer count:            {farmer_count}")
    print(f"Farmer Project count:    {project_count}")
    print(f"Sales Invoice count:     {invoice_count}")
    print(f"Service Visit count:     {service_count}")

    # Project stage distribution
    stages = frappe.db.sql(
        """SELECT current_stage, COUNT(*) as cnt
           FROM `tabFarmer Project`
           GROUP BY current_stage
           ORDER BY cnt DESC""",
        as_dict=True,
    )
    print("\nProject stage distribution:")
    for s in stages:
        print(f"  {s['current_stage']}: {s['cnt']}")