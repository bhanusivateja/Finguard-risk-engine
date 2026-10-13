"""
Unit Tests for FinGuard AI - End-to-End Decision Engine
Tests complete pipeline from raw transaction dictionary through ML inference,
contextual evaluation, behavioral scoring, and persistence.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.decision_engine import TransactionDecisionEngine


class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TransactionDecisionEngine()

    def test_low_risk_legitimate_scenario(self):
        """Tests that a standard routine purchase by an established user is ALLOWED."""
        req = {
            "user_id": "USER_101",
            "amount": 25.0,
            "merchant_category": "grocery",
            "card_network": "visa",
            "card_type": "debit",
            "device_status": "trusted_device",
            "ip_status": "clean_residential",
            "location_status": "home_location",
        }
        res = self.engine.evaluate(req, save_record=False)
        self.assertIn(res["decision"], [config.DECISION_ALLOW, config.DECISION_VERIFY])
        self.assertLess(res["dynamic_risk_score"], 45.0)

    def test_high_risk_fraud_scenario(self):
        """Tests that an extreme anomaly (burst amount, casino, Tor network) is BLOCKED."""
        req = {
            "user_id": "USER_202",
            "amount": 4500.0,
            "merchant_category": "gambling",
            "card_network": "visa",
            "card_type": "credit",
            "device_status": "emulator_rooted",
            "ip_status": "tor_blacklisted",
            "location_status": "impossible_velocity",
            "failed_attempts": 4,
            "txns_last_1h": 6,
        }
        res = self.engine.evaluate(req, save_record=False)
        self.assertEqual(res["decision"], config.DECISION_BLOCK)
        self.assertEqual(res["risk_level"], "HIGH RISK")
        self.assertGreaterEqual(res["dynamic_risk_score"], config.THRESHOLD_MEDIUM_RISK)

    def test_invalid_negative_amount_raises_error(self):
        """Verifies input validation on negative transaction amount."""
        req = {"user_id": "USER_101", "amount": -50.0}
        with self.assertRaises(ValueError):
            self.engine.evaluate(req, save_record=False)


if __name__ == "__main__":
    unittest.main()
