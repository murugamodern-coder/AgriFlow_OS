import sys
sys.path.insert(0, "/home/muruga/workspace/frappe-bench/apps")
import frappe
frappe.init("dev.agriflow.local")
frappe.connect()
from agriflow.scripts.seed_officers import run
result = run()
print(result)
frappe.destroy()