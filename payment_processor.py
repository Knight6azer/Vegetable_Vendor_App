import time
import random

class PaymentProcessor:
    def __init__(self):
        # In a real app, this would connect to Stripe/Razorpay/Auth.net
        self.supported_methods = ["Credit Card", "UPI", "Cash"]

    def process_payment(self, amount, method, details):
        """
        Simulate processing a payment.
        Returns (success: bool, message: str, transaction_id: str)
        """
        if method not in self.supported_methods:
            return False, "Invalid payment method", None

        # Simulate network delay for effect
        time.sleep(1.5)

        # Generate a fake transaction ID
        transaction_id = f"TXN_{int(time.time())}_{random.randint(1000, 9999)}"

        if method == "Cash":
            return True, "Cash payment recorded. Please collect cash from customer.", transaction_id

        # Simulate simple validation
        if method == "Credit Card":
            if not details.get("card_number") or len(details.get("card_number")) < 12:
                return False, "Invalid Card Number", None
            if not details.get("cvv") or len(details.get("cvv")) != 3:
                return False, "Invalid CVV", None
            
        elif method == "UPI":
            if not details.get("upi_id") or "@" not in details.get("upi_id"):
                return False, "Invalid UPI ID", None

        # Randomly fail 10% of online transactions to simulate real world issues
        # (Optional: can remove this for smoother demo if desired, effectively 100% success)
        if random.random() < 0.05: 
             return False, "Payment Gateway Timeout", None

        return True, "Payment Successful", transaction_id
