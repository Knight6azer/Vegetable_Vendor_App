import json
import re
from datetime import datetime
from typing import Dict, Any, Optional


class ReceiptGenerator:
    """
    Handles receipt formatting, tax calculations, filename sanitization,
    and structured document generation for retail orders.
    """

    def __init__(self, store_name: str = "Green Valley Vegetable Market",
                 store_address: str = "123 Market Street, Fresh City",
                 store_phone: str = "+91-9876543210",
                 tax_rate: float = 0.05):
        self.store_name = store_name
        self.store_address = store_address
        self.store_phone = store_phone
        self.tax_rate = max(0.0, float(tax_rate))  # Default 5% GST

    def calculate_totals(self, items: Dict[str, Any]) -> Dict[str, float]:
        """
        Single authoritative source of truth for subtotal, tax, and grand total calculations.
        Enforces 2-decimal financial rounding at every arithmetic step.
        """
        if not items or not isinstance(items, dict):
            return {"subtotal": 0.0, "tax_amount": 0.0, "total": 0.0}

        subtotal = 0.0
        for item in items.values():
            if not isinstance(item, dict):
                continue
            qty = max(0.0, float(item.get("quantity", 0.0)))
            price = max(0.0, float(item.get("price", 0.0)))
            subtotal += round(qty * price, 2)

        subtotal = round(subtotal, 2)
        tax_amount = round(subtotal * self.tax_rate, 2)
        total = round(subtotal + tax_amount, 2)

        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total": total
        }

    def format_currency(self, amount: float) -> str:
        """Format a numeric value into an Indian Rupee string."""
        return f"₹{float(amount):.2f}"

    def sanitize_filename(self, order_id: str) -> str:
        """
        Sanitize order IDs for safe filesystem path handling.
        Strips directory traversal, path separators, and illegal filesystem characters.
        """
        if not order_id or not isinstance(order_id, str):
            order_id = f"ORDER_{int(datetime.now().timestamp())}"
        import os
        base_name = os.path.basename(order_id.strip())
        safe_id = re.sub(r"[^\w\-]", "_", base_name)
        safe_id = re.sub(r"_+", "_", safe_id).strip("_")
        if not safe_id:
            safe_id = f"ORDER_{int(datetime.now().timestamp())}"
        return f"receipt_{safe_id}.txt"

    def generate_receipt(self, order_data: Dict[str, Any]) -> str:
        """
        Generate a standardized 50-character wide thermal receipt representation.
        Handles empty orders, missing fields, dynamic payment methods, and transaction IDs.
        """
        try:
            if not order_data or not isinstance(order_data, dict):
                return "Error: Invalid or empty order data provided."

            receipt_lines = [
                "=" * 50,
                f"{self.store_name:^50}",
                f"{self.store_address:^50}",
                f"Phone: {self.store_phone:^44}",
                "=" * 50,
                ""
            ]

            order_id = str(order_data.get("order_id", "N/A")).strip()
            timestamp = order_data.get("timestamp", datetime.now().isoformat())

            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    formatted_time = timestamp
            else:
                formatted_time = str(timestamp)

            receipt_lines.extend([
                f"Order ID: {order_id}",
                f"Date & Time: {formatted_time}",
                "Cashier: Vendor POS Terminal",
                "",
                "-" * 50,
                f"{'ITEM':<20} {'QTY':<8} {'RATE':<8} {'AMOUNT':<12}",
                "-" * 50
            ])

            items = order_data.get("items", {})
            if not isinstance(items, dict) or not items:
                receipt_lines.append(f"{'No items in order':^50}")
            else:
                for item_id, item in items.items():
                    if not isinstance(item, dict):
                        continue
                    name = str(item.get("name", "Unknown")).replace("_", " ").title()
                    quantity = float(item.get("quantity", 0.0))
                    price = float(item.get("price", 0.0))
                    amount = round(quantity * price, 2)

                    if len(name) > 18:
                        name = name[:15] + "..."

                    receipt_lines.append(
                        f"{name:<20} {quantity:<8.1f} {price:<8.0f} {amount:<12.2f}"
                    )

            totals = self.calculate_totals(items)
            subtotal = totals["subtotal"]
            tax_amount = totals["tax_amount"]
            total_amount = totals["total"]

            tax_label = f"Tax ({int(self.tax_rate * 100)}% GST):"

            receipt_lines.extend([
                "-" * 50,
                f"{'Subtotal:':<38} ₹{subtotal:>9.2f}",
                f"{tax_label:<38} ₹{tax_amount:>9.2f}",
                "=" * 50,
                f"{'TOTAL AMOUNT:':<38} ₹{total_amount:>9.2f}",
                "=" * 50,
                ""
            ])

            payment_method = str(order_data.get("payment_method", "Cash")).strip()
            receipt_lines.extend([
                f"{'Payment Method:':<20} {payment_method}",
                f"{'Amount Paid:':<20} ₹{total_amount:.2f}",
                f"{'Change:':<20} ₹0.00",
            ])

            if order_data.get("transaction_id"):
                receipt_lines.append(f"{'Transaction ID:':<20} {order_data['transaction_id']}")

            receipt_lines.extend([
                "",
                "-" * 50,
                "Thank you for shopping with us!",
                "Fresh vegetables, honest prices!",
                "",
                "* Please check items upon receipt",
                "* Perishable items cannot be returned",
                "* Have a healthy day!",
                "",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 50
            ])

            return "\n".join(receipt_lines)

        except Exception as e:
            return f"Error generating receipt: {str(e)}"

    def generate_simple_receipt(self, order_data: Dict[str, Any]) -> str:
        """Generate a concise plain-text receipt summary."""
        try:
            if not order_data or not isinstance(order_data, dict):
                return "Error: Invalid order data"

            order_id = str(order_data.get("order_id", "N/A")).strip()
            lines = [
                f"Order ID: {order_id}",
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "Items purchased:"
            ]

            items = order_data.get("items", {})
            totals = self.calculate_totals(items)

            if isinstance(items, dict):
                for item in items.values():
                    if not isinstance(item, dict):
                        continue
                    name = str(item.get("name", "Unknown")).replace("_", " ").title()
                    quantity = float(item.get("quantity", 0.0))
                    price = float(item.get("price", 0.0))
                    amount = round(quantity * price, 2)
                    lines.append(f"- {name}: {quantity} kg × ₹{price} = ₹{amount:.2f}")

            lines.extend([
                "",
                f"Subtotal: ₹{totals['subtotal']:.2f}",
                f"Tax (5%): ₹{totals['tax_amount']:.2f}",
                f"Total Amount: ₹{totals['total']:.2f}",
                "",
                "Thank you for your purchase!"
            ])

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating simple receipt: {str(e)}"

    def export_receipt_data(self, order_data: Dict[str, Any]) -> str:
        """Export structured receipt information as a JSON string."""
        receipt_data = {
            "store_info": {
                "name": self.store_name,
                "address": self.store_address,
                "phone": self.store_phone
            },
            "order_info": order_data,
            "receipt_generated_at": datetime.now().isoformat(),
            "tax_rate": self.tax_rate
        }
        return json.dumps(receipt_data, indent=2)

    def get_receipt_summary(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a structured financial summary dictionary for an order."""
        items = order_data.get("items", {}) if isinstance(order_data, dict) else {}
        totals = self.calculate_totals(items)
        item_count = len(items) if isinstance(items, dict) else 0
        total_quantity = sum(float(item.get("quantity", 0.0)) for item in items.values()) if isinstance(items, dict) else 0.0

        return {
            "order_id": order_data.get("order_id", "N/A") if isinstance(order_data, dict) else "N/A",
            "timestamp": order_data.get("timestamp", datetime.now().isoformat()) if isinstance(order_data, dict) else datetime.now().isoformat(),
            "item_count": item_count,
            "total_quantity": round(total_quantity, 2),
            "subtotal": totals["subtotal"],
            "tax_amount": totals["tax_amount"],
            "total_amount": totals["total"],
            "formatted_total": self.format_currency(totals["total"])
        }
