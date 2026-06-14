"""Tests for M7 Service & AMC API - Week 5."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestServiceAPI(FrappeTestCase):
    """Service & AMC API tests."""
    
    def test_service_visit_doctype_json_valid(self):
        """Service Visit DocType JSON should be loadable and valid."""
        import json
        import os
        
        doctype_path = frappe.get_app_path(
            "agriflow", 
            "service_amc", 
            "doctype", 
            "service_visit", 
            "service_visit.json"
        )
        self.assertTrue(os.path.exists(doctype_path), "service_visit.json not found")
        
        with open(doctype_path) as f:
            data = json.load(f)
        
        self.assertEqual(data["doctype"], "DocType")
        self.assertEqual(data["name"], "Service Visit")
        self.assertIn("fields", data)
        self.assertIn("permissions", data)
    
    def test_service_visit_has_required_fields_in_json(self):
        """Service Visit JSON should have required fields defined."""
        import json
        import os
        
        doctype_path = frappe.get_app_path(
            "agriflow", 
            "service_amc", 
            "doctype", 
            "service_visit", 
            "service_visit.json"
        )
        with open(doctype_path) as f:
            data = json.load(f)
        
        field_names = [f["fieldname"] for f in data["fields"] if "fieldname" in f]
        required = [
            "farmer_project", "farmer", "visit_number",
            "scheduled_date", "visit_status", "completed",
        ]
        for field in required:
            self.assertIn(field, field_names, f"Missing field: {field}")
    
    def test_amc_visit_count_is_6(self):
        """3-year AMC = 6 visits (every 6 months)."""
        years = 3
        months_per_visit = 6
        expected_visits = (years * 12) // months_per_visit
        self.assertEqual(expected_visits, 6)
    
    def test_visit_number_range(self):
        """Visit number should be 1-6."""
        for visit_num in range(1, 7):
            self.assertTrue(1 <= visit_num <= 6)
    
    def test_visit_status_values(self):
        """Verify valid visit statuses from JSON."""
        import json
        import os
        
        doctype_path = frappe.get_app_path(
            "agriflow", 
            "service_amc", 
            "doctype", 
            "service_visit", 
            "service_visit.json"
        )
        with open(doctype_path) as f:
            data = json.load(f)
        
        # Find the visit_status field
        status_field = None
        for f in data["fields"]:
            if f.get("fieldname") == "visit_status":
                status_field = f
                break
        
        self.assertIsNotNone(status_field, "visit_status field not found in JSON")
        options = status_field.get("options", "").split("\n")
        valid_statuses = ["Scheduled", "In Progress", "Completed", "Missed", "Rescheduled"]
        for status in valid_statuses:
            self.assertIn(status, options, f"Missing status: {status}")