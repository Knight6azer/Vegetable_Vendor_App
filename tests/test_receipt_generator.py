import unittest
from receipt_generator import ReceiptGenerator


class TestReceiptGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ReceiptGenerator(tax_rate=0.05)

    def test_calculate_totals_standard(self):
        items = {
            "1": {"name": "Potato", "quantity": 2.0, "price": 30.0},
            "2": {"name": "Tomato", "quantity": 1.0, "price": 50.0}
        }
        # Subtotal: 60 + 50 = 110.0
        # Tax: 110.0 * 0.05 = 5.50
        # Total: 115.50
        totals = self.generator.calculate_totals(items)
        self.assertEqual(totals["subtotal"], 110.0)
        self.assertEqual(totals["tax_amount"], 5.50)
        self.assertEqual(totals["total"], 115.50)

    def test_calculate_totals_fractional(self):
        items = {
            "1": {"name": "Ginger", "quantity": 0.25, "price": 120.0},
            "2": {"name": "Chili", "quantity": 0.15, "price": 100.0}
        }
        # 0.25 * 120 = 30.0, 0.15 * 100 = 15.0 -> Subtotal = 45.0
        # Tax: 45.0 * 0.05 = 2.25 -> Total = 47.25
        totals = self.generator.calculate_totals(items)
        self.assertEqual(totals["subtotal"], 45.0)
        self.assertEqual(totals["tax_amount"], 2.25)
        self.assertEqual(totals["total"], 47.25)

    def test_calculate_totals_empty(self):
        totals = self.generator.calculate_totals({})
        self.assertEqual(totals["subtotal"], 0.0)
        self.assertEqual(totals["tax_amount"], 0.0)
        self.assertEqual(totals["total"], 0.0)

    def test_sanitize_filename_traversal_prevention(self):
        safe_1 = self.generator.sanitize_filename("../../etc/passwd")
        self.assertNotIn("..", safe_1)
        self.assertNotIn("/", safe_1)
        self.assertNotIn("\\", safe_1)

        safe_2 = self.generator.sanitize_filename("ORD_20261121_120000")
        self.assertEqual(safe_2, "receipt_ORD_20261121_120000.txt")

    def test_generate_receipt_formatting(self):
        order_data = {
            "order_id": "ORD_TEST_001",
            "timestamp": "2026-11-21T10:00:00",
            "items": {
                "item_1": {"name": "Potato", "quantity": 2.0, "price": 30.0}
            },
            "payment_method": "UPI",
            "transaction_id": "SIM_TXN_9999"
        }
        receipt = self.generator.generate_receipt(order_data)
        self.assertIn("Green Valley Vegetable Market", receipt)
        self.assertIn("ORD_TEST_001", receipt)
        self.assertIn("Potato", receipt)
        self.assertIn("Subtotal:", receipt)
        self.assertIn("Tax (5% GST):", receipt)
        self.assertIn("TOTAL AMOUNT:", receipt)
        self.assertIn("Payment Method:      UPI", receipt)
        self.assertIn("Transaction ID:      SIM_TXN_9999", receipt)

    def test_generate_simple_receipt(self):
        order_data = {
            "order_id": "ORD_TEST_002",
            "items": {"1": {"name": "Tomato", "quantity": 1.0, "price": 50.0}}
        }
        simple = self.generator.generate_simple_receipt(order_data)
        self.assertIn("Order ID: ORD_TEST_002", simple)
        self.assertIn("Total Amount: ₹52.50", simple)

    def test_export_receipt_json(self):
        order_data = {"order_id": "ORD_JSON", "items": {}}
        exported = self.generator.export_receipt_data(order_data)
        self.assertIn("store_info", exported)
        self.assertIn("order_info", exported)


if __name__ == "__main__":
    unittest.main()
