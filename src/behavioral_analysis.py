"""
FinGuard AI - Behavioral Risk Analysis Engine
Calculates transaction risk based on historical user spending deviations,
transaction velocity, failed authentication attempts, and abnormal timing.
Seamlessly integrates Cold-Start fallback for new accounts.
"""

import sys
import logging
from typing import Dict, Any, List

# Add project root to sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.cold_start import get_cold_start_evaluator

logger = logging.getLogger("FinGuard_Behavioral")


class BehavioralRiskEngine:
    """
    Evaluates real-time deviations from an individual user's established baseline.
    """

    def __init__(self):
        self.cold_start_evaluator = get_cold_start_evaluator()

    def evaluate_behavioral_risk(
        self,
        current_txn: Dict[str, Any],
        user_profile: Dict[str, Any],
        contextual_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Main behavioral evaluation method.
        Returns:
            {
                "behavioral_risk_score": float (0-100),
                "is_cold_start": bool,
                "factors": list[str],
                "details": dict
            }
        """
        contextual_data = contextual_data or {}
        amount = float(current_txn.get("amount", current_txn.get("TransactionAmt", 0.0)))
        total_txns = user_profile.get("total_txns", 0)

        # 1. Cold-Start Check
        if self.cold_start_evaluator.is_cold_start(user_profile):
            cold_res = self.cold_start_evaluator.evaluate_cold_start_behavior(
                current_amount=amount,
                user_profile=user_profile,
                contextual_data=contextual_data,
            )
            return {
                "behavioral_risk_score": cold_res["cold_start_score"],
                "is_cold_start": True,
                "factors": cold_res["factors"],
                "details": {
                    "total_historical_txns": total_txns,
                    "mode": "cold_start",
                    "maturity_ratio": cold_res["maturity_ratio"],
                },
            }

        # 2. Established Account Behavioral Scoring
        score = 0.0
        factors: List[str] = []

        avg_amount = float(user_profile.get("avg_amount", 50.0))
        std_amount = float(user_profile.get("std_amount", 20.0))
        std_amount = max(std_amount, 5.0)  # Avoid division by zero
        max_historical_amount = float(user_profile.get("max_amount", avg_amount * 2.0))

        # A. Amount Deviation (Z-score & Multiple of Average)
        z_score = (amount - avg_amount) / std_amount
        multiplier = amount / max(avg_amount, 1.0)

        if amount > max_historical_amount * 2.5:
            score += 40.0
            factors.append(
                f"Severe spending surge: ${amount:,.2f} is more than 2.5x the user's all-time record (${max_historical_amount:,.2f}) (Z-score: +{z_score:.1f})."
            )
        elif multiplier >= 4.0:
            score += 30.0
            factors.append(
                f"Abnormal amount deviation: Transaction is {multiplier:.1f}x higher than user average (${avg_amount:,.2f}) (Z-score: +{z_score:.1f})."
            )
        elif multiplier >= 2.2 or z_score >= 2.5:
            score += 15.0
            factors.append(
                f"Moderate amount deviation: {multiplier:.1f}x above typical average spending (${avg_amount:,.2f})."
            )
        elif multiplier <= 1.2 and z_score <= 1.0:
            score += 0.0
            factors.append(
                f"Consistent spending amount: ${amount:,.2f} matches historical profile (avg: ${avg_amount:,.2f})."
            )

        # B. Transaction Frequency / Velocity
        txns_1h = int(user_profile.get("txns_last_1h", current_txn.get("txns_last_1h", 0)))
        txns_24h = int(user_profile.get("txns_last_24h", current_txn.get("txns_last_24h", 1)))

        if txns_1h >= 5:
            score += 35.0
            factors.append(
                f"Extreme burst velocity: {txns_1h} transactions initiated in the past hour (indicates automated or panic draining)."
            )
        elif txns_1h >= 3:
            score += 20.0
            factors.append(
                f"High transaction frequency: {txns_1h} transactions within the past hour."
            )
        elif txns_24h >= 15:
            score += 15.0
            factors.append(
                f"Elevated daily frequency: {txns_24h} transactions in the last 24 hours."
            )

        # C. Repeated Failed Security / PIN Attempts
        failed_attempts = int(user_profile.get("recent_failed_attempts", current_txn.get("failed_attempts", 0)))
        if failed_attempts >= 3:
            score += 35.0
            factors.append(
                f"Security brute-force alert: {failed_attempts} failed authentication attempts recorded prior to this transaction."
            )
        elif failed_attempts >= 1:
            score += 15.0
            factors.append(
                f"Preceding authentication retry: {failed_attempts} failed verification attempt(s) in last 24h."
            )

        # D. Timing Anomaly (Hour of Day)
        txn_hour = int(current_txn.get("hour_of_day", current_txn.get("hour", 14)))
        user_habitual_night = user_profile.get("transacts_at_night", False)

        if 1 <= txn_hour <= 5 and not user_habitual_night:
            score += 15.0
            factors.append(
                f"Unusual transaction timing: Executed during dormant hours ({txn_hour:02d}:00 AM) contrasting habitual active hours."
            )

        # E. Category Deviation
        txn_category = str(current_txn.get("merchant_category", "retail")).lower()
        regular_categories = user_profile.get("habitual_categories", ["retail", "grocery", "utility"])
        if txn_category in ["crypto", "gambling", "p2p_wire"] and txn_category not in regular_categories:
            score += 20.0
            factors.append(
                f"High-risk novel category deviation: User has no prior activity in '{txn_category.replace('_', ' ').title()}'."
            )

        # Baseline clamp: 0 to 100
        final_behavioral_score = max(0.0, min(100.0, score))

        return {
            "behavioral_risk_score": round(final_behavioral_score, 2),
            "is_cold_start": False,
            "factors": factors,
            "details": {
                "total_historical_txns": total_txns,
                "avg_amount": avg_amount,
                "multiplier": round(multiplier, 2),
                "z_score": round(z_score, 2),
                "txns_1h": txns_1h,
                "failed_attempts": failed_attempts,
            },
        }


# Singleton
_behavioral_engine = None


def get_behavioral_engine() -> BehavioralRiskEngine:
    global _behavioral_engine
    if _behavioral_engine is None:
        _behavioral_engine = BehavioralRiskEngine()
    return _behavioral_engine


if __name__ == "__main__":
    engine = get_behavioral_engine()
    # Test established user
    profile = {
        "total_txns": 45,
        "avg_amount": 42.0,
        "std_amount": 15.0,
        "max_amount": 180.0,
        "txns_last_1h": 4,
        "recent_failed_attempts": 2,
    }
    current = {"amount": 550.0, "hour_of_day": 3, "merchant_category": "crypto"}
    res = engine.evaluate_behavioral_risk(current, profile)
    print("Behavioral Assessment Result:")
    for k, v in res.items():
        print(f"  {k}: {v}")
