import frappe

districts = frappe.get_all("Geo District", fields=["name", "district_name", "district_code"], limit_page_length=10)
print("Districts:", districts)

blocks = frappe.get_all("Geo Block", fields=["name", "block_name", "block_code"], limit_page_length=10)
print("Blocks:", blocks)

villages = frappe.get_all("Geo Village", fields=["name", "village_name"], limit_page_length=10)
print("Villages:", villages)