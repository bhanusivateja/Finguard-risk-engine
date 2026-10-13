"""
FinGuard AI - Cold-Start Risk Assessment Module
Evaluates new accounts and first-ever transactions when historical
behavioral data is unavailable. Adapts weight distributions and assigns
transparent, explainable neutral-prudent risk assessments.
"""

import sys
import logging
from typing import Dict, Any, Tuple

# Add project root to sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logger = logging.getLogger("FinGuard_ColdStart")


class ColdStartEvaluator:
    """
    Manages cold-start accounts (0 to 4 prior transactions).
    Applies principled baseline adjustments and dynamic weight redistribution
    so new accounts are neither unfairly penalized nor given blind approval.
    """

    def __init__(self, min_history_threshold: int = config.COLD_START_TXN_THRESHOLD):
        self.min_history_threshold = min_history_threshold
        self.default_prior = config.COLD_START_DEFAULT_PRIOR

    def is_cold_start(self, user_profile: Dict[str, Any]) -> bool:
        """Determines if user profile is within cold-start window."""
        total_txns = user_profile.get("total_txns", 0)
        return total_txns < self.min_history_threshold

    def evaluate_cold_start_behavior(
        self,
        current_amount: float,
        user_profile: Dict[str, Any],
        contextual_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculates a calibrated behavioral score for cold-start accounts.
        Combines baseline population statistics with account-onboarding context.
        """
        total_txns = user_profile.get("total_txns", 0)
        account_age_days = contextual_data.get("account_age_days", 1)
        kyc_status = str(contextual_data.get("kyc_status", "verified")).lower()

        # Start from calibrated neutral prior
        score = self.default_prior
        factors = []
        factors.append(
            f"Cold-Start Profile: New account with {total_txns} historical transactions (baseline prior: {self.default_prior:.0f})."
        )

        # First transaction amount check against standard retail thresholds
        if current_amount > 2000.0:
            score += 25.0
            factors.append(
                f"Elevated first-transaction amount (${current_amount:,.2f} > $2,000 threshold for new accounts)."
            )
        elif current_amount > 500.0:
            score += 10.0
            factors.append(
                f"Moderate first-transaction amount (${current_amount:,.2f} > $500 threshold)."
            )
        else:
            score -= 10.0
            factors.append(
                f"Conservative initial transaction amount (${current_amount:,.2f} is within low-risk onboarding range)."
            )

        # Onboarding maturity bonus/penalty
        if account_age_days < 1:
            score += 15.0
            factors.append("Immediate transaction within hours of account creation.")
        elif account_age_days > 30:
            score -= 10.0
            factors.append(f"Account aged {account_age_days} days prior to first transaction.")

        # KYC reassurance for new users
        if kyc_status in ["fully_verified", "verified", "tier_2"]:
            score -= 10.0
            factors.append("Completed KYC verification reduces cold-start uncertainty.")
        elif kyc_status in ["unverified", "none"]:
            score += 20.0
            factors.append("Unverified KYC significantly amplifies cold-start risk.")

        # Progressive blending weight for warm-up period (0 to 4 txns)
        # 0 txns: 100% cold-start weighting
        # 1-4 txns: smoothly transitions into empirical behavioral profile
        maturity_ratio = total_txns / float(self.min_history_threshold)
        final_score = max(5.0, min(95.0, score))

        return {
            "is_cold_start": True,
            "cold_start_score": round(final_score, 2),
            "total_historical_txns": total_txns,
            "maturity_ratio": round(maturity_ratio, 2),
            "factors": factors,
        }

    def get_adjusted_weights(self, total_txns: int) -> Tuple[float, float, float]:
        """
        Dynamically redistributes weights during cold-start.
        Since behavioral data is scarce, ML and Contextual signals receive higher weight.
        """
        if total_txns == 0:
            # Full cold start: 45% ML, 45% Contextual, 10% Prior
            return config.COLD_START_WEIGHT_ML, config.COLD_START_WEIGHT_PRIOR, config.COLD_START_WEIGHT_CONTEXTUAL

        # Progressive transition
        alpha = total_txns / float(self.min_history_threshold)
        w_ml = config.COLD_START_WEIGHT_ML * (1 - alpha) + config.DEFAULT_WEIGHT_ML * alpha
        w_beh = config.COLD_START_WEIGHT_PRIOR * (1 - alpha) + config.DEFAULT_WEIGHT_BEHAVIORAL * alpha
        w_ctx = config.COLD_START_WEIGHT_CONTEXTUAL * (1 - alpha) + config.DEFAULT_WEIGHT_CONTEXTUAL * alpha

        # Normalize to 1.0
        tot = w_ml + w_beh + w_ctx
        return w_ml / tot, w_beh / tot, w_ctx / tot


# Singleton
_cold_start_evaluator = None


def get_cold_start_evaluator() -> ColdStartEvaluator:
    global _cold_start_evaluator
    if _cold_start_evaluator is None:
        _cold_start_evaluator = ColdStartEvaluator()
    return _cold_start_evaluator
