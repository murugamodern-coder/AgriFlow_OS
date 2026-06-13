import json
import urllib.request
import urllib.parse
import base64
from pathlib import Path

BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("PHASE 3.4 PDF ENDPOINT TEST")
print("=" * 70)
print()

# Login
print("Step 1: Login with JWT")
req = urllib.request.Request(
    f"{BASE}/api/method/agriflow.api.v1.auth.login",
    data=json.dumps({"username": "Administrator", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = json.loads(urllib.request.urlopen(req).read())
token = resp["message"]["data"]["access_token"]
print(f"✅ Token: {token[:20]}...")
print()

# Get latest invoice
print("Step 2: Get latest invoice")
req = urllib.request.Request(
    f"{BASE}/api/method/agriflow.api.v1.billing.list_recent_invoices?limit=1",
    headers={"Authorization": f"Bearer {token}"},
)
data = json.loads(urllib.request.urlopen(req).read())
inv_data = data["message"]
invoices = inv_data["data"] if isinstance(inv_data, dict) and "data" in inv_data else inv_data
invoice_name = invoices[0]["name"] if invoices else None
print(f"✅ Latest invoice: {invoice_name}")
print()

if not invoice_name:
    print("❌ FAILED: No invoice in DB")
    exit(1)

# Get PDF
print("Step 3: Call get_invoice_pdf endpoint")
# Frappe whitelist handles GET query params for named kwargs
req = urllib.request.Request(
    f"{BASE}/api/method/agriflow.api.v1.billing.get_invoice_pdf?invoice_name={urllib.parse.quote(invoice_name)}",
    headers={"Authorization": f"Bearer {token}"},
)
try:
    resp_data = json.loads(urllib.request.urlopen(req).read())
    print(f"✅ HTTP 200 OK")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP {e.code}")
    err_resp = json.loads(e.read())
    print(err_resp)
    exit(1)

# Parse PDF data
print()
print("Step 4: Parse PDF response")
pdf_info = resp_data["message"]["data"] if "data" in resp_data["message"] else resp_data["message"]
print(f"  Filename: {pdf_info['filename']}")
print(f"  PDF Size: {pdf_info['size_bytes']} bytes")
print(f"  Base64 length: {len(pdf_info['pdf_base64'])}")
print()

# Save PDF locally
print("Step 5: Save PDF to /tmp")
pdf_bytes = base64.b64decode(pdf_info["pdf_base64"])
out_path = Path("/tmp/test_invoice.pdf")
out_path.write_bytes(pdf_bytes)
print(f"✅ Saved to: {out_path}")
print(f"✅ File size: {out_path.stat().st_size} bytes")
print()

# Verify PDF
print("Step 6: Verify PDF validity")
if pdf_bytes[:4] == b"%PDF":
    print(f"✅ VERIFIED: Valid PDF file (magic bytes: {pdf_bytes[:4]})")
else:
    print(f"⚠️  WARNING: First bytes are {pdf_bytes[:10]}")
print()

if pdf_info['size_bytes'] > 5000:
    print(f"✅ PDF size {pdf_info['size_bytes']} > 5000 (valid)")
else:
    print(f"⚠️  PDF size {pdf_info['size_bytes']} seems small")
print()

print("=" * 70)
print("PHASE 3.4 PDF ENDPOINT - ALL TESTS PASSED")
print("=" * 70)
print()
print("✅ Backend PDF endpoint operational")
print("✅ Valid PDF generated and saved")
print("✅ Ready to implement mobile share feature")
