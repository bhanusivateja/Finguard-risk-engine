"""
Unit Tests for FinGuard AI - Dynamic Risk Score Engine
Tests weight distribution, score bounds, risk level categorizations,
and custom policy threshold handling.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.dynamic_risk_score import DynamicRiskEngine


class TestDynamicRiskEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DynamicRiskEngine()

    def test_score_bounds_and_clamping(self):
        """Ensures dynamic risk score never exceeds [0, 100] bounds."""
        res_zero = self.engine.compute_dynamic_risk(ml_score=0.0, behavioral_score=0.0, contextual_score=0.0)
        self.assertEqual(res_zero["dynamic_risk_score"], 0.0)
        self.assertEqual(res_zero["risk_level"], "LOW RISK")
        self.assertEqual(res_zero["decision"], config.DECISION_ALLOW)

        res_max = self.engine.compute_dynamic_risk(ml_score=100.0, behavioral_score=100.0, contextual_score=100.0)
        self.assertEqual(res_max["dynamic_risk_score"], 100.0)
        self.assertEqual(res_max["risk_level"], "HIGH RISK")
        self.assertEqual(res_max["decision"], config.DECISION_BLOCK)

    def test_weighted_formula_calculation(self):
        """Verifies exact weighted formula: (ML * 0.40) + (Beh * 0.35) + (Ctx * 0.25)."""
        # 50 * 0.40 = 20; 60 * 0.35 = 21; 40 * 0.25 = 10 -> Expected: 51.0
        res = self.engine.compute_dynamic_risk(
            ml_score=50.0,
            behavioral_score=60.0,
            contextual_score=40.0,
            is_cold_start=False,
        )
        self.assertAlmostEqual(res["dynamic_risk_score"], 51.0, places=1)
        self.assertEqual(res["risk_level"], "MEDIUM RISK")
        self.assertEqual(res["decision"], config.DECISION_VERIFY)

    def test_threshold_transitions(self):
        """Verifies boundary thresholds (29.9 -> LOW, 30.0 -> MEDIUM, 70.0 -> HIGH)."""
        res_low = self.engine.compute_dynamic_risk(ml_score=25.0, behavioral_score=25.0, contextual_score=25.0)
        self.assertEqual(res_low["risk_level"], "LOW RISK")
        self.assertEqual(res_low["decision"], config.DECISION_ALLOW)

        res_med = self.engine.compute_dynamic_risk(ml_score=50.0, behavioral_score=50.0, contextual_score=50.0)
        self.assertEqual(res_med["risk_level"], "MEDIUM RISK")
        self.assertEqual(res_med["decision"], config.DECISION_VERIFY)

        res_high = self.engine.compute_dynamic_risk(ml_score=85.0, behavioral_score=85.0, contextual_score=85.0)
        self.assertEqual(res_high["risk_level"], "HIGH RISK")
        self.assertEqual(res_high["decision"], config.DECISION_BLOCK)

    def test_custom_configurable_weights(self):
        """Verifies that custom admin weights normalize and compute correctly."""
        custom_weights = {"ml": 0.80, "behavioral": 0.10, "contextual": 0.10}
        res = self.engine.compute_dynamic_risk(
            ml_score=100.0,
            behavioral_score=0.0,
            contextual_score=0.0,
            custom_weights=custom_weights,
        )
        self.assertAlmostEqual(res["dynamic_risk_score"], 80.0, places=1)
        self.assertEqual(res["risk_level"], "HIGH RISK")


if __name__ == "__main__":
    unittest.main()
