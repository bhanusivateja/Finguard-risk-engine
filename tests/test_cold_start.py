"""
Unit Tests for FinGuard AI - Cold Start Risk Assessment
Verifies that accounts without transaction history are evaluated properly
using contextual signals and baseline priors without automatic false blocking.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.cold_start import ColdStartEvaluator
from src.behavioral_analysis import BehavioralRiskEngine


class TestColdStartEvaluator(unittest.TestCase):

    def setUp(self):
        self.cold_evaluator = ColdStartEvaluator()
        self.beh_engine = BehavioralRiskEngine()

    def test_cold_start_detection(self):
        """Verifies accounts with < 5 transactions are flagged as cold start."""
        self.assertTrue(self.cold_evaluator.is_cold_start({"total_txns": 0}))
        self.assertTrue(self.cold_evaluator.is_cold_start({"total_txns": 4}))
        self.assertFalse(self.cold_evaluator.is_cold_start({"total_txns": 5}))
        self.assertFalse(self.cold_evaluator.is_cold_start({"total_txns": 100}))

    def test_new_user_not_automatically_blocked(self):
        """
        Verifies that a genuine new user with low amount and verified KYC
        is assigned a reasonable low-to-medium risk score rather than blocked.
        """
        user_profile = {"total_txns": 0}
        current_amount = 35.0
        contextual_data = {"account_age_days": 10, "kyc_status": "fully_verified"}

        res = self.cold_evaluator.evaluate_cold_start_behavior(
            current_amount=current_amount,
            user_profile=user_profile,
            contextual_data=contextual_data,
        )

        self.assertTrue(res["is_cold_start"])
        self.assertLess(res["cold_start_score"], 40.0, "Low-risk new user should receive modest risk score.")

    def test_high_amount_new_user_receives_elevated_scrutiny(self):
        """Verifies high first-ever transactions receive higher vigilance."""
        user_profile = {"total_txns": 0}
        current_amount = 3500.0
        contextual_data = {"account_age_days": 1, "kyc_status": "unverified"}

        res = self.cold_evaluator.evaluate_cold_start_behavior(
            current_amount=current_amount,
            user_profile=user_profile,
            contextual_data=contextual_data,
        )
        self.assertGreater(res["cold_start_score"], 65.0)

    def test_adjusted_weights_transition(self):
        """Verifies smooth transition of weights from cold-start to full behavioral history."""
        w_ml_0, w_beh_0, w_ctx_0 = self.cold_evaluator.get_adjusted_weights(0)
        self.assertAlmostEqual(w_ml_0 + w_beh_0 + w_ctx_0, 1.0, places=2)
        self.assertGreater(w_ctx_0, w_beh_0)


if __name__ == "__main__":
    unittest.main()
