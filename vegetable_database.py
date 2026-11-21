import copy
import json
import os
import pandas as pd
from typing import Dict, Any, Optional

DB_FILE = "inventory_data.json"


class VegetableDatabase:
    """
    Data access and persistence layer for vegetable inventory management.
    Handles CRUD operations, stock adjustments, schema validation, and atomic JSON persistence.
    """

    DEFAULT_DATA: Dict[str, Dict[str, Dict[str, Any]]] = {
        "Ground": {
            "Potato": {"price": 30, "stock": 50.0},
            "Onion": {"price": 40, "stock": 30.0},
            "Carrot": {"price": 60, "stock": 25.0},
            "Radish": {"price": 35, "stock": 20.0},
            "Beetroot": {"price": 50, "stock": 15.0},
            "Sweet_Potato": {"price": 45, "stock": 20.0},
            "Turnip": {"price": 25, "stock": 18.0}
        },
        "Leafy": {
            "Spinach": {"price": 40, "stock": 15.0},
            "Lettuce": {"price": 80, "stock": 10.0},
            "Cabbage": {"price": 35, "stock": 25.0},
            "Cauliflower": {"price": 50, "stock": 20.0},
            "Broccoli": {"price": 120, "stock": 12.0},
            "Mint": {"price": 60, "stock": 5.0}
        },
        "Fruity_Veges": {
            "Tomato": {"price": 50, "stock": 30.0},
            "Cucumber": {"price": 35, "stock": 25.0},
            "Bell_Pepper": {"price": 80, "stock": 15.0},
            "Eggplant": {"price": 45, "stock": 20.0},
            "Okra": {"price": 60, "stock": 18.0},
            "Zucchini": {"price": 70, "stock": 12.0},
            "Pumpkin": {"price": 25, "stock": 40.0}
        },
        "Legumes": {
            "Green_Beans": {"price": 70, "stock": 20.0},
            "Peas": {"price": 90, "stock": 15.0},
            "Green_Chili": {"price": 100, "stock": 10.0},
            "Drumstick": {"price": 80, "stock": 12.0},
            "Cluster_Beans": {"price": 60, "stock": 15.0}
        }
    }

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.default_data = copy.deepcopy(self.DEFAULT_DATA)
        self.vegetables = self.load_data()

    def _validate_schema(self, data: Any) -> bool:
        """Validate that raw data matches the expected category -> item -> {price, stock} schema."""
        if not isinstance(data, dict) or not data:
            return False
        for category, items in data.items():
            if not isinstance(category, str) or not isinstance(items, dict):
                return False
            for item_name, details in items.items():
                if not isinstance(item_name, str) or not isinstance(details, dict):
                    return False
                if "price" not in details or "stock" not in details:
                    return False
                price = details["price"]
                stock = details["stock"]
                if not isinstance(price, (int, float)) or price < 0:
                    return False
                if not isinstance(stock, (int, float)) or stock < 0:
                    return False
        return True

    def load_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load inventory from JSON file with schema validation and automatic corruption recovery."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if self._validate_schema(data):
                    return data
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                pass

        # If file is missing or corrupted, restore defaults and write out atomically
        fallback = copy.deepcopy(self.default_data)
        self.vegetables = fallback
        self.save_data()
        return fallback

    def save_data(self) -> bool:
        """
        Save current inventory state to JSON atomically using temporary file replacement.
        Guarantees that power loss or mid-write crashes never leave a corrupt JSON file.
        """
        temp_file = f"{self.db_file}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.vegetables, f, indent=4)
            os.replace(temp_file, self.db_file)
            return True
        except OSError:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            return False

    def get_all_vegetables(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Return the complete inventory dictionary."""
        return self.vegetables

    def get_vegetable_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up a vegetable by exact name (case-sensitive or normalized)."""
        clean_name = name.strip()
        for category, items in self.vegetables.items():
            if clean_name in items:
                return {
                    "name": clean_name,
                    "category": category,
                    **items[clean_name]
                }
            # Case-insensitive / normalized lookup fallback
            for item_key, details in items.items():
                if (item_key.lower() == clean_name.lower() or
                        item_key.replace("_", " ").lower() == clean_name.replace("_", " ").lower()):
                    return {
                        "name": item_key,
                        "category": category,
                        **details
                    }
        return None

    def get_vegetables_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Return all items within a specific category."""
        return self.vegetables.get(category, {})

    def update_stock(self, vegetable_name: str, quantity_sold: float) -> bool:
        """
        Deduct stock when an item is added to cart or sold.
        Validates quantity bounds (> 0) and prevents negative stock.
        """
        if not isinstance(quantity_sold, (int, float)) or quantity_sold <= 0:
            return False

        target = self.get_vegetable_by_name(vegetable_name)
        if not target:
            return False

        cat = target["category"]
        exact_name = target["name"]
        current_stock = self.vegetables[cat][exact_name]["stock"]

        if current_stock >= quantity_sold:
            self.vegetables[cat][exact_name]["stock"] = round(current_stock - float(quantity_sold), 2)
            self.save_data()
            return True
        return False

    def return_stock(self, vegetable_name: str, quantity: float) -> bool:
        """
        Restore stock when an item is removed from cart or an order is cancelled.
        Validates that quantity is strictly positive.
        """
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False

        target = self.get_vegetable_by_name(vegetable_name)
        if not target:
            return False

        cat = target["category"]
        exact_name = target["name"]
        current_stock = self.vegetables[cat][exact_name]["stock"]
        self.vegetables[cat][exact_name]["stock"] = round(current_stock + float(quantity), 2)
        self.save_data()
        return True

    def check_availability(self, vegetable_name: str, quantity: float) -> bool:
        """Check whether requested quantity is available in stock."""
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False
        target = self.get_vegetable_by_name(vegetable_name)
        if not target:
            return False
        return target["stock"] >= quantity

    def get_low_stock_items(self, threshold: float = 5.0) -> Dict[str, Dict[str, Any]]:
        """Identify items with stock below the specified alert threshold."""
        low_stock = {}
        for category, items in self.vegetables.items():
            for name, details in items.items():
                if details["stock"] < threshold:
                    low_stock[name] = {
                        "category": category,
                        **details
                    }
        return low_stock

    def get_inventory_summary(self) -> pd.DataFrame:
        """Generate a clean pandas DataFrame summary for analytics and reporting."""
        columns = ["Name", "Category", "Price (₹/kg)", "Stock (kg)", "Value (₹)"]
        data = []
        for category, items in self.vegetables.items():
            for name, details in items.items():
                price = float(details["price"])
                stock = float(details["stock"])
                data.append({
                    "Name": name.replace("_", " ").title(),
                    "Category": category.replace("_", " ").title(),
                    "Price (₹/kg)": round(price, 2),
                    "Stock (kg)": round(stock, 2),
                    "Value (₹)": round(price * stock, 2)
                })

        if not data:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(data)
