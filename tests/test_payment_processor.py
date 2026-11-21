import unittest
from payment_processor import PaymentProcessor


class TestPaymentProcessor(unittest.TestCase):
    def setUp(self):
        # Deterministic test setup: 0 delay, 0 failure rate
        self.processor = PaymentProcessor(simulate_network_delay=False, failure_rate=0.0)

    def test_cash_payment_success(self):
        success, msg, txn_id = self.processor.process_payment(150.0, "Cash")
        self.assertTrue(success)
        self.assertIn("Cash payment recorded", msg)
        self.assertTrue(txn_id.startswith("SIM_TXN_"))

    def test_negative_or_zero_amount_rejected(self):
        success, msg, txn = self.processor.process_payment(0.0, "Cash")
        self.assertFalse(success)
        self.assertIn("strictly positive", msg)

        success, msg, txn = self.processor.process_payment(-50.0, "Cash")
        self.assertFalse(success)

    def test_unsupported_method_rejected(self):
        success, msg, txn = self.processor.process_payment(100.0, "Bitcoin")
        self.assertFalse(success)
        self.assertIn("Unsupported", msg)

    def test_card_valid(self):
        details = {
            "card_number": "4111 2222 3333 4444",
            "cvv": "123",
            "expiry": "12/28"
        }
        success, msg, txn_id = self.processor.process_payment(250.0, "Credit Card", details)
        self.assertTrue(success)
        self.assertIn("approved", msg)
        self.assertIsNotNone(txn_id)

    def test_card_invalid_number(self):
        # Too short
        details = {"card_number": "12345", "cvv": "123", "expiry": "12/28"}
        success, msg, txn = self.processor.process_payment(100.0, "Credit Card", details)
        self.assertFalse(success)
        self.assertIn("Card Number", msg)

        # Non-digits
        details["card_number"] = "4111ABCD33334444"
        success, msg, txn = self.processor.process_payment(100.0, "Credit Card", details)
        self.assertFalse(success)

    def test_card_invalid_cvv(self):
        details = {"card_number": "4111222233334444", "cvv": "1", "expiry": "12/28"}
        success, msg, txn = self.processor.process_payment(100.0, "Credit Card", details)
        self.assertFalse(success)
        self.assertIn("CVV", msg)

    def test_card_invalid_expiry(self):
        details = {"card_number": "4111222233334444", "cvv": "123", "expiry": "13/28"}  # Month 13 is invalid
        success, msg, txn = self.processor.process_payment(100.0, "Credit Card", details)
        self.assertFalse(success)
        self.assertIn("Expiry", msg)

        details["expiry"] = "invalid"
        success, msg, txn = self.processor.process_payment(100.0, "Credit Card", details)
        self.assertFalse(success)

    def test_upi_valid(self):
        details = {"upi_id": "fresh.vendor@okhdfcbank"}
        success, msg, txn_id = self.processor.process_payment(85.0, "UPI", details)
        self.assertTrue(success)
        self.assertIn("approved", msg)

    def test_upi_invalid(self):
        # Missing @
        success, msg, txn = self.processor.process_payment(85.0, "UPI", {"upi_id": "plainuser"})
        self.assertFalse(success)

        # Empty
        success, msg, txn = self.processor.process_payment(85.0, "UPI", {"upi_id": ""})
        self.assertFalse(success)

    def test_simulated_failure_rate(self):
        # 100% failure rate processor
        failing_proc = PaymentProcessor(simulate_network_delay=False, failure_rate=1.0)
        details = {"upi_id": "user@bank"}
        success, msg, txn = failing_proc.process_payment(100.0, "UPI", details)
        self.assertFalse(success)
        self.assertIn("Timeout", msg)


if __name__ == "__main__":
    unittest.main()
