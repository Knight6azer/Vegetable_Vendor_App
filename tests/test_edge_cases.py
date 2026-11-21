import os
import unittest
from vegetable_database import VegetableDatabase
from cart_manager import CartManager
from payment_processor import PaymentProcessor
from receipt_generator import ReceiptGenerator


class TestEdgeCases(unittest.TestCase):
    EDGE_DB_FILE = "test_inventory_edge.json"

    def setUp(self):
        if os.path.exists(self.EDGE_DB_FILE):
            os.remove(self.EDGE_DB_FILE)
        self.db = VegetableDatabase(db_file=self.EDGE_DB_FILE)
        self.cart = CartManager()
        self.payment = PaymentProcessor(simulate_network_delay=False, failure_rate=0.0)
        self.receipt_gen = ReceiptGenerator()

    def tearDown(self):
        if os.path.exists(self.EDGE_DB_FILE):
            try:
                os.remove(self.EDGE_DB_FILE)
            except OSError:
                pass
        tmp = f"{self.EDGE_DB_FILE}.tmp"
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

    def test_zero_quantity_rejected(self):
        self.assertFalse(self.db.update_stock("Potato", 0.0))
        self.assertFalse(self.cart.add_item("Potato", 0.0, 30.0, "Ground"))

    def test_negative_quantity_rejected(self):
        self.assertFalse(self.db.update_stock("Potato", -5.0))
        self.assertFalse(self.cart.add_item("Potato", -5.0, 30.0, "Ground"))

    def test_quantity_exceeding_stock(self):
        current_stock = self.db.get_vegetable_by_name("Mint")["stock"]  # 5.0 kg
        self.assertFalse(self.db.update_stock("Mint", current_stock + 0.1))
        self.assertFalse(self.db.check_availability("Mint", current_stock + 0.1))

    def test_exact_stock_exhaustion(self):
        current_stock = self.db.get_vegetable_by_name("Mint")["stock"]  # 5.0 kg
        self.assertTrue(self.db.update_stock("Mint", current_stock))
        self.assertEqual(self.db.get_vegetable_by_name("Mint")["stock"], 0.0)
        # Further purchases must fail
        self.assertFalse(self.db.update_stock("Mint", 0.5))

    def test_fractional_steps_precision(self):
        # 0.1 kg increments
        self.assertTrue(self.cart.add_item("Green_Chili", 0.1, 100.0, "Legumes"))
        self.assertTrue(self.cart.add_item("Green_Chili", 0.2, 100.0, "Legumes"))
        items = self.cart.get_cart_items()
        item = list(items.values())[0]
        self.assertEqual(item["quantity"], 0.3)
        self.assertEqual(item["subtotal"], 30.0)

    def test_special_characters_in_names(self):
        self.assertTrue(self.cart.add_item("Bell_Pepper (Organic / Fresh)", 1.0, 80.0, "Fruity_Veges"))
        order = {
            "order_id": "ORD_SPECIAL_CHARS_#%&",
            "items": self.cart.get_cart_items(),
            "payment_method": "Cash"
        }
        receipt = self.receipt_gen.generate_receipt(order)
        self.assertIn("Bell Pepper", receipt)
        safe_fname = self.receipt_gen.sanitize_filename(order["order_id"])
        self.assertNotIn("%", safe_fname)
        self.assertNotIn("&", safe_fname)
        self.assertNotIn("#", safe_fname)

    def test_empty_order_receipt_generation(self):
        receipt = self.receipt_gen.generate_receipt({})
        self.assertIn("Error", receipt)

        receipt2 = self.receipt_gen.generate_receipt({"order_id": "ORD_EMPTY", "items": {}})
        self.assertIn("No items in order", receipt2)
        self.assertIn("TOTAL AMOUNT:                          ₹     0.00", receipt2)


if __name__ == "__main__":
    unittest.main()
