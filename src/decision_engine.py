"""
FinGuard AI - Complete Transaction Decision Engine
End-to-End Orchestrator executing the complete 12-step decision workflow:
Input Validation -> ML Inference -> Behavioral Analysis -> Contextual Risk
-> Cold-Start Adaptation -> Dynamic Score -> Policy Decision -> Persistence.
"""

import sys
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.predict_fraud import get_fraud_predictor
from src.behavioral_analysis import get_behavioral_engine
from src.contextual_risk import get_contextual_engine
from src.dynamic_risk_score import get_dynamic_risk_engine
from src.storage import get_database_manager
from src.smart_shields import get_smart_shields_engine

logger = logging.getLogger("FinGuard_DecisionEngine")


class TransactionDecisionEngine:
    """
    Production Gateway for evaluating banking transactions BEFORE authorization.
    """

    def __init__(self):
        self.predictor = get_fraud_predictor()
        self.behavioral_engine = get_behavioral_engine()
        self.contextual_engine = get_contextual_engine()
        self.dynamic_risk_engine = get_dynamic_risk_engine()
        self.smart_shields = get_smart_shields_engine()
        self.db = get_database_manager()

    def evaluate(
        self,
        txn_request: Dict[str, Any],
        custom_weights: Optional[Dict[str, float]] = None,
        custom_thresholds: Optional[Dict[str, float]] = None,
        save_record: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the full evaluation pipeline.
        """
        # Step 1: Assign ID and Timestamp
        txn_id = txn_request.get("transaction_id", f"TXN-{uuid.uuid4().hex[:8].upper()}")
        timestamp = txn_request.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        user_id = str(txn_request.get("user_id", "USER_101")).strip()

        # Step 2: Validate Input
        amount = float(txn_request.get("amount", txn_request.get("TransactionAmt", 0.0)))
        if amount <= 0.0:
            raise ValueError(f"Invalid transaction amount: ${amount}. Must be greater than 0.")

        # Step 3: Fetch User Profile
        user_profile = self.db.get_user_profile(user_id)
        if not user_profile:
            # Fallback for ad-hoc / new customer IDs
            user_profile = {
                "user_id": user_id,
                "account_name": f"New Customer ({user_id})",
                "total_txns": 0,
                "avg_amount": 0.0,
                "std_amount": 0.0,
                "max_amount": 0.0,
                "recent_failed_attempts": int(txn_request.get("failed_attempts", 0)),
                "account_age_days": int(txn_request.get("account_age_days", 1)),
                "kyc_status": txn_request.get("kyc_status", "unverified"),
            }

        # Step 4: ML Fraud Probability Inference
        ml_input = {
            "TransactionAmt": amount,
            "card_network": txn_request.get("card_network", "visa"),
            "card_type": txn_request.get("card_type", "credit"),
            "device_type": txn_request.get("device_type", "mobile"),
            "email_domain": txn_request.get("email_domain", "gmail.com"),
            "channel": txn_request.get("channel", "WEB"),
        }
        ml_res = self.predictor.predict_transaction_probability(ml_input)

        # Step 5: Contextual Risk Evaluation
        ctx_input = {
            "merchant_category": txn_request.get("merchant_category", "retail"),
            "device_status": txn_request.get("device_status", "trusted_device"),
            "ip_status": txn_request.get("ip_status", "clean_residential"),
            "location_status": txn_request.get("location_status", "home_location"),
            "account_age_days": int(txn_request.get("account_age_days", user_profile.get("account_age_days", 180))),
            "kyc_status": txn_request.get("kyc_status", user_profile.get("kyc_status", "fully_verified")),
        }
        ctx_res = self.contextual_engine.evaluate_contextual_risk(ctx_input)

        # Step 6: Behavioral Risk Analysis (With Cold-Start Detection)
        beh_input = {
            "amount": amount,
            "hour_of_day": int(txn_request.get("hour_of_day", datetime.now().hour)),
            "merchant_category": txn_request.get("merchant_category", "retail"),
            "failed_attempts": int(txn_request.get("failed_attempts", user_profile.get("recent_failed_attempts", 0))),
            "txns_last_1h": int(txn_request.get("txns_last_1h", 0)),
            "txns_last_24h": int(txn_request.get("txns_last_24h", 1)),
        }
        beh_res = self.behavioral_engine.evaluate_behavioral_risk(
            current_txn=beh_input,
            user_profile=user_profile,
            contextual_data=ctx_input,
        )

        # Step 6b: Smart Protection Shields (Child-Safe Mode & Betting Alerts)
        shields_res = self.smart_shields.evaluate_shields(txn_request, user_profile)
        if shields_res["protective_score_boost"] > 0:
            ctx_res["contextual_risk_score"] = min(100.0, ctx_res["contextual_risk_score"] + shields_res["protective_score_boost"])
        for alert in shields_res["shield_alerts"]:
            ctx_res["factors"].append(f"[{alert['icon']} {alert['shield']}]: {alert['message']}")

        # Step 7: Combine factors
        incoming_factors = {
            "ml": ml_res["factors"],
            "behavioral": beh_res["factors"],
            "contextual": ctx_res["factors"],
        }

        # Step 8: Compute Dynamic Risk Score & Decision
        risk_result = self.dynamic_risk_engine.compute_dynamic_risk(
            ml_score=ml_res["ml_risk_score"],
            behavioral_score=beh_res["behavioral_risk_score"],
            contextual_score=ctx_res["contextual_risk_score"],
            is_cold_start=beh_res["is_cold_start"],
            total_historical_txns=user_profile.get("total_txns", 0),
            custom_weights=custom_weights,
            custom_thresholds=custom_thresholds,
            incoming_factors=incoming_factors,
        )

        # Check action override from active shields (e.g. Parental 2FA)
        action_text = risk_result["recommended_action"]
        for alert in shields_res["shield_alerts"]:
            if "action_override" in alert and risk_result["decision"] != config.DECISION_BLOCK:
                action_text = f"Action: {alert['shield']} Enforcement ({alert['action_override'].replace('_', ' ').title()})"

        # Build complete payload
        record = {
            "transaction_id": txn_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "account_name": user_profile.get("account_name", user_id),
            "amount": amount,
            "merchant_category": txn_request.get("merchant_category", "retail"),
            "card_network": txn_request.get("card_network", "visa"),
            "card_type": txn_request.get("card_type", "credit"),
            "ml_probability": ml_res["ml_probability"],
            "ml_risk_score": ml_res["ml_risk_score"],
            "behavioral_risk_score": beh_res["behavioral_risk_score"],
            "contextual_risk_score": ctx_res["contextual_risk_score"],
            "dynamic_risk_score": risk_result["dynamic_risk_score"],
            "risk_level": risk_result["risk_level"],
            "decision": risk_result["decision"],
            "recommended_action": action_text,
            "decision_detail": risk_result["decision_detail"],
            "badge_color": risk_result["badge_color"],
            "primary_driver": risk_result["primary_driver"],
            "is_cold_start": beh_res["is_cold_start"],
            "shields_active": shields_res["shields_active"],
            "shield_alerts": shields_res["shield_alerts"],
            "weights_used": risk_result["weights_used"],
            "component_contributions": risk_result["component_contributions"],
            "component_scores": risk_result["component_scores"],
            "explanation_factors": risk_result["explanation_factors"],
            "raw_details": {
                "user_profile": user_profile,
                "contextual_components": ctx_res.get("component_scores", {}),
                "behavioral_details": beh_res.get("details", {}),
            },
        }

        # Step 9: Persist to storage & update user profile
        if save_record:
            self.db.save_transaction(record)
            self.db.update_user_profile_after_txn(user_id, amount, risk_result["decision"])

        return record


# Singleton
_decision_engine_instance = None


def get_decision_engine() -> TransactionDecisionEngine:
    global _decision_engine_instance
    if _decision_engine_instance is None:
        _decision_engine_instance = TransactionDecisionEngine()
    return _decision_engine_instance


if __name__ == "__main__":
    engine = get_decision_engine()
    test_req = {
        "user_id": "USER_101",
        "amount": 42.0,
        "merchant_category": "grocery",
        "card_network": "visa",
        "card_type": "debit",
        "device_status": "trusted_device",
        "ip_status": "clean_residential",
        "location_status": "home_location",
    }
    result = engine.evaluate(test_req)
    print("\n--- Decision Gateway Output ---")
    print(f"Transaction ID: {result['transaction_id']}")
    print(f"Dynamic Risk Score: {result['dynamic_risk_score']} / 100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Decision: {result['decision']} ({result['recommended_action']})")
    print("Explanations:")
    for f in result['explanation_factors']:
        print(f"  - {f}")
