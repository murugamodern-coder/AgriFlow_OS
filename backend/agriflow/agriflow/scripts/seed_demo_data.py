"""Seed 50 demo farmers + 20 projects across various workflow stages.

Run via: bench --site dev.agriflow.local execute agriflow.scripts.seed_demo_data.run_seed
"""

from __future__ import annotations
import frappe
import random
from datetime import datetime, timedelta


# Tamil farmer names (realistic for Tiruvannamalai region)
TAMIL_NAMES = [
    "முருகன் சாமி", "ராமச்சந்திரன்", "லட்சுமி தேவி", "கமலா ராணி", "வேலுசாமி",
    "சண்முகம் பிள்ளை", "அண்ணாமலை", "பாலகிருஷ்ணன்", "ஜெயலட்சுமி", "ரவிக்குமார்",
    "சுந்தரம் முதலியார்", "திருமூர்த்தி", "சரஸ்வதி அம்மாள்", "கதிரேசன்", "வடிவேலு",
    "ராதாகிருஷ்ணன்", "ஈஸ்வரி", "மணிகண்டன்", "ராஜேஷ் குமார்", "சாந்தி தேவி",
    "கோபால கிருஷ்ணன்", "மீனாட்சி", "சுப்ரமணியன்", "அம்பிகா", "தங்கவேலு",
    "பெருமாள் சாமி", "விஜயலட்சுமி", "காமராஜ்", "நாகராஜன்", "ஜெகதீஸ்வரன்",
    "சண்முக சுந்தரி", "ராஜாமணி", "செல்வராசு", "ஆனந்தி", "பாண்டிய ராஜா",
    "கணேசன்", "சகுந்தலா", "ராமலிங்கம்", "வசந்தா", "தேன்மொழி",
    "ஆறுமுகம்", "ஜெயராமன்", "மாலதி", "சாமிநாதன்", "புஷ்பவல்லி",
    "செல்வம்", "ராஜேந்திரன்", "மேனகா", "பழனிசாமி", "காவேரி"
]

# Stage keys for Farmer Project's current_stage Select field
STAGE_KEYS = [
    "lead_captured",
    "eligibility_check",
    "documents_collected",
    "mimis_registered",
    "field_survey",
    "quotation_generated",
    "pre_inspection_approval",
    "work_order_received",
    "material_dispatched",
    "installation_done",
    "post_inspection_approval",
    "subsidy_released",
]

# Workflow state names (must match the workflow state records in Frappe)
# These are the exact label values from the Farmer Project Workflow
WORKFLOW_STATE_LABELS = {
    "lead_captured": "Lead Captured",
    "eligibility_check": "Eligibility Check",
    "documents_collected": "Documents Collected",
    "mimis_registered": "MIMIS Registered",
    "field_survey": "Field Survey",
    "quotation_generated": "Quotation Generated",
    "pre_inspection_approval": "Pre-Inspection Approval",
    "work_order_received": "Work Order Received",
    "material_dispatched": "Material Dispatched",
    "installation_done": "Installation Done",
    "post_inspection_approval": "Post-Inspection Approval",
    "subsidy_released": "Subsidy Released",
}

SCHEMES = ["Drip Irrigation", "Mini Sprinkler", "Pumpset", "Greenhouse"]


def run_seed():
    """Main seed function."""
    print("=" * 60)
    print("AgriFlow Demo Data Seeding - 50 farmers + projects")
    print("=" * 60)

    created_farmers = []
    created_projects = []

    # ── Resolve geography ──────────────────────────────────────
    state = frappe.db.get_value("Geo State", {"state_name": "Tamil Nadu"}, "name")
    if not state:
        state = frappe.db.get_value("Geo State", {}, "name")
    if not state:
        print("✗ No Geo State found. Ensure geography fixtures are loaded.")
        return
    print(f"Using State: {state}")

    district = frappe.db.get_value("District", {"name": "593"}, "name")
    if not district:
        district = frappe.db.get_value("District", {}, "name")
    if not district:
        print("✗ No District found.")
        return
    print(f"Using District: {district}")

    block_records = frappe.db.get_all("Block", filters={"district": district}, pluck="name")
    if not block_records:
        block_records = frappe.db.get_all("Block", pluck="name")
    if not block_records:
        print("✗ No Block records found.")
        return
    selected_blocks = random.sample(block_records, min(5, len(block_records)))
    print(f"Found {len(block_records)} blocks, using {len(selected_blocks)}")

    block_village_map = {}
    for blk in selected_blocks:
        villages = frappe.db.get_all("Village", filters={"block": blk}, pluck="name")
        if villages:
            block_village_map[blk] = villages

    if not block_village_map:
        all_villages = frappe.db.get_all("Village", pluck="name")
        if all_villages:
            block_village_map = {selected_blocks[0]: all_villages}
        else:
            print("✗ No Village records found.")
            return
    print(f"Villages available across {len(block_village_map)} blocks")

    clusters = frappe.db.get_all("Cluster", pluck="name")
    default_cluster = clusters[0] if clusters else None
    if not default_cluster:
        try:
            cl = frappe.get_doc({
                "doctype": "Cluster",
                "cluster_name": "Demo Cluster",
                "block": selected_blocks[0],
            }).insert(ignore_permissions=True)
            default_cluster = cl.name
            frappe.db.commit()
        except Exception:
            try:
                default_cluster = frappe.db.get_value("Cluster", {}, "name")
            except Exception:
                default_cluster = None
    if not default_cluster:
        print("✗ No Cluster available – projects will be skipped")
    else:
        print(f"Using Cluster: {default_cluster}")

    # ── Seed farmers ───────────────────────────────────────────
    count = 0
    farmers_needing_projects = []  # (farmer_name, blk, village) for post-creation patching

    for i, tamil_name in enumerate(TAMIL_NAMES, start=1):
        try:
            prefix = random.choice(["94", "95", "96", "98", "99"])
            mobile = f"{prefix}{random.randint(10000000, 99999999)}"

            existing = frappe.db.get_value("Farmer", {"mobile": mobile})
            if existing:
                continue

            blk = random.choice(list(block_village_map.keys()))
            village = random.choice(block_village_map[blk])

            farmer = frappe.get_doc({
                "doctype": "Farmer",
                "farmer_name": tamil_name,
                "state": state,
                "district": district,
                "block": blk,
                "village": village,
                "mobile": mobile,
                "aadhaar_last4": str(random.randint(1000, 9999)),
                "language_preference": "Tamil",
                "land_extent_acres": round(random.uniform(0.5, 10.0), 2),
                "is_active": 1,
            }).insert(ignore_permissions=True)
            created_farmers.append(farmer.name)
            count += 1

            # Schedule project creation (40% chance, max 20)
            if random.random() < 0.4 and len(farmers_needing_projects) < 20 and default_cluster:
                farmers_needing_projects.append((farmer.name, tamil_name, blk, village))

            if count % 10 == 0:
                frappe.db.commit()
                print(f"  -- Committed {count} farmers --")

        except Exception as e:
            print(f"  ✗ Error creating {tamil_name}: {e}")
            frappe.db.rollback()
            continue

    frappe.db.commit()
    print(f"✅ Created {len(created_farmers)} farmers")

    # ── Seed projects (created at lead_captured, patched after) ──
    print("\n--- Seeding projects ---")
    for farmer_name, tamil_name, blk, village in farmers_needing_projects:
        try:
            scheme = random.choice(SCHEMES)
            stage = random.choice(STAGE_KEYS)
            stage_idx = STAGE_KEYS.index(stage)
            project_value = random.choice([45000, 65000, 85000, 120000, 175000])

            # Create at initial workflow state to pass validation
            project = frappe.get_doc({
                "doctype": "Farmer Project",
                "project_title": f"{scheme} - {tamil_name[:15]}",
                "farmer": farmer_name,
                "project_type": "subsidy",
                "current_stage": "lead_captured",
                "stage_sequence": 1,
                "status": "active",
                "district": district,
                "block": blk,
                "cluster": default_cluster,
                "village": village,
                "quoted_amount": project_value,
                "expected_subsidy_amount": int(project_value * 0.8),
                "started_on": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
            }).insert(ignore_permissions=True)
            frappe.db.commit()

            # Patch workflow_state and current_stage using raw SQL
            # to bypass workflow transition validation
            wf_state_label = WORKFLOW_STATE_LABELS.get(stage, "Lead Captured")
            frappe.db.sql(
                """UPDATE `tabFarmer Project`
                   SET current_stage = %s,
                       stage_sequence = %s,
                       workflow_state = %s
                   WHERE name = %s""",
                (stage, stage_idx + 1, wf_state_label, project.name),
            )
            frappe.db.commit()
            created_projects.append(project.name)
            print(f"  ✓ {project.name} [{stage}] → {farmer_name}")

        except Exception as e:
            print(f"  ✗ Error creating project for {farmer_name}: {e}")
            frappe.db.rollback()
            continue

    print("=" * 60)
    print(f"✅ Seeded {len(created_farmers)} farmers")
    print(f"✅ Seeded {len(created_projects)} projects across workflow stages")
    print("=" * 60)

    return {
        "farmers_created": len(created_farmers),
        "projects_created": len(created_projects),
        "farmer_names": created_farmers[:5],
        "project_names": created_projects[:5],
    }


def reset_demo_data():
    """Delete all demo data (use with caution!)."""
    farmers = frappe.get_all("Farmer", filters={"language_preference": "Tamil"}, pluck="name")
    print(f"Found {len(farmers)} demo farmers to delete")
    # Disabled by default - uncomment if needed
    # for f in farmers:
    #     frappe.delete_doc("Farmer", f, ignore_permissions=True, force=True)