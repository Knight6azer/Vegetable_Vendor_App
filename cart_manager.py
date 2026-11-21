import copy
import json
from datetime import datetime
from typing import Dict, Any, Optional


class CartManager:
    """
    Manages customer shopping cart state, operations, and financial subtotals.
    Provides deterministic duplicate item aggregation, fractional quantity precision,
    and export/import capabilities.
    """

    def __init__(self):
        self.cart_items: Dict[str, Dict[str, Any]] = {}
        self.cart_id_counter: int = 1

    def add_item(self, name: str, quantity: float, price: float, category: str) -> bool:
        """
        Add a product to the cart or aggregate quantity if already present.
        Validates that quantity and price are positive numbers and maintains 2-decimal precision.
        """
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False
        if not isinstance(price, (int, float)) or price < 0:
            return False
        if not name or not isinstance(name, str):
            return False

        try:
            qty = round(float(quantity), 2)
            unit_price = round(float(price), 2)

            existing_id = self.find_item_by_name(name)
            if existing_id:
                # Merge into existing line item
                current_qty = self.cart_items[existing_id]["quantity"]
                new_qty = round(current_qty + qty, 2)
                self.cart_items[existing_id]["quantity"] = new_qty
                self.cart_items[existing_id]["price"] = unit_price
                self.cart_items[existing_id]["subtotal"] = round(new_qty * unit_price, 2)
                return True

            item_id = f"item_{self.cart_id_counter}"
            self.cart_id_counter += 1

            self.cart_items[item_id] = {
                "name": name.strip(),
                "quantity": qty,
                "price": unit_price,
                "category": category.strip() if category else "General",
                "added_at": datetime.now().isoformat(),
                "subtotal": round(qty * unit_price, 2)
            }
            return True
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return False

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the cart by its ID."""
        try:
            if item_id in self.cart_items:
                del self.cart_items[item_id]
                return True
            return False
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            return False

    def update_quantity(self, item_id: str, new_quantity: float) -> bool:
        """Update the quantity and recompute subtotal for an existing cart item."""
        if not isinstance(new_quantity, (int, float)) or new_quantity <= 0:
            return False

        try:
            if item_id in self.cart_items:
                qty = round(float(new_quantity), 2)
                price = self.cart_items[item_id]["price"]
                self.cart_items[item_id]["quantity"] = qty
                self.cart_items[item_id]["subtotal"] = round(qty * price, 2)
                return True
            return False
        except Exception as e:
            print(f"Error updating item quantity: {e}")
            return False

    def get_cart_items(self) -> Dict[str, Dict[str, Any]]:
        """Return a copy of the active cart items dictionary."""
        return copy.deepcopy(self.cart_items)

    def get_cart_total(self) -> float:
        """Compute the grand sum of all cart line subtotals with 2-decimal precision."""
        return round(sum(item["subtotal"] for item in self.cart_items.values()), 2)

    def get_cart_count(self) -> int:
        """Return the count of distinct items in the cart."""
        return len(self.cart_items)

    def clear_cart(self) -> bool:
        """Clear all cart items and reset the counter."""
        try:
            self.cart_items.clear()
            self.cart_id_counter = 1
            return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False

    def get_cart_summary(self) -> Dict[str, Any]:
        """Return a structured summary of cart contents, item counts, total weight, and amount."""
        if not self.cart_items:
            return {
                "items": [],
                "total_items": 0,
                "total_quantity": 0.0,
                "total_amount": 0.0,
                "is_empty": True
            }

        items_summary = []
        total_quantity = 0.0

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
            "total_quantity": round(total_quantity, 2),
            "total_amount": self.get_cart_total(),
            "is_empty": False
        }

    def export_cart_json(self) -> str:
        """Serialize cart state to JSON."""
        cart_data = {
            "cart_summary": self.get_cart_summary(),
            "timestamp": datetime.now().isoformat(),
            "export_type": "cart_data"
        }
        return json.dumps(cart_data, indent=2)

    def import_cart_json(self, json_data: str) -> bool:
        """Deserialize and restore cart state from JSON with schema validation."""
        try:
            data = json.loads(json_data)
            if "cart_summary" in data and "items" in data["cart_summary"]:
                items = data["cart_summary"]["items"]
                if not isinstance(items, list):
                    return False

                self.clear_cart()
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name")
                    quantity = item.get("quantity")
                    price = item.get("price")
                    category = item.get("category", "General")
                    if name and quantity is not None and price is not None:
                        self.add_item(name, quantity, price, category)
                return True
            return False
        except Exception as e:
            print(f"Error importing cart data: {e}")
            return False

    def find_item_by_name(self, name: str) -> Optional[str]:
        """Find an existing cart item ID by case-insensitive name matching."""
        if not name or not isinstance(name, str):
            return None
        clean_target = name.strip().lower()
        for item_id, item in self.cart_items.items():
            item_name = item["name"].strip().lower()
            if item_name == clean_target or item_name.replace("_", " ") == clean_target.replace("_", " "):
                return item_id
        return None

    def get_items_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Return all cart items matching a given category name."""
        if not category or not isinstance(category, str):
            return {}
        clean_cat = category.strip().lower()
        category_items = {}
        for item_id, item in self.cart_items.items():
            if item["category"].strip().lower() == clean_cat:
                category_items[item_id] = copy.deepcopy(item)
        return category_items
