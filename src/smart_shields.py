"""
FinGuard AI - Smart Protection Shields Module
Implements specialized banking security layers:
1. Child-Safe Spending Protection: Detects impulsive in-app/gaming microtransactions
   on parents' accounts and requires parental step-up verification.
2. Betting & High-Risk Speculative Alerts: Detects rapid deposits into gambling,
   rummy, and betting portals, enforcing cool-off safety challenges.
"""

import sys
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("FinGuard_SmartShields")


class SmartShieldsEngine:
    """
    Evaluates specialized fraud & safety shields on top of baseline scoring.
    Directly aligns with FinGuard AI mentor innovations.
    """

    # Known gaming and app store indicators
    GAMING_KEYWORDS = [
        "gaming", "game", "in_app_purchase", "playstore", "app_store",
        "roblox", "free_fire", "bgmi", "steam", "playstation", "xbox"
    ]

    # Known betting and gambling indicators
    BETTING_KEYWORDS = [
        "gambling", "casino", "betting", "rummy", "poker", "lottery",
        "sports_bet", "dream11", "stake"
    ]

    def evaluate_shields(
        self,
        txn_request: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates active protection shields.
        Returns triggered shield flags, score adjustments, and advisory messages.
        """
        merchant_cat = str(txn_request.get("merchant_category", "")).lower()
        amount = float(txn_request.get("amount", txn_request.get("TransactionAmt", 0.0)))
        txns_1h = int(txn_request.get("txns_last_1h", 0))

        # Check if user has child-safe mode enabled (or detect gaming burst)
        child_safe_enabled = bool(
            txn_request.get("child_safe_mode", user_profile.get("child_safe_mode_enabled", False))
        )

        shield_alerts: List[Dict[str, Any]] = []
        protective_score_boost = 0.0

        # -------------------------------------------------------------
        # SHIELD 1: Child-Safe Spending Protection
        # -------------------------------------------------------------
        is_gaming = any(k in merchant_cat for k in self.GAMING_KEYWORDS) or merchant_cat in ["gaming", "electronics"]
        
        if child_safe_enabled and is_gaming:
            protective_score_boost += 25.0
            shield_alerts.append({
                "shield": "Child-Safe Spending Protection",
                "severity": "HIGH",
                "icon": "👶",
                "message": (
                    f"Child-Safe Shield Active: Gaming/In-App transaction of ${amount:,.2f} detected on parent account. "
                    "Mandatory parental biometric / PIN confirmation triggered to prevent accidental digital spend."
                ),
                "action_override": "REQUIRE_PARENTAL_APPROVAL",
            })
        elif is_gaming and amount > 150.0 and txns_1h >= 2:
            # Automatic heuristic detection even without explicit toggle
            protective_score_boost += 15.0
            shield_alerts.append({
                "shield": "Suspected Unauthorized Minor In-App Purchase",
                "severity": "MEDIUM",
                "icon": "🎮",
                "message": (
                    f"Multiple rapid gaming transactions (${amount:,.2f}, {txns_1h} within 1h). "
                    "Suspected accidental child spending."
                ),
                "action_override": "PARENTAL_OTP_CHALLENGE",
            })

        # -------------------------------------------------------------
        # SHIELD 2: Betting & High-Risk Speculation Alert
        # -------------------------------------------------------------
        is_betting = any(k in merchant_cat for k in self.BETTING_KEYWORDS) or merchant_cat == "gambling"

        if is_betting:
            if txns_1h >= 3:
                protective_score_boost += 35.0
                shield_alerts.append({
                    "shield": "Compulsive Gambling & Loss-Chasing Shield",
                    "severity": "CRITICAL",
                    "icon": "🎲",
                    "message": (
                        f"Acute high-frequency betting deposits ({txns_1h} transactions in 1 hour). "
                        "Cooling-off mandatory freeze enforced for account protection."
                    ),
                    "action_override": "COOLING_OFF_FREEZE",
                })
            elif amount >= 1000.0:
                protective_score_boost += 25.0
                shield_alerts.append({
                    "shield": "High-Value Unregulated Gambling Alert",
                    "severity": "HIGH",
                    "icon": "🎰",
                    "message": (
                        f"Large deposit (${amount:,.2f}) into offshore casino/betting portal. "
                        "Step-up risk verification and transaction velocity check required."
                    ),
                    "action_override": "MANDATORY_2FA_ACKNOWLEDGE",
                })

        return {
            "shields_active": len(shield_alerts) > 0,
            "shield_alerts": shield_alerts,
            "protective_score_boost": protective_score_boost,
        }


# Singleton
_smart_shields_instance = None


def get_smart_shields_engine() -> SmartShieldsEngine:
    global _smart_shields_instance
    if _smart_shields_instance is None:
        _smart_shields_instance = SmartShieldsEngine()
    return _smart_shields_instance


if __name__ == "__main__":
    engine = get_smart_shields_engine()
    test_child = {
        "merchant_category": "gaming",
        "amount": 79.99,
        "child_safe_mode": True,
        "txns_last_1h": 2,
    }
    res = engine.evaluate_shields(test_child, {})
    print("Child-Safe Shield Test:")
    for a in res["shield_alerts"]:
        print(f"  [{a['icon']} {a['shield']}]: {a['message']}")
