import unittest
from cart_manager import CartManager


class TestCartManager(unittest.TestCase):
    def setUp(self):
        self.cart = CartManager()

    def test_add_item(self):
        self.assertTrue(self.cart.add_item("Potato", 2.5, 30.0, "Ground"))
        items = self.cart.get_cart_items()
        self.assertEqual(len(items), 1)
        item = list(items.values())[0]
        self.assertEqual(item["name"], "Potato")
        self.assertEqual(item["quantity"], 2.5)
        self.assertEqual(item["price"], 30.0)
        self.assertEqual(item["subtotal"], 75.0)

    def test_duplicate_item_merges(self):
        self.assertTrue(self.cart.add_item("Potato", 2.0, 30.0, "Ground"))
        self.assertTrue(self.cart.add_item("Potato", 3.0, 30.0, "Ground"))
        items = self.cart.get_cart_items()
        self.assertEqual(len(items), 1)  # Merged into 1 line item
        item = list(items.values())[0]
        self.assertEqual(item["quantity"], 5.0)
        self.assertEqual(item["subtotal"], 150.0)
        self.assertEqual(self.cart.get_cart_total(), 150.0)

    def test_invalid_quantity_rejected(self):
        self.assertFalse(self.cart.add_item("Tomato", 0.0, 50.0, "Fruity_Veges"))
        self.assertFalse(self.cart.add_item("Tomato", -2.0, 50.0, "Fruity_Veges"))
        self.assertFalse(self.cart.add_item("Tomato", "invalid", 50.0, "Fruity_Veges"))
        self.assertEqual(self.cart.get_cart_count(), 0)

    def test_invalid_price_rejected(self):
        self.assertFalse(self.cart.add_item("Tomato", 1.0, -50.0, "Fruity_Veges"))
        self.assertFalse(self.cart.add_item("Tomato", 1.0, "invalid", "Fruity_Veges"))
        self.assertEqual(self.cart.get_cart_count(), 0)

    def test_remove_item(self):
        self.cart.add_item("Potato", 2.0, 30.0, "Ground")
        item_id = list(self.cart.get_cart_items().keys())[0]
        self.assertTrue(self.cart.remove_item(item_id))
        self.assertEqual(self.cart.get_cart_count(), 0)
        self.assertFalse(self.cart.remove_item("non_existent_id"))

    def test_update_quantity(self):
        self.cart.add_item("Potato", 2.0, 30.0, "Ground")
        item_id = list(self.cart.get_cart_items().keys())[0]
        self.assertTrue(self.cart.update_quantity(item_id, 4.0))
        item = self.cart.get_cart_items()[item_id]
        self.assertEqual(item["quantity"], 4.0)
        self.assertEqual(item["subtotal"], 120.0)
        self.assertFalse(self.cart.update_quantity(item_id, -1.0))
        self.assertFalse(self.cart.update_quantity(item_id, 0.0))

    def test_clear_cart(self):
        self.cart.add_item("Potato", 2.0, 30.0, "Ground")
        self.cart.add_item("Carrot", 1.0, 60.0, "Ground")
        self.assertEqual(self.cart.get_cart_count(), 2)
        self.assertTrue(self.cart.clear_cart())
        self.assertEqual(self.cart.get_cart_count(), 0)
        self.assertEqual(self.cart.get_cart_total(), 0.0)

    def test_fractional_precision(self):
        self.cart.add_item("Spinach", 0.35, 40.0, "Leafy")
        self.cart.add_item("Mint", 0.15, 60.0, "Leafy")
        # 0.35 * 40 = 14.0, 0.15 * 60 = 9.0 -> Total = 23.0
        self.assertEqual(self.cart.get_cart_total(), 23.0)

    def test_export_import_json(self):
        self.cart.add_item("Potato", 2.0, 30.0, "Ground")
        self.cart.add_item("Tomato", 1.5, 50.0, "Fruity_Veges")
        exported = self.cart.export_cart_json()
        new_cart = CartManager()
        self.assertTrue(new_cart.import_cart_json(exported))
        self.assertEqual(new_cart.get_cart_count(), 2)
        self.assertEqual(new_cart.get_cart_total(), self.cart.get_cart_total())

    def test_find_item_by_name(self):
        self.cart.add_item("Sweet_Potato", 1.0, 45.0, "Ground")
        self.assertIsNotNone(self.cart.find_item_by_name("sweet_potato"))
        self.assertIsNotNone(self.cart.find_item_by_name("Sweet Potato"))
        self.assertIsNone(self.cart.find_item_by_name("Pumpkin"))


if __name__ == "__main__":
    unittest.main()
