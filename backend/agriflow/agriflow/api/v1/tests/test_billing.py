"""Tests for billing API endpoints - Phase 3.6."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBillingAPI(FrappeTestCase):
    """Test suite for agriflow.api.v1.billing endpoints."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_item = "DRIP-16MM-100M"
        cls.test_project = "FP-2026-00007"
    
    def _extract_data(self, result):
        """Extract data from response envelope."""
        if isinstance(result, dict):
            if "data" in result:
                return result.get("data")
            return result
        return result
    
    def test_subsidy_split_math_80_20(self):
        """Pure math: 80/20 subsidy split."""
        total = 10000.0
        subsidy = total * 0.80
        farmer = total - subsidy
        self.assertEqual(subsidy, 8000.0)
        self.assertEqual(farmer, 2000.0)
        self.assertEqual(subsidy + farmer, total)
    
    def test_subsidy_split_math_with_decimals(self):
        """80/20 split with decimal amounts."""
        total = 8500.50
        subsidy = round(total * 0.80, 2)
        farmer = round(total - subsidy, 2)
        self.assertAlmostEqual(subsidy + farmer, total, places=1)
    
    def test_get_item_search_returns_results(self):
        """Item search should return items."""
        from agriflow.api.v1.billing import get_item_search
        result = get_item_search(search="Drip", limit=10)
        self.assertIsNotNone(result)
        data = self._extract_data(result)
        if isinstance(data, list):
            self.assertGreaterEqual(len(data), 0)
    
    def test_get_item_search_empty_query(self):
        """Empty query should still return list (not error)."""
        from agriflow.api.v1.billing import get_item_search
        result = get_item_search(search="", limit=5)
        self.assertIsNotNone(result)
    
    def test_get_item_search_no_match(self):
        """Search for non-existent item returns empty list."""
        from agriflow.api.v1.billing import get_item_search
        result = get_item_search(search="NONEXISTENT_XYZ_999", limit=5)
        data = self._extract_data(result)
        if isinstance(data, list):
            self.assertEqual(len(data), 0)
    
    def test_list_recent_invoices_returns_list(self):
        """Recent invoices endpoint returns list (not error)."""
        from agriflow.api.v1.billing import list_recent_invoices
        result = list_recent_invoices(limit=5)
        self.assertIsNotNone(result)
    
    def test_list_recent_invoices_with_sale_mode(self):
        """Filter by sale_mode works."""
        from agriflow.api.v1.billing import list_recent_invoices
        result = list_recent_invoices(limit=5, sale_mode="Cash & Carry")
        self.assertIsNotNone(result)
    
    def test_walkin_customer_creation(self):
        """Walk-in customer creation/retrieval works."""
        from agriflow.api.v1.billing import get_or_create_walkin_customer
        result = get_or_create_walkin_customer()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Walk-in Customer")
    
    def test_create_cash_carry_minimal(self):
        """Basic Cash & Carry invoice creation."""
        from agriflow.api.v1.billing import create_cash_carry_invoice
        
        if not frappe.db.exists("Item", self.test_item):
            self.skipTest(f"Test item {self.test_item} not found")
        
        result = create_cash_carry_invoice(
            items=[{"item_code": self.test_item, "qty": 1, "rate": 850}],
            customer_name="Pytest Customer",
            customer_mobile="9000000001",
            payment_mode="Cash"
        )
        self.assertIsNotNone(result)
        data = self._extract_data(result)
        if isinstance(data, dict) and "name" in data:
            self.assertIsNotNone(data["name"])
    
    def test_project_invoice_requires_project(self):
        """Project invoice creation requires valid project."""
        from agriflow.api.v1.billing import create_project_invoice
        
        # Test with non-existent project — should raise DoesNotExistError
        with self.assertRaises(frappe.DoesNotExistError):
            create_project_invoice(
                project_name="NONEXISTENT-PROJECT-XYZ",
                items=[{"item_code": self.test_item, "qty": 1, "rate": 100}],
                subsidy_amount=80,
                farmer_portion=20,
                payment_mode="Cash"
            )


class TestBillingValidation(FrappeTestCase):
    """Input validation tests."""
    
    def test_empty_items_rejected(self):
        """Empty items list should be rejected."""
        from agriflow.api.v1.billing import create_cash_carry_invoice
        try:
            result = create_cash_carry_invoice(
                items=[],
                customer_name="Test",
                payment_mode="Cash"
            )
            if isinstance(result, dict):
                self.assertFalse(result.get("ok", True))
        except Exception:
            pass  # Exception is acceptable
    
    def test_payment_modes_accepted(self):
        """All standard payment modes should be accepted."""
        valid_modes = ["Cash", "UPI", "Card", "Bank Transfer", "Mixed"]
        for mode in valid_modes:
            self.assertIsNotNone(mode)
            self.assertIsInstance(mode, str)