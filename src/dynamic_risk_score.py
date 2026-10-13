"""
FinGuard AI - Dynamic Risk Score Engine
Computes real-time dynamic risk score (0-100) by combining:
ML Fraud Probability + Behavioral Deviation Risk + Contextual Gateway Risk.
Applies configurable weighting, policy thresholds, and transparent explainability.
"""

import sys
import logging
from typing import Dict, Any, List, Optional, Tuple

# Add project root to sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.cold_start import get_cold_start_evaluator

logger = logging.getLogger("FinGuard_DynamicRisk")


class DynamicRiskEngine:
    """
    Central Risk Aggregator and Decision Engine for FinGuard AI.
    Formula:
        Score = (ML_Score * w_ml) + (Behavioral_Score * w_beh) + (Contextual_Score * w_ctx)
    """

    def __init__(self):
        self.cold_start_evaluator = get_cold_start_evaluator()

    def compute_dynamic_risk(
        self,
        ml_score: float,
        behavioral_score: float,
        contextual_score: float,
        is_cold_start: bool = False,
        total_historical_txns: int = 10,
        custom_weights: Optional[Dict[str, float]] = None,
        custom_thresholds: Optional[Dict[str, float]] = None,
        incoming_factors: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """
        Calculates the dynamic risk score and policy decision.
        """
        # Determine weights
        if custom_weights:
            w_ml = float(custom_weights.get("ml", config.DEFAULT_WEIGHT_ML))
            w_beh = float(custom_weights.get("behavioral", config.DEFAULT_WEIGHT_BEHAVIORAL))
            w_ctx = float(custom_weights.get("contextual", config.DEFAULT_WEIGHT_CONTEXTUAL))
            total_w = w_ml + w_beh + w_ctx
            if total_w > 0:
                w_ml, w_beh, w_ctx = w_ml / total_w, w_beh / total_w, w_ctx / total_w
        elif is_cold_start:
            w_ml, w_beh, w_ctx = self.cold_start_evaluator.get_adjusted_weights(total_historical_txns)
        else:
            w_ml = config.DEFAULT_WEIGHT_ML
            w_beh = config.DEFAULT_WEIGHT_BEHAVIORAL
            w_ctx = config.DEFAULT_WEIGHT_CONTEXTUAL

        # Ensure scores are within [0, 100]
        ml_score = max(0.0, min(100.0, float(ml_score)))
        behavioral_score = max(0.0, min(100.0, float(behavioral_score)))
        contextual_score = max(0.0, min(100.0, float(contextual_score)))

        # Base weighted calculation
        c_ml = ml_score * w_ml
        c_beh = behavioral_score * w_beh
        c_ctx = contextual_score * w_ctx

        dynamic_score = c_ml + c_beh + c_ctx

        # Cross-layer corroboration: When multiple independent defense layers
        # (e.g. Behavioral and Contextual) exhibit severe alarm levels simultaneously,
        # apply multi-vector threat amplification.
        if behavioral_score >= 85.0 and contextual_score >= 75.0:
            threat_boost = 8.0
            dynamic_score = min(100.0, dynamic_score + threat_boost)
            c_beh += threat_boost * 0.5
            c_ctx += threat_boost * 0.5

        dynamic_score = round(max(0.0, min(100.0, dynamic_score)), 2)

        # Thresholds
        thresh_low = custom_thresholds.get("low", config.THRESHOLD_LOW_RISK) if custom_thresholds else config.THRESHOLD_LOW_RISK
        thresh_med = custom_thresholds.get("medium", config.THRESHOLD_MEDIUM_RISK) if custom_thresholds else config.THRESHOLD_MEDIUM_RISK

        # Assign Risk Category & Decision
        if dynamic_score < thresh_low:
            risk_level = "LOW RISK"
            decision = config.DECISION_ALLOW
            action = "Allow Transaction"
            decision_detail = "Transaction Approved: Low composite risk profile detected across all behavioral, contextual, and ML signals."
            badge_color = "green"
        elif dynamic_score < thresh_med:
            risk_level = "MEDIUM RISK"
            decision = config.DECISION_VERIFY
            action = "Request Additional Verification"
            decision_detail = "Step-up Authentication Required: Moderate anomalies detected. Prompt user for 2FA, biometric scan, or OTP challenge."
            badge_color = "orange"
        else:
            risk_level = "HIGH RISK"
            decision = config.DECISION_BLOCK
            action = "Block Transaction"
            decision_detail = "Transaction Blocked: Severe fraud risk indicators detected. Account placed on temporary security hold and escalated to fraud analyst queue."
            badge_color = "red"

        # Determine Primary Risk Driver
        contributions = {
            "Machine Learning Pattern": c_ml,
            "Behavioral Deviation": c_beh,
            "Contextual Gateway Threat": c_ctx,
        }
        primary_driver = max(contributions, key=contributions.get)

        # Aggregate explanation factors
        factors = []
        if incoming_factors:
            for source, factor_list in incoming_factors.items():
                for f in factor_list:
                    if f and f not in factors:
                        factors.append(f)

        return {
            "dynamic_risk_score": dynamic_score,
            "risk_level": risk_level,
            "decision": decision,
            "recommended_action": action,
            "decision_detail": decision_detail,
            "badge_color": badge_color,
            "primary_driver": primary_driver,
            "weights_used": {
                "ml_weight": round(w_ml, 3),
                "behavioral_weight": round(w_beh, 3),
                "contextual_weight": round(w_ctx, 3),
            },
            "component_scores": {
                "ml_risk_score": round(ml_score, 2),
                "behavioral_risk_score": round(behavioral_score, 2),
                "contextual_risk_score": round(contextual_score, 2),
            },
            "component_contributions": {
                "ml_contribution_points": round(c_ml, 2),
                "behavioral_contribution_points": round(c_beh, 2),
                "contextual_contribution_points": round(c_ctx, 2),
            },
            "thresholds_used": {
                "low_threshold": thresh_low,
                "medium_threshold": thresh_med,
            },
            "is_cold_start": is_cold_start,
            "explanation_factors": factors,
        }


# Singleton
_dynamic_risk_engine = None


def get_dynamic_risk_engine() -> DynamicRiskEngine:
    global _dynamic_risk_engine
    if _dynamic_risk_engine is None:
        _dynamic_risk_engine = DynamicRiskEngine()
    return _dynamic_risk_engine


if __name__ == "__main__":
    engine = get_dynamic_risk_engine()
    res = engine.compute_dynamic_risk(
        ml_score=85.0,
        behavioral_score=70.0,
        contextual_score=90.0,
        is_cold_start=False,
    )
    print("Dynamic Risk Result:")
    for k, v in res.items():
        print(f"  {k}: {v}")
