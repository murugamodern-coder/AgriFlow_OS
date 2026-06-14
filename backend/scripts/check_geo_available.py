import frappe

# Check what geography doctypes exist
state = frappe.db.get_value("Geo State", {"state_name": "Tamil Nadu"}, "name")
print(f"Geo State (Tamil Nadu): {state}")

# Check District doctype
districts = frappe.db.get_all("District", pluck="name", limit=20)
print(f"Districts: {districts}")

# Check Geo District
geo_districts = frappe.db.get_all("Geo District", pluck="name", limit=20)
print(f"Geo Districts: {geo_districts}")

# Check Block
blocks = frappe.db.get_all("Block", pluck="name", limit=20)
print(f"Blocks: {blocks}")

# Check Geo Block  
geo_blocks = frappe.db.get_all("Geo Block", pluck="name", limit=20)
print(f"Geo Blocks: {geo_blocks}")

# Check Village
villages = frappe.db.get_all("Village", pluck="name", limit=20)
print(f"Villages: {villages[:5]}")
print(f"Total villages: {len(villages)}")