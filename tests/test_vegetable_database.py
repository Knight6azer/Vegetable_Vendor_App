import os
import json
import unittest
from vegetable_database import VegetableDatabase


class TestVegetableDatabase(unittest.TestCase):
    TEST_DB_FILE = "test_inventory_unit.json"

    def setUp(self):
        if os.path.exists(self.TEST_DB_FILE):
            os.remove(self.TEST_DB_FILE)
        self.db = VegetableDatabase(db_file=self.TEST_DB_FILE)

    def tearDown(self):
        if os.path.exists(self.TEST_DB_FILE):
            try:
                os.remove(self.TEST_DB_FILE)
            except OSError:
                pass
        tmp_file = f"{self.TEST_DB_FILE}.tmp"
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass

    def test_default_initialization(self):
        all_veges = self.db.get_all_vegetables()
        self.assertIn("Ground", all_veges)
        self.assertIn("Leafy", all_veges)
        self.assertIn("Fruity_Veges", all_veges)
        self.assertIn("Legumes", all_veges)
        potato = self.db.get_vegetable_by_name("Potato")
        self.assertIsNotNone(potato)
        self.assertEqual(potato["price"], 30)
        self.assertEqual(potato["stock"], 50.0)

    def test_atomic_persistence(self):
        self.assertTrue(os.path.exists(self.TEST_DB_FILE))
        # Verify valid JSON
        with open(self.TEST_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("Ground", data)

    def test_corrupt_json_recovery(self):
        # Corrupt file on disk
        with open(self.TEST_DB_FILE, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON CONTENT !!!")

        reloaded_db = VegetableDatabase(db_file=self.TEST_DB_FILE)
        potato = reloaded_db.get_vegetable_by_name("Potato")
        self.assertIsNotNone(potato)
        self.assertEqual(potato["stock"], 50.0)

    def test_invalid_schema_recovery(self):
        # Write invalid schema (e.g. negative price)
        with open(self.TEST_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"Ground": {"Potato": {"price": -10, "stock": 50}}}, f)

        reloaded_db = VegetableDatabase(db_file=self.TEST_DB_FILE)
        potato = reloaded_db.get_vegetable_by_name("Potato")
        self.assertEqual(potato["price"], 30)

    def test_update_stock_valid(self):
        success = self.db.update_stock("Potato", 5.0)
        self.assertTrue(success)
        potato = self.db.get_vegetable_by_name("Potato")
        self.assertEqual(potato["stock"], 45.0)

        # Check persistence
        with open(self.TEST_DB_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["Ground"]["Potato"]["stock"], 45.0)

    def test_update_stock_insufficient(self):
        success = self.db.update_stock("Potato", 999.0)
        self.assertFalse(success)
        potato = self.db.get_vegetable_by_name("Potato")
        self.assertEqual(potato["stock"], 50.0)

    def test_update_stock_negative_or_zero(self):
        self.assertFalse(self.db.update_stock("Potato", 0.0))
        self.assertFalse(self.db.update_stock("Potato", -5.0))
        potato = self.db.get_vegetable_by_name("Potato")
        self.assertEqual(potato["stock"], 50.0)

    def test_return_stock_valid(self):
        self.db.update_stock("Potato", 10.0)
        self.assertTrue(self.db.return_stock("Potato", 5.0))
        potato = self.db.get_vegetable_by_name("Potato")
        self.assertEqual(potato["stock"], 45.0)

    def test_return_stock_invalid(self):
        self.assertFalse(self.db.return_stock("Potato", 0.0))
        self.assertFalse(self.db.return_stock("Potato", -3.0))

    def test_low_stock_detection(self):
        # Radish default is 20
        self.db.update_stock("Radish", 16.0)  # Remaining: 4.0 kg
        low_items = self.db.get_low_stock_items(threshold=5.0)
        self.assertIn("Radish", low_items)
        self.assertEqual(low_items["Radish"]["stock"], 4.0)

    def test_inventory_summary_dataframe(self):
        df = self.db.get_inventory_summary()
        self.assertFalse(df.empty)
        self.assertIn("Name", df.columns)
        self.assertIn("Category", df.columns)
        self.assertIn("Price (₹/kg)", df.columns)
        self.assertIn("Stock (kg)", df.columns)
        self.assertIn("Value (₹)", df.columns)
        self.assertGreater(df["Value (₹)"].sum(), 0)


if __name__ == "__main__":
    unittest.main()
