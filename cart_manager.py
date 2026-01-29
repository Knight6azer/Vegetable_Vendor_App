import json
from typing import Dict, Any, Optional
from datetime import datetime


class CartManager:
    def __init__(self):
        self.cart_items = {}
        self.cart_id_counter = 1

    def add_item(self, name: str, quantity: float, price: float, category: str) -> bool:
        try:
            item_id = f"item_{self.cart_id_counter}"
            self.cart_id_counter += 1

            self.cart_items[item_id] = {
                "name": name,
                "quantity": quantity,
                "price": price,
                "category": category,
                "added_at": datetime.now().isoformat(),
                "subtotal": quantity * price
            }
            return True
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return False

    def remove_item(self, item_id: str) -> bool:
        try:
            if item_id in self.cart_items:
                del self.cart_items[item_id]
                return True
            return False
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            return False

    def update_quantity(self, item_id: str, new_quantity: float) -> bool:
        try:
            if item_id in self.cart_items and new_quantity > 0:
                self.cart_items[item_id]["quantity"] = new_quantity
                self.cart_items[item_id]["subtotal"] = new_quantity * self.cart_items[item_id]["price"]
                return True
            return False
        except Exception as e:
            print(f"Error updating item quantity: {e}")
            return False

    def get_cart_items(self) -> Dict[str, Dict[str, Any]]:
        return self.cart_items.copy()

    def get_cart_total(self) -> float:
        return sum(item["subtotal"] for item in self.cart_items.values())

    def get_cart_count(self) -> int:
        return len(self.cart_items)

    def clear_cart(self) -> bool:
        try:
            self.cart_items.clear()
            self.cart_id_counter = 1
            return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False

    def get_cart_summary(self) -> Dict[str, Any]:
        if not self.cart_items:
            return {
                "items": [],
                "total_items": 0,
                "total_quantity": 0,
                "total_amount": 0,
                "is_empty": True
            }

        items_summary = []
        total_quantity = 0

        for item_id, item in self.cart_items.items():
            items_summary.append({
                "id": item_id,
                "name": item["name"],
                "category": item["category"],
                "quantity": item["quantity"],
                "price": item["price"],
                "subtotal": item["subtotal"]
            })
            total_quantity += item["quantity"]

        return {
            "items": items_summary,
            "total_items": len(self.cart_items),
            "total_quantity": total_quantity,
            "total_amount": self.get_cart_total(),
            "is_empty": False
        }

    def export_cart_json(self) -> str:
        cart_data = {
            "cart_summary": self.get_cart_summary(),
            "timestamp": datetime.now().isoformat(),
            "export_type": "cart_data"
        }
        return json.dumps(cart_data, indent=2)

    def import_cart_json(self, json_data: str) -> bool:
        try:
            data = json.loads(json_data)
            if "cart_summary" in data and "items" in data["cart_summary"]:
                self.clear_cart()
                for item in data["cart_summary"]["items"]:
                    item_id = item["id"]
                    self.cart_items[item_id] = {
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "category": item["category"],
                        "added_at": datetime.now().isoformat(),
                        "subtotal": item["subtotal"]
                    }
                return True
            return False
        except Exception as e:
            print(f"Error importing cart data: {e}")
            return False

    def find_item_by_name(self, name: str) -> Optional[str]:
        for item_id, item in self.cart_items.items():
            if item["name"].lower() == name.lower():
                return item_id
        return None

    def get_items_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        category_items = {}
        for item_id, item in self.cart_items.items():
            if item["category"].lower() == category.lower():
                category_items[item_id] = item
        return category_items