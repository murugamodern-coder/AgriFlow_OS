# Copyright (c) 2026, Murugan and contributors
"""Tiruvannamalai demo dataset — geography, officers, farmers, projects, tasks, notifications.

Run:
    bench --site <site> execute agriflow.commands.seed_demo
"""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.utils import add_days, add_months, getdate, now_datetime, today

from agriflow.project_lifecycle.services.lifecycle import ProjectLifecycleService
from agriflow.project_lifecycle.utils.stages import get_next_stage_key, get_stage_map
from agriflow.task_engine.services.lifecycle import TaskLifecycleService

DEMO_USER = "field.officer@agriflow.local"
DISTRICT = "TVM"
GEO_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "demo_geo.json"

BLOCKS = [
	("POLUR", "Polur"),
	("KALAS", "Kalasapakkam"),
	("VANDA", "Vandavasi"),
	("ARANI", "Arani"),
	("KEELN", "Keelnamulloor"),
	("ELURU", "Eluru"),
	("CHERT", "Cherthupattu"),
	("THURI", "Thurinjapuram"),
	("JAMUN", "Jamunamaruthur"),
	("SURAM", "Suram"),
	("CHEYY", "Cheyyar"),
	("CHETP", "Chetpet"),
]

VILLAGE_NAMES = [
	"Athipatti",
	"Kizhpattu",
	"Melpattu",
	"Senrayanur",
	"Thandarampattu",
]

AAO_NAMES = [
	"Suresh Kumar",
	"Ravi Chandran",
	"Murugan A.",
	"Karthik R.",
	"Prakash V.",
	"Senthil M.",
	"Ganesan P.",
	"Velmurugan S.",
	"Arun Kumar",
	"Bala Krishnan",
	"Devarajan T.",
	"Eswaran N.",
]

AHO_NAMES = [
	"Lakshmi Devi",
	"Meena Kumari",
	"Priya R.",
	"Deepa S.",
	"Kavitha M.",
	"Anitha P.",
	"Nirmala V.",
	"Revathi K.",
	"Sumathi R.",
	"Vijaya L.",
	"Malathi S.",
	"Chitra G.",
]

SUBSIDY_FARMERS = [
	{
		"name": "FR-DEMO-KUMAR",
		"farmer_name": "Kumar M.",
		"block": "BLK-POLUR",
		"village": "VIL-POL-ATHI",
		"cluster": "CLU-POL-AAO",
		"officer": "OFF-POL-AAO",
		"acres": 4,
		"tags": "VIP,drip",
		"notes": "referred_by: Murugesan",
		"target_stage": 10,
		"hero": True,
	},
	{
		"name": "FR-DEMO-RAJAN",
		"farmer_name": "Rajan P.",
		"block": "BLK-KALAS",
		"village": "VIL-KAL-01",
		"cluster": "CLU-KAL-AAO",
		"officer": "OFF-KAL-AAO",
		"acres": 2.5,
		"tags": "VIP",
		"target_stage": 12,
	},
	{
		"name": "FR-DEMO-LAKSHMI",
		"farmer_name": "Lakshmi V.",
		"block": "BLK-VANDA",
		"village": "VIL-VAN-01",
		"cluster": "CLU-VAN-AAO",
		"officer": "OFF-VAN-AAO",
		"acres": 3,
		"tags": "VIP",
		"target_stage": 10,
	},
	{
		"name": "FR-DEMO-MURUGAN",
		"farmer_name": "Murugesan K.",
		"block": "BLK-ARANI",
		"village": "VIL-ARA-01",
		"cluster": "CLU-ARA-AAO",
		"officer": "OFF-ARA-AAO",
		"acres": 5,
		"tags": "Farmer Friend",
		"target_stage": 7,
	},
	{
		"name": "FR-DEMO-SENTHIL",
		"farmer_name": "Senthil R.",
		"block": "BLK-KEELN",
		"village": "VIL-KEE-01",
		"cluster": "CLU-KEE-AAO",
		"officer": "OFF-KEE-AAO",
		"acres": 1.5,
		"tags": "Farmer Friend",
		"target_stage": 7,
	},
	{
		"name": "FR-DEMO-PALANI",
		"farmer_name": "Palaniappan S.",
		"block": "BLK-ELURU",
		"village": "VIL-ELU-01",
		"cluster": "CLU-ELU-AAO",
		"officer": "OFF-ELU-AAO",
		"acres": 2,
		"target_stage": 5,
		"blockers": ["FMB Survey-2"],
	},
	{
		"name": "FR-DEMO-VELU",
		"farmer_name": "Velu M.",
		"block": "BLK-CHERT",
		"village": "VIL-CHE-01",
		"cluster": "CLU-CHE-AAO",
		"officer": "OFF-CHE-AAO",
		"acres": 3.5,
		"target_stage": 3,
	},
	{
		"name": "FR-DEMO-GOVIND",
		"farmer_name": "Govindarajan T.",
		"block": "BLK-THURI",
		"village": "VIL-THU-01",
		"cluster": "CLU-THU-AAO",
		"officer": "OFF-THU-AAO",
		"acres": 2,
		"target_stage": 1,
	},
]

OTHER_FARMERS = [
	("FR-DEMO-RET-01", "Selvam R.", "BLK-JAMUN", "retail", 1.2),
	("FR-DEMO-RET-02", "Kannan D.", "BLK-SURAM", "retail", 2),
	("FR-DEMO-RET-03", "Mani T.", "BLK-CHEYY", "retail", 1.8),
	("FR-DEMO-RET-04", "Ponni A.", "BLK-CHETP", "retail", 2.2),
	("FR-DEMO-RET-05", "Arumugam S.", "BLK-POLUR", "retail", 1),
	("FR-DEMO-COMP-01", "Ramesh V.", "BLK-KALAS", "competitor", 3),
	("FR-DEMO-COMP-02", "Saravanan K.", "BLK-VANDA", "competitor", 2.5),
]


def execute():
	"""Entry point for bench execute agriflow.commands.seed_demo."""
	frappe.only_for("Administrator")
	frappe.set_user("Administrator")
	svc = ProjectLifecycleService()
	task_svc = TaskLifecycleService()

	_ensure_district()
	blocks = _seed_blocks()
	clusters = _seed_clusters_and_officers(blocks)
	_seed_villages(blocks, clusters)
	_ensure_demo_user(blocks)
	farmers = _seed_farmers(blocks, clusters)
	projects = _seed_projects(svc, farmers)
	tasks = _seed_tasks(task_svc, projects)
	notifications = _seed_notifications(projects)

	frappe.db.commit()
	return {
		"ok": True,
		"district": DISTRICT,
		"blocks": len(blocks),
		"clusters": len(clusters),
		"farmers": len(farmers),
		"projects": projects,
		"hero_project": projects.get("FR-DEMO-KUMAR"),
		"tasks": len(tasks),
		"notifications": notifications,
		"demo_user": DEMO_USER,
		"demo_password": "AgriFlow@2026",
	}


def _ensure_district():
	if not frappe.db.exists("District", DISTRICT):
		frappe.get_doc(
			{
				"doctype": "District",
				"name": DISTRICT,
				"district_code": DISTRICT,
				"district_name": "Tiruvannamalai",
				"state": "Tamil Nadu",
				"is_active": 1,
			}
		).insert(ignore_permissions=True)


def _seed_blocks() -> list[str]:
	names = []
	for code, block_name in BLOCKS:
		name = f"BLK-{code}"
		if frappe.db.exists("Block", name):
			names.append(name)
			continue
		frappe.get_doc(
			{
				"doctype": "Block",
				"name": name,
				"block_code": code,
				"block_name": block_name,
				"district": DISTRICT,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
		names.append(name)
	return names


def _seed_clusters_and_officers(blocks: list[str]) -> list[str]:
	cluster_names = []
	for idx, (code, _) in enumerate(BLOCKS):
		block = f"BLK-{code}"
		aao_code = f"OFF-{code}-AAO"
		aho_code = f"OFF-{code}-AHO"
		clu_aao = f"CLU-{code}-AAO"
		clu_aho = f"CLU-{code}-AHO"
		for clu_name, clu_label, off_code, off_name, dept in (
			(clu_aao, f"{code} AAO Cluster", aao_code, AAO_NAMES[idx], "agriculture"),
			(clu_aho, f"{code} AHO Cluster", aho_code, AHO_NAMES[idx], "horticulture"),
		):
			if not frappe.db.exists("Cluster", clu_name):
				frappe.get_doc(
					{
						"doctype": "Cluster",
						"name": clu_name,
						"cluster_code": clu_name,
						"cluster_name": clu_label,
						"block": block,
						"district": DISTRICT,
						"is_active": 1,
					}
				).insert(ignore_permissions=True)
			cluster_names.append(clu_name)
			_upsert_officer(off_code, off_name, dept, clu_name, mobile=f"9{800000000 + idx * 2 + (0 if dept == 'agriculture' else 1)}")
			_ensure_assignment(off_code, clu_name, block)
	return cluster_names


def _upsert_officer(code: str, name: str, department: str, cluster: str, mobile: str):
	if frappe.db.exists("Officer", code):
		frappe.db.set_value(
			"Officer",
			code,
			{"officer_name": name, "department": department, "mobile": mobile, "is_active": 1},
			update_modified=False,
		)
		return
	frappe.get_doc(
		{
			"doctype": "Officer",
			"name": code,
			"officer_code": code,
			"officer_name": name,
			"department": department,
			"mobile": mobile,
			"is_active": 1,
			"current_cluster": cluster,
		}
	).insert(ignore_permissions=True)


def _ensure_assignment(officer: str, cluster: str, block: str):
	if frappe.db.exists(
		"Officer Assignment History",
		{"officer": officer, "cluster": cluster, "valid_to": ("is", "not set")},
	):
		return
	frappe.get_doc(
		{
			"doctype": "Officer Assignment History",
			"officer": officer,
			"cluster": cluster,
			"block": block,
			"district": DISTRICT,
			"valid_from": add_months(today(), -12),
			"is_active": 1,
		}
	).insert(ignore_permissions=True)


def _seed_villages(blocks: list[str], clusters: list[str]):
	for code, _ in BLOCKS:
		block = f"BLK-{code}"
		cluster = f"CLU-{code}-AAO"
		for vidx, vname in enumerate(VILLAGE_NAMES):
			vcode = f"VIL-{code}-{vidx + 1:02d}"
			if frappe.db.exists("Village", vcode):
				continue
			frappe.get_doc(
				{
					"doctype": "Village",
					"name": vcode,
					"village_code": vcode,
					"village_name": vname if vidx == 0 else f"{vname} {vidx + 1}",
					"cluster": cluster,
					"block": block,
					"district": DISTRICT,
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
	# Hero village code override
	if not frappe.db.exists("Village", "VIL-POL-ATHI"):
		frappe.get_doc(
			{
				"doctype": "Village",
				"name": "VIL-POL-ATHI",
				"village_code": "VIL-POL-ATHI",
				"village_name": "Athipatti",
				"cluster": "CLU-POL-AAO",
				"block": "BLK-POLUR",
				"district": DISTRICT,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)


def _ensure_demo_user(blocks: list[str]):
	if not frappe.db.exists("User", DEMO_USER):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": DEMO_USER,
				"first_name": "Field",
				"last_name": "Officer",
				"send_welcome_email": 0,
				"roles": [{"role": "System Manager"}, {"role": "Field Staff"}],
			}
		)
		user.insert(ignore_permissions=True)
		user.new_password = "AgriFlow@2026"
		user.save(ignore_permissions=True)
	for block in blocks:
		if not frappe.db.exists(
			"User Permission",
			{"user": DEMO_USER, "allow": "Block", "for_value": block},
		):
			frappe.get_doc(
				{
					"doctype": "User Permission",
					"user": DEMO_USER,
					"allow": "Block",
					"for_value": block,
					"apply_to_all_doctypes": 1,
				}
			).insert(ignore_permissions=True)


def _seed_farmers(blocks: list[str], clusters: list[str]) -> list[str]:
	created = []
	for spec in SUBSIDY_FARMERS + [
		{
			"name": n,
			"farmer_name": fn,
			"block": b,
			"village": f"VIL-{b.split('-')[1]}-01",
			"cluster": f"CLU-{b.split('-')[1]}-AAO",
			"officer": f"OFF-{b.split('-')[1]}-AAO",
			"acres": ac,
			"tags": tag,
			"notes": "",
		}
		for n, fn, b, tag, ac in OTHER_FARMERS
	]:
		if frappe.db.exists("Farmer", spec["name"]):
			frappe.db.set_value(
				"Farmer",
				spec["name"],
				{
					"farmer_name": spec["farmer_name"],
					"mobile": _mobile_for(spec["name"]),
					"block": spec["block"],
					"village": spec.get("village"),
					"cluster": spec.get("cluster"),
					"district": DISTRICT,
					"land_extent_acres": spec.get("acres", 2),
					"tags": spec.get("tags", ""),
					"notes": spec.get("notes", ""),
					"is_active": 1,
				},
				update_modified=False,
			)
			created.append(spec["name"])
			continue
		frappe.get_doc(
			{
				"doctype": "Farmer",
				"name": spec["name"],
				"farmer_name": spec["farmer_name"],
				"mobile": _mobile_for(spec["name"]),
				"district": DISTRICT,
				"block": spec["block"],
				"village": spec.get("village"),
				"cluster": spec.get("cluster"),
				"land_extent_acres": spec.get("acres", 2),
				"tags": spec.get("tags", ""),
				"notes": spec.get("notes", ""),
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
		created.append(spec["name"])
	return created


def _mobile_for(key: str) -> str:
	digits = sum(ord(c) for c in key) % 100000
	return f"98765{digits:05d}"


def _seed_projects(svc: ProjectLifecycleService, farmers: list[str]) -> dict[str, str]:
	out: dict[str, str] = {}
	for spec in SUBSIDY_FARMERS:
		farmer = spec["name"]
		existing = frappe.db.get_value(
			"Farmer Project",
			{"farmer": farmer, "project_type": "subsidy", "is_deleted": 0},
			"name",
		)
		if existing:
			project_name = existing
			doc = frappe.get_doc("Farmer Project", project_name)
		else:
			remarks = _remarks(spec)
			doc = svc.create_project(
				farmer,
				block=spec["block"],
				cluster=spec["cluster"],
				village=spec["village"],
				officer=spec["officer"],
				remarks=remarks,
				created_via="seed_demo",
			)
			project_name = doc.name
		if spec.get("hero"):
			frappe.db.set_value(
				"Farmer Project",
				project_name,
				{
					"project_title": f"{spec['farmer_name']} - Athipatti · Project #1284",
					"quoted_amount": 240000,
					"mimis_registration_number": "78234",
					"work_order_number": "TN25-AB1234",
					"remarks": _remarks(spec),
				},
				update_modified=False,
			)
		_advance_to_sequence(svc, project_name, spec["target_stage"])
		out[farmer] = project_name
	return out


def _remarks(spec: dict) -> str:
	lines = []
	for b in spec.get("blockers") or []:
		lines.append(f"BLOCKER: {b}")
	return "\n".join(lines)


def _advance_to_sequence(svc: ProjectLifecycleService, project_name: str, target_sequence: int):
	project = frappe.get_doc("Farmer Project", project_name)
	while (project.stage_sequence or 1) < target_sequence:
		next_stage = get_next_stage_key(project.current_stage)
		if not next_stage:
			break
		if next_stage == "mimis_registered":
			frappe.db.set_value(
				"Farmer Project",
				project_name,
				{"mimis_gate_status": "approved", "mimis_registration_number": "78234"},
				update_modified=False,
			)
			project.reload()
		if next_stage == "quotation_generated" and not project.quoted_amount:
			frappe.db.set_value(
				"Farmer Project", project_name, {"quoted_amount": 240000}, update_modified=False
			)
			project.reload()
		svc.transition(
			project_name,
			next_stage,
			notes=f"Demo seed → {next_stage}",
			user="Administrator",
		)
		project = frappe.get_doc("Farmer Project", project_name)


def _seed_tasks(task_svc: TaskLifecycleService, projects: dict[str, str]) -> list[str]:
	created = []
	project_list = list(projects.values())
	specs = [
		("today", 0, "high"),
		("today", 0, "normal"),
		("today", 0, "normal"),
		("today", 0, "low"),
		("today", 0, "normal"),
		("overdue", -2, "high"),
		("overdue", -3, "normal"),
		("overdue", -5, "high"),
		("overdue", -1, "normal"),
		("upcoming", 3, "normal"),
		("upcoming", 5, "low"),
		("upcoming", 7, "normal"),
		("upcoming", 10, "normal"),
		("upcoming", 14, "low"),
		("upcoming", 21, "normal"),
	]
	for idx, (bucket, day_offset, priority) in enumerate(specs):
		project = project_list[idx % len(project_list)]
		client_id = f"demo-task-{bucket}-{idx}"
		if frappe.db.exists("Project Task", {"client_id": client_id, "is_deleted": 0}):
			created.append(frappe.db.get_value("Project Task", {"client_id": client_id}, "name"))
			continue
		task = task_svc.create_task(
			subject=f"Demo {bucket} — visit #{idx + 1}",
			farmer_project=project,
			task_type="field_visit",
			due_date=add_days(today(), day_offset),
			priority=priority,
			description=f"Seeded {bucket} task for demo",
			assigned_officer=DEMO_USER,
			client_id=client_id,
			auto_assign=True,
		)
		created.append(task.name)
	return created


def _seed_notifications(projects: dict[str, str]) -> int:
	hero = projects.get("FR-DEMO-KUMAR")
	if not hero:
		return 0
	block = frappe.db.get_value("Farmer Project", hero, "block")
	farmer = frappe.db.get_value("Farmer Project", hero, "farmer")
	specs = [
		("task_overdue", "notificationTaskOverdue", "Urgent: subsidy visit overdue", "high", {"tone": "urgent"}),
		("task_overdue", "notificationTaskOverdue", "Warning: document pending", "high", {"tone": "warning"}),
		("project_stage_changed", "notificationStageTransition", "Installation stage active", "normal", {"tone": "info"}),
		("manual_note", "notificationManual", "AAO Suresh added a field note", "normal", {"tone": "info"}),
		("system_alert", "notificationManual", "Cluster-7 weekly review tomorrow", "normal", {"tone": "info"}),
		("task_assigned", "notificationTaskDue", "New task: pre-inspection photos", "normal", {"tone": "info"}),
		("task_assigned", "notificationTaskDue", "Task due today — Kumar M.", "high", {"tone": "urgent"}),
		("project_stage_changed", "notificationProjectStatus", "Material dispatched for FP", "normal", {"tone": "warning"}),
		("manual_note", "notificationManual", "Murugesan referral follow-up", "low", {"tone": "info"}),
		("system_alert", "notificationSlaBreach", "SLA breach: quotation pending", "high", {"tone": "urgent"}),
	]
	count = 0
	for idx, (ntype, i18n_key, preview, priority, payload) in enumerate(specs):
		dkey = f"demo-notif-{idx}"
		if frappe.db.exists("Notification", {"delivery_key": dkey}):
			count += 1
			continue
		frappe.get_doc(
			{
				"doctype": "Notification",
				"delivery_key": dkey,
				"recipient": DEMO_USER,
				"notification_type": ntype,
				"title_i18n_key": i18n_key,
				"body_preview": preview[:140],
				"payload_json": json.dumps(payload),
				"farmer_project": hero,
				"farmer": farmer,
				"block": block,
				"district": DISTRICT,
				"priority": priority,
				"created_on": now_datetime(),
				"is_deleted": 0,
			}
		).insert(ignore_permissions=True)
		count += 1
	return count
