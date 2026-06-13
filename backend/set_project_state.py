import subprocess

cmd = [
    "/home/muruga/workspace/frappe-bench/env/bin/bench",
    "--site",
    "dev.agriflow.local",
    "execute",
    "frappe.db.set_value",
    "--args",
    '["Farmer Project", "FP-2026-00007", "workflow_state", "Quotation Generated"]',
]
proc = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", proc.stdout)
print("STDERR:\n", proc.stderr)
if proc.returncode:
    raise SystemExit(proc.returncode)
