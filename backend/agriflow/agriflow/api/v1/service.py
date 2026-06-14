"""Service & AMC API endpoints - M7."""

from __future__ import annotations
import frappe
from frappe import _
from datetime import datetime, timedelta

from agriflow.api.v1.response import fail, parse_data, success


@frappe.whitelist()
def schedule_amc_visits(**kwargs):
    """Auto-schedule 6 visits (every 6 months for 3 years) for a project."""
    project_name = kwargs.get("project_name") or frappe.form_dict.get("project_name")
    start_date_str = kwargs.get("start_date") or frappe.form_dict.get("start_date")
    
    if not project_name:
        return fail("VAL_REQUIRED_FIELD", _("project_name required"), http_status=400)
    
    if not frappe.db.exists("Farmer Project", project_name):
        return fail("PROJECT_NOT_FOUND", _("Project not found"), http_status=404)
    
    start_date = (
        datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if start_date_str
        else datetime.now().date()
    )
    
    project = frappe.get_doc("Farmer Project", project_name)
    
    # Check if visits already exist
    existing = frappe.get_all(
        "Service Visit",
        filters={"farmer_project": project_name},
        fields=["name"],
    )
    if existing:
        return fail("ALREADY_SCHEDULED", _(f"{len(existing)} visits already exist for this project"), http_status=409)
    
    created = []
    for visit_num in range(1, 7):  # 1 to 6
        scheduled = start_date + timedelta(days=180 * visit_num)  # Every 6 months
        
        visit = frappe.get_doc({
            "doctype": "Service Visit",
            "farmer_project": project_name,
            "farmer": project.farmer,
            "visit_number": visit_num,
            "scheduled_date": scheduled,
            "visit_status": "Scheduled",
        })
        visit.insert(ignore_permissions=True)
        created.append({"name": visit.name, "visit_number": visit_num, "scheduled_date": str(scheduled)})
    
    frappe.db.commit()
    return success({"project": project_name, "visits_created": len(created), "visits": created})


@frappe.whitelist()
def list_upcoming_visits(**kwargs):
    """List upcoming service visits (next 90 days)."""
    days_ahead = int(kwargs.get("days_ahead") or frappe.form_dict.get("days_ahead") or 90)
    technician = kwargs.get("technician") or frappe.form_dict.get("technician")
    
    cutoff = (datetime.now() + timedelta(days=days_ahead)).date()
    today = datetime.now().date()
    
    filters = {
        "scheduled_date": ["between", [today, cutoff]],
        "visit_status": ["in", ["Scheduled", "Rescheduled"]],
    }
    if technician:
        filters["technician"] = technician
    
    visits = frappe.get_all(
        "Service Visit",
        filters=filters,
        fields=[
            "name", "farmer_project", "farmer", "visit_number",
            "scheduled_date", "technician", "visit_status",
        ],
        order_by="scheduled_date asc",
        limit=100,
    )
    return success({"count": len(visits), "visits": visits})


@frappe.whitelist()
def complete_visit(**kwargs):
    """Mark visit as completed with checklist data."""
    visit_name = kwargs.get("visit_name") or frappe.form_dict.get("visit_name")
    if not visit_name:
        return fail("VAL_REQUIRED_FIELD", _("visit_name required"), http_status=400)
    
    if not frappe.db.exists("Service Visit", visit_name):
        return fail("VISIT_NOT_FOUND", _("Visit not found"), http_status=404)
    
    visit = frappe.get_doc("Service Visit", visit_name)
    
    # Update checklist fields if provided
    for field in [
        "drip_pipes_intact", "drippers_clogged", "filter_clean",
        "valve_working", "pump_motor_ok",
        "issues_found", "actions_taken", "farmer_satisfaction",
        "follow_up_required", "follow_up_date",
    ]:
        value = kwargs.get(field) or frappe.form_dict.get(field)
        if value is not None:
            visit.set(field, value)
    
    visit.completed = 1
    visit.visit_status = "Completed"
    visit.actual_visit_date = frappe.utils.today()
    visit.save(ignore_permissions=True)
    frappe.db.commit()
    
    return success({"visit": visit_name, "status": "Completed"})


@frappe.whitelist()
def farmer_service_history(**kwargs):
    """Get all service visits for a farmer."""
    farmer = kwargs.get("farmer") or frappe.form_dict.get("farmer")
    if not farmer:
        return fail("VAL_REQUIRED_FIELD", _("farmer required"), http_status=400)
    
    visits = frappe.get_all(
        "Service Visit",
        filters={"farmer": farmer},
        fields=["name", "farmer_project", "visit_number", "scheduled_date",
                "actual_visit_date", "visit_status", "completed", "technician"],
        order_by="visit_number asc",
    )
    
    completed = sum(1 for v in visits if v.get("completed"))
    return success({
        "farmer": farmer,
        "total_visits": len(visits),
        "completed_visits": completed,
        "remaining_visits": len(visits) - completed,
        "visits": visits,
    })