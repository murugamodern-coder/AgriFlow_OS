import frappe
import json

def run():
    farmers = frappe.db.sql("SELECT name, farmer_name, district, block, village FROM tabFarmer LIMIT 5", as_dict=True)
    print("Existing farmers:")
    for f in farmers:
        print(f"  {f['name']}: district={f['district']}, block={f['block']}, village={f['village']}")
    
    dists = frappe.db.sql("SELECT name FROM tabDistrict LIMIT 10", as_dict=True)
    print(f"\nDistricts ({len(dists)}):")
    for d in dists:
        print(f"  {d['name']}")
    
    blocks = frappe.db.sql("SELECT name, district FROM tabBlock LIMIT 10", as_dict=True)
    print(f"\nBlocks ({len(blocks)}):")
    for b in blocks:
        print(f"  {b['name']} -> district={b['district']}")
    
    villages = frappe.db.sql("SELECT name, block FROM tabVillage LIMIT 10", as_dict=True)
    print(f"\nVillages ({len(villages)}):")
    for v in villages:
        print(f"  {v['name']} -> block={v['block']}")
    
    # Also check the doctype definition to see the Link target
    print("\n--- Checking Geo District doctype ---")
    geo_districts = frappe.db.sql("SELECT name, district_name FROM `tabGeo District` LIMIT 10", as_dict=True)
    for g in geo_districts:
        print(f"  {g['name']}: {g.get('district_name', 'N/A')}")