import json
import os
import pandas as pd
from typing import Dict, Any

DB_FILE = "inventory_data.json"

class VegetableDatabase:
    def __init__(self):
        self.default_data = {
            "Ground": {
                "Potato": {"price": 30, "stock": 50},
                "Onion": {"price": 40, "stock": 30},
                "Carrot": {"price": 60, "stock": 25},
                "Radish": {"price": 35, "stock": 20},
                "Beetroot": {"price": 50, "stock": 15},
                "Sweet_Potato": {"price": 45, "stock": 20},
                "Turnip": {"price": 25, "stock": 18}
            },
            "Leafy": {
                "Spinach": {"price": 40, "stock": 15},
                "Lettuce": {"price": 80, "stock": 10},
                "Cabbage": {"price": 35, "stock": 25},
                "Cauliflower": {"price": 50, "stock": 20},
                "Broccoli": {"price": 120, "stock": 12},
                "Mint": {"price": 60, "stock": 5}
            },
            "Fruity_Veges": {
                "Tomato": {"price": 50, "stock": 30},
                "Cucumber": {"price": 35, "stock": 25},
                "Bell_Pepper": {"price": 80, "stock": 15},
                "Eggplant": {"price": 45, "stock": 20},
                "Okra": {"price": 60, "stock": 18},
                "Zucchini": {"price": 70, "stock": 12},
                "Pumpkin": {"price": 25, "stock": 40}
            },
            "Legumes": {
                "Green_Beans": {"price": 70, "stock": 20},
                "Peas": {"price": 90, "stock": 15},
                "Green_Chili": {"price": 100, "stock": 10},
                "Drumstick": {"price": 80, "stock": 12},
                "Cluster_Beans": {"price": 60, "stock": 15}
            }
        }
        self.vegetables = self.load_data()

    def load_data(self) -> Dict:
        """Load inventory from JSON file or use default."""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self.default_data
        return self.default_data

    def save_data(self):
        """Save current inventory state to JSON."""
        with open(DB_FILE, 'w') as f:
            json.dump(self.vegetables, f, indent=4)

    def get_all_vegetables(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        return self.vegetables

    def get_vegetable_by_name(self, name: str) -> Dict[str, Any]:
        for category, items in self.vegetables.items():
            if name in items:
                return {
                    "name": name,
                    "category": category,
                    **items[name]
                }
        return None

    def get_vegetables_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        return self.vegetables.get(category, {})

    def update_stock(self, vegetable_name: str, quantity_sold: float) -> bool:
        """Update stock and SAVE to file immediately."""
        for category, items in self.vegetables.items():
            if vegetable_name in items:
                if items[vegetable_name]["stock"] >= quantity_sold:
                    items[vegetable_name]["stock"] -= quantity_sold
                    self.save_data()  # Save after update
                    return True
                else:
                    return False
        return False

    def return_stock(self, vegetable_name: str, quantity: float) -> bool:
        for category, items in self.vegetables.items():
            if vegetable_name in items:
                items[vegetable_name]["stock"] += quantity
                self.save_data()  # Save after return
                return True
        return False

    def check_availability(self, vegetable_name: str, quantity: float) -> bool:
        for category, items in self.vegetables.items():
            if vegetable_name in items:
                return items[vegetable_name]["stock"] >= quantity
        return False

    def get_low_stock_items(self, threshold: float = 5.0) -> Dict[str, Dict[str, Any]]:
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
        data = []
        for category, items in self.vegetables.items():
            for name, details in items.items():
                data.append({
                    "Name": name.replace("_", " ").title(),
                    "Category": category.replace("_", " ").title(),
                    "Price (₹/kg)": details["price"],
                    "Stock (kg)": details["stock"],
                    "Value (₹)": details["price"] * details["stock"]
                })

        return pd.DataFrame(data)