from datetime import datetime
from typing import Dict, Any
import json


class ReceiptGenerator:
    def __init__(self):
        self.store_name = "Green Valley Vegetable Market"
        self.store_address = "123 Market Street, Fresh City"
        self.store_phone = "+91-9876543210"
        self.tax_rate = 0.05  # 5% tax

    def generate_receipt(self, order_data: Dict[str, Any]) -> str:
        try:
            receipt_lines = []

            receipt_lines.extend([
                "=" * 50,
                f"{self.store_name:^50}",
                f"{self.store_address:^50}",
                f"Phone: {self.store_phone:^44}",
                "=" * 50,
                ""
            ])

            order_id = order_data.get('order_id', 'N/A')
            timestamp = order_data.get('timestamp', datetime.now().isoformat())

            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = timestamp
            else:
                formatted_time = str(timestamp)

            receipt_lines.extend([
                f"Order ID: {order_id}",
                f"Date & Time: {formatted_time}",
                f"Cashier: Vendor System",
                "",
                "-" * 50,
                f"{'ITEM':<20} {'QTY':<8} {'RATE':<8} {'AMOUNT':<12}",
                "-" * 50
            ])

            subtotal = 0
            items = order_data.get('items', {})

            for item_id, item in items.items():
                name = item.get('name', 'Unknown').replace('_', ' ').title()
                quantity = item.get('quantity', 0)
                price = item.get('price', 0)
                amount = quantity * price
                subtotal += amount

                if len(name) > 18:
                    name = name[:15] + "..."

                receipt_lines.append(
                    f"{name:<20} {quantity:<8.1f} {price:<8.0f} {amount:<12.2f}"
                )

            tax_amount = subtotal * self.tax_rate
            total_amount = subtotal + tax_amount

            receipt_lines.extend([
                "-" * 50,
                f"{'Subtotal:':<38} ₹{subtotal:>9.2f}",
                f"{'Tax (5%):':<38} ₹{tax_amount:>9.2f}",
                "=" * 50,
                f"{'TOTAL AMOUNT:':<38} ₹{total_amount:>9.2f}",
                "=" * 50,
                ""
            ])

            receipt_lines.extend([
                f"{'Payment Method:':<20} Cash",
                f"{'Amount Paid:':<20} ₹{total_amount:.2f}",
                f"{'Change:':<20} ₹0.00",
                ""
            ])

            receipt_lines.extend([
                "-" * 50,
                "Thank you for shopping with us!",
                "Fresh vegetables, fresh prices!",
                "",
                "* Please check your items before leaving",
                "* No returns on perishable items",
                "* Have a great day!",
                "",
                f"Receipt generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 50
            ])

            return "\n".join(receipt_lines)

        except Exception as e:
            return f"Error generating receipt: {str(e)}"

    def generate_simple_receipt(self, order_data: Dict[str, Any]) -> str:
        try:
            lines = [
                f"Order ID: {order_data.get('order_id', 'N/A')}",
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "Items purchased:"
            ]

            total = 0
            items = order_data.get('items', {})

            for item in items.values():
                name = item.get('name', 'Unknown').replace('_', ' ').title()
                quantity = item.get('quantity', 0)
                price = item.get('price', 0)
                amount = quantity * price
                total += amount

                lines.append(f"- {name}: {quantity} kg × ₹{price} = ₹{amount:.2f}")

            lines.extend([
                "",
                f"Total Amount: ₹{total:.2f}",
                "",
                "Thank you for your purchase!"
            ])

            return "\n".join(lines)

        except Exception:
            return "Error generating simple receipt"

    def export_receipt_data(self, order_data: Dict[str, Any]) -> str:
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

    def calculate_totals(self, items: Dict[str, Any]) -> Dict[str, float]:
        subtotal = sum(item.get('quantity', 0) * item.get('price', 0)
                       for item in items.values())
        tax_amount = subtotal * self.tax_rate
        total = subtotal + tax_amount

        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total": total
        }

    def format_currency(self, amount: float) -> str:
        return f"₹{amount:.2f}"

    def get_receipt_summary(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        items = order_data.get('items', {})
        totals = self.calculate_totals(items)

        return {
            "order_id": order_data.get('order_id', 'N/A'),
            "timestamp": order_data.get('timestamp', datetime.now().isoformat()),
            "item_count": len(items),
            "total_quantity": sum(item.get('quantity', 0) for item in items.values()),
            "subtotal": totals["subtotal"],
            "tax_amount": totals["tax_amount"],
            "total_amount": totals["total"],
            "formatted_total": self.format_currency(totals["total"])
        }