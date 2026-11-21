import os
import unittest
from vegetable_database import VegetableDatabase
from cart_manager import CartManager
from payment_processor import PaymentProcessor
from receipt_generator import ReceiptGenerator


class TestIntegrationWorkflow(unittest.TestCase):
    INTEG_DB_FILE = "test_inventory_integ.json"

    def setUp(self):
        if os.path.exists(self.INTEG_DB_FILE):
            os.remove(self.INTEG_DB_FILE)
        self.db = VegetableDatabase(db_file=self.INTEG_DB_FILE)
        self.cart = CartManager()
        self.payment = PaymentProcessor(simulate_network_delay=False, failure_rate=0.0)
        self.receipt_gen = ReceiptGenerator()

    def tearDown(self):
        if os.path.exists(self.INTEG_DB_FILE):
            try:
                os.remove(self.INTEG_DB_FILE)
            except OSError:
                pass
        tmp = f"{self.INTEG_DB_FILE}.tmp"
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

    def test_complete_checkout_workflow(self):
        # 1. Check initial inventory
        initial_potato = self.db.get_vegetable_by_name("Potato")["stock"]
        initial_tomato = self.db.get_vegetable_by_name("Tomato")["stock"]

        # 2. Add produce to cart and deduct stock
        qty_potato = 2.0
        qty_tomato = 1.5
        self.assertTrue(self.db.update_stock("Potato", qty_potato))
        self.assertTrue(self.cart.add_item("Potato", qty_potato, 30.0, "Ground"))

        self.assertTrue(self.db.update_stock("Tomato", qty_tomato))
        self.assertTrue(self.cart.add_item("Tomato", qty_tomato, 50.0, "Fruity_Veges"))

        # Verify stock decremented
        self.assertEqual(self.db.get_vegetable_by_name("Potato")["stock"], initial_potato - qty_potato)
        self.assertEqual(self.db.get_vegetable_by_name("Tomato")["stock"], initial_tomato - qty_tomato)

        # 3. Verify cart calculations
        # Potato: 2.0 * 30 = 60.0, Tomato: 1.5 * 50 = 75.0 -> Subtotal = 135.0
        cart_items = self.cart.get_cart_items()
        totals = self.receipt_gen.calculate_totals(cart_items)
        self.assertEqual(totals["subtotal"], 135.0)
        self.assertEqual(totals["tax_amount"], 6.75)
        self.assertEqual(totals["total"], 141.75)

        # 4. Process payment
        success, msg, txn_id = self.payment.process_payment(totals["total"], "Cash")
        self.assertTrue(success)
        self.assertIsNotNone(txn_id)

        # 5. Generate receipt
        order = {
            "order_id": "ORD_INTEG_001",
            "items": cart_items,
            "total_amount": totals["total"],
            "timestamp": "2026-11-21T10:15:00",
            "payment_method": "Cash",
            "transaction_id": txn_id
        }
        receipt = self.receipt_gen.generate_receipt(order)
        self.assertIn("ORD_INTEG_001", receipt)
        self.assertIn("TOTAL AMOUNT:                          ₹   141.75", receipt)

        # 6. Clear cart
        self.cart.clear_cart()
        self.assertEqual(self.cart.get_cart_count(), 0)

        # 7. Reload DB from file to verify persistence integrity
        reloaded_db = VegetableDatabase(db_file=self.INTEG_DB_FILE)
        self.assertEqual(reloaded_db.get_vegetable_by_name("Potato")["stock"], initial_potato - qty_potato)
        self.assertEqual(reloaded_db.get_vegetable_by_name("Tomato")["stock"], initial_tomato - qty_tomato)

    def test_cart_item_removal_restores_inventory(self):
        initial_carrot = self.db.get_vegetable_by_name("Carrot")["stock"]
        qty = 4.0

        # Add to cart and deduct stock
        self.db.update_stock("Carrot", qty)
        self.cart.add_item("Carrot", qty, 60.0, "Ground")
        self.assertEqual(self.db.get_vegetable_by_name("Carrot")["stock"], initial_carrot - qty)

        # User removes Carrot from cart
        item_id = list(self.cart.get_cart_items().keys())[0]
        self.db.return_stock("Carrot", qty)
        self.cart.remove_item(item_id)

        # Stock is restored
        self.assertEqual(self.db.get_vegetable_by_name("Carrot")["stock"], initial_carrot)
        self.assertEqual(self.cart.get_cart_count(), 0)

    def test_queue_order_and_cancellation(self):
        initial_spinach = self.db.get_vegetable_by_name("Spinach")["stock"]
        qty = 3.0

        # Reserve stock and put into order queue
        self.db.update_stock("Spinach", qty)
        self.cart.add_item("Spinach", qty, 40.0, "Leafy")

        order = {
            "order_id": "ORD_QUEUE_CANCEL",
            "items": self.cart.get_cart_items(),
            "total_amount": self.cart.get_cart_total()
        }
        self.cart.clear_cart()
        order_queue = [order]

        # Vendor cancels order from queue
        cancelled = order_queue.pop(0)
        for item in cancelled["items"].values():
            self.db.return_stock(item["name"], item["quantity"])

        # Stock fully restored
        self.assertEqual(self.db.get_vegetable_by_name("Spinach")["stock"], initial_spinach)


if __name__ == "__main__":
    unittest.main()
