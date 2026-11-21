import re
import time
import random
from typing import Dict, Any, Tuple, Optional


class PaymentProcessor:
    """
    Simulated multi-mode Payment Gateway for local retail Point of Sale.
    Supports Cash, simulated UPI, and simulated Credit/Debit Card transactions.

    DISCLAIMER: This module is strictly a sandbox simulator for demonstration, testing,
    and workflow evaluation. It does NOT connect to real financial institutions or process
    real currency. Sensitive card details are validated syntactically and never logged or stored.
    """

    SUPPORTED_METHODS = ["Credit Card", "UPI", "Cash"]

    def __init__(self, simulate_network_delay: bool = True, failure_rate: float = 0.05, seed: Optional[int] = None):
        """
        Initialize the simulated payment processor.
        :param simulate_network_delay: If True, introduces a 1.5s delay to mimic bank network authorization.
        :param failure_rate: Probability (0.0 to 1.0) of simulated network timeout (default 5%).
        :param seed: Optional random seed for deterministic testing.
        """
        self.simulate_network_delay = simulate_network_delay
        self.failure_rate = max(0.0, min(1.0, float(failure_rate)))
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _validate_card(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Syntactic validation for simulated card payment (card number, CVV, expiry)."""
        raw_card = str(details.get("card_number", "")).strip()
        card_number = re.sub(r"[\s\-]", "", raw_card)

        if not card_number.isdigit() or len(card_number) < 12 or len(card_number) > 19:
            return False, "Invalid Card Number (must be 12-19 digits)"

        raw_cvv = str(details.get("cvv", "")).strip()
        if not raw_cvv.isdigit() or len(raw_cvv) not in (3, 4):
            return False, "Invalid CVV (must be 3 or 4 digits)"

        raw_expiry = str(details.get("expiry", "")).strip()
        if raw_expiry:
            # Expiry validation for MM/YY format
            match = re.match(r"^(0[1-9]|1[0-2])\/?([0-9]{2})$", raw_expiry)
            if not match:
                return False, "Invalid Expiry format (expected MM/YY)"
        else:
            return False, "Card expiry date is required"

        return True, "Card details validated"

    def _validate_upi(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Syntactic validation for simulated UPI ID (e.g. user@bank)."""
        raw_upi = str(details.get("upi_id", "")).strip()
        if not raw_upi:
            return False, "UPI ID is required"

        # General pattern: username@handle where username can contain letters, numbers, dots, hyphens
        upi_pattern = r"^[\w\.\-]+@[a-zA-Z0-9]+$"
        if not re.match(upi_pattern, raw_upi):
            return False, "Invalid UPI ID format (expected user@bank handle)"

        return True, "UPI details validated"

    def process_payment(self, amount: float, method: str, details: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Simulate payment processing.
        Returns: (success: bool, user_message: str, transaction_id: Optional[str])
        """
        if details is None:
            details = {}

        if method not in self.SUPPORTED_METHODS:
            return False, f"Unsupported payment method: {method}", None

        if not isinstance(amount, (int, float)) or amount <= 0:
            return False, "Transaction amount must be strictly positive", None

        # Simulate network latency for realistic interactive feel
        if self.simulate_network_delay:
            time.sleep(1.5)

        # Generate a unique simulated transaction identifier
        transaction_id = f"SIM_TXN_{int(time.time())}_{self._rng.randint(1000, 9999)}"

        if method == "Cash":
            return True, "Cash payment recorded. Please collect cash at counter.", transaction_id

        if method == "Credit Card":
            valid, msg = self._validate_card(details)
            if not valid:
                return False, msg, None

        elif method == "UPI":
            valid, msg = self._validate_upi(details)
            if not valid:
                return False, msg, None

        # Stochastic failure simulation (e.g., 5% gateway timeout)
        if self.failure_rate > 0.0 and self._rng.random() < self.failure_rate:
            return False, "Payment Gateway Timeout (Simulated network drop)", None

        return True, f"Simulated {method} payment approved.", transaction_id
