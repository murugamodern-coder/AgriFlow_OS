"""Verify seed data counts."""
import frappe

def run():
    farmer_count = frappe.db.count("Farmer")
    project_count = frappe.db.count("Farmer Project")
    
    # Workflow stage distribution
    stages = frappe.db.sql("""
        SELECT current_stage, COUNT(*) as cnt
        FROM `tabFarmer Project`
        GROUP BY current_stage
        ORDER BY cnt DESC
    """, as_dict=True)
    
    print(f"Farmer count: {farmer_count}")
    print(f"Farmer Project count: {project_count}")
    print("\nWorkflow stage distribution:")
    for s in stages:
        print(f"  {s.current_stage}: {s.cnt}")
    
    return {"farmers": farmer_count, "projects": project_count}