import json
import sys
sys.path.insert(0, "/home/muruga/workspace/frappe-bench/apps/frappe")
import frappe

frappe.init(site="dev.agriflow.local")
frappe.connect()

rows = frappe.db.sql("SELECT name, `current` FROM tabSeries ORDER BY name", as_dict=True)
print("=== tabSeries (all) ===")
print(json.dumps(rows, indent=2))
print("=== Farmer autoname ===", frappe.db.get_value("DocType", "Farmer", "autoname"))
print("=== Farmer count ===", frappe.db.count("Farmer"))
print("=== Last farmers ===", frappe.get_all("Farmer", fields=["name", "creation"], order_by="creation desc", limit=5))

try:
    status = frappe.db.sql("SHOW ENGINE INNODB STATUS", as_dict=False)
    text = status[0][2] if status else ""
    for section in ("LATEST DETECTED DEADLOCK", "TRANSACTIONS", "LOCK WAIT"):
        idx = text.find(section)
        if idx >= 0:
            print(f"\n=== INNODB STATUS: {section} ===")
            print(text[idx:idx+2500])
except Exception as e:
    print("INNODB STATUS error:", e)

frappe.destroy()
