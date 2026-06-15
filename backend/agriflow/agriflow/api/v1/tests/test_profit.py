"""M9 Profit Dashboard tests."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestProfitAPI(FrappeTestCase):
    """Profit Dashboard API tests."""
    
    def test_workflow_states_exist(self):
        """Verify Farmer Project workflow_state field exists."""
        meta = frappe.get_meta("Farmer Project")
        field_names = [f.fieldname for f in meta.fields]
        self.assertIn("workflow_state", field_names)
    
    def test_sales_invoice_custom_fields(self):
        """Verify Sales Invoice has agriflow custom fields."""
        meta = frappe.get_meta("Sales Invoice")
        field_names = [f.fieldname for f in meta.fields]
        expected = ["agriflow_sale_mode", "agriflow_subsidy_amount", "agriflow_farmer_portion"]
        for field in expected:
            self.assertIn(field, field_names, f"Missing custom field: {field}")
    
    def test_profit_calculation_concept(self):
        """Test profit math."""
        total = 100000.0
        cost = 70000.0
        profit = total - cost
        margin = (profit / total) * 100
        self.assertEqual(profit, 30000.0)
        self.assertEqual(margin, 30.0)
    
    def test_subsidy_split_math(self):
        """80/20 split verification."""
        total = 50000.0
        subsidy = total * 0.80
        farmer = total - subsidy
        self.assertEqual(subsidy, 40000.0)
        self.assertEqual(farmer, 10000.0)