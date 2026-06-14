"""Officer Network API - M8."""

from __future__ import annotations
import frappe
from frappe import _

from agriflow.api.v1.response import fail, success


@frappe.whitelist()
def list_officers(**kwargs):
    """List active officers, filterable by district/block/designation."""
    district = kwargs.get("district") or frappe.form_dict.get("district")
    block = kwargs.get("block") or frappe.form_dict.get("block")
    designation = kwargs.get("designation") or frappe.form_dict.get("designation")

    filters = {"is_active": 1}
    if district:
        filters["district"] = district
    if block:
        filters["block"] = block
    if designation:
        filters["designation"] = designation

    officers = frappe.get_all(
        "Government Officer",
        filters=filters,
        fields=["name", "officer_name", "designation", "mobile", "email",
                "office_location", "district", "block"],
        order_by="officer_name asc",
        limit=200,
    )
    return success({"count": len(officers), "officers": officers})


@frappe.whitelist()
def assign_officer_to_project(**kwargs):
    """Assign an officer to a project."""
    project = kwargs.get("project_name") or frappe.form_dict.get("project_name")
    officer = kwargs.get("officer") or frappe.form_dict.get("officer")
    role = kwargs.get("role_in_project") or frappe.form_dict.get("role_in_project") or "Other"

    if not project:
        return fail("VAL_REQUIRED", _("project_name required"), http_status=400)
    if not officer:
        return fail("VAL_REQUIRED", _("officer required"), http_status=400)

    if not frappe.db.exists("Farmer Project", project):
        return fail("NOT_FOUND", _("Project not found"), http_status=404)
    if not frappe.db.exists("Government Officer", officer):
        return fail("NOT_FOUND", _("Officer not found"), http_status=404)

    # Check duplicate
    existing = frappe.get_all(
        "Project Officer Assignment",
        filters={"farmer_project": project, "officer": officer, "role_in_project": role, "status": "Active"},
        fields=["name"],
    )
    if existing:
        return fail("DUPLICATE", _("Officer already assigned to this role"), http_status=409)

    assignment = frappe.get_doc({
        "doctype": "Project Officer Assignment",
        "farmer_project": project,
        "officer": officer,
        "role_in_project": role,
        "status": "Active",
    })
    assignment.insert(ignore_permissions=True)
    frappe.db.commit()

    return success({
        "name": assignment.name,
        "project": project,
        "officer": officer,
        "role": role,
    })


@frappe.whitelist()
def project_officers(**kwargs):
    """Get all officers assigned to a project."""
    project = kwargs.get("project_name") or frappe.form_dict.get("project_name")
    if not project:
        return fail("VAL_REQUIRED", _("project_name required"), http_status=400)

    assignments = frappe.db.sql("""
        SELECT
            poa.name, poa.role_in_project, poa.status, poa.assigned_date, poa.last_interaction,
            o.name as officer_id, o.officer_name, o.designation, o.mobile, o.office_location
        FROM `tabProject Officer Assignment` poa
        JOIN `tabGovernment Officer` o ON poa.officer = o.name
        WHERE poa.farmer_project = %s
        ORDER BY poa.assigned_date DESC
    """, project, as_dict=True)

    return success({"project": project, "count": len(assignments), "assignments": assignments})


@frappe.whitelist()
def officer_workload(**kwargs):
    """Get count of active projects per officer."""
    workload = frappe.db.sql("""
        SELECT
            o.name as officer_id, o.officer_name, o.designation, o.mobile,
            COUNT(poa.name) as active_projects
        FROM `tabGovernment Officer` o
        LEFT JOIN `tabProject Officer Assignment` poa
            ON poa.officer = o.name AND poa.status = 'Active'
        WHERE o.is_active = 1
        GROUP BY o.name
        ORDER BY active_projects DESC
        LIMIT 50
    """, as_dict=True)

    return success({"count": len(workload), "workload": workload})


@frappe.whitelist()
def update_assignment_status(**kwargs):
    """Update assignment status (Active/Completed/Reassigned/On Hold)."""
    assignment = kwargs.get("assignment_name") or frappe.form_dict.get("assignment_name")
    new_status = kwargs.get("status") or frappe.form_dict.get("status")
    notes = kwargs.get("notes") or frappe.form_dict.get("notes")

    if not assignment:
        return fail("VAL_REQUIRED", _("assignment_name required"), http_status=400)

    if not frappe.db.exists("Project Officer Assignment", assignment):
        return fail("NOT_FOUND", _("Assignment not found"), http_status=404)

    doc = frappe.get_doc("Project Officer Assignment", assignment)
    if new_status:
        doc.status = new_status
    if notes:
        doc.notes = notes
    doc.last_interaction = frappe.utils.today()
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return success({"name": assignment, "status": doc.status})