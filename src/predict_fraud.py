"""
FinGuard AI - Fraud Probability Predictor
Loads trained machine learning model and preprocessor to predict
the fraud probability P(Fraud) for single transactions or batches.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import joblib

import config
from src.data_preprocessing import DataPreprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinGuard_Predict")


class FraudPredictor:
    """
    Inference Engine for ML Fraud Probability.
    Converts raw incoming transaction parameters into model-compatible vectors,
    invokes the calibrated ML model, and outputs the fraud probability.
    """

    def __init__(
        self,
        model_path: Path = config.BEST_MODEL_PATH,
        preprocessor_path: Path = config.PREPROCESSOR_PATH,
    ):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model = None
        self.preprocessor = None
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self):
        """Loads model and preprocessor if available."""
        try:
            if self.model_path.exists() and self.preprocessor_path.exists():
                self.model = joblib.load(self.model_path)
                self.preprocessor = DataPreprocessor.load(self.preprocessor_path)
                self.is_loaded = True
                logger.info(f"Loaded ML model from {self.model_path}")
            else:
                logger.warning("Model or preprocessor artifacts not found on disk.")
                self.is_loaded = False
        except Exception as e:
            logger.error(f"Error loading model artifacts: {e}")
            self.is_loaded = False

    def predict_transaction_probability(self, txn_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single live transaction.
        Returns:
            {
                "ml_probability": float (0.0 to 1.0),
                "ml_risk_score": float (0.0 to 100.0),
                "model_status": "active" | "untrained_fallback",
                "factors": list of str
            }
        """
        if not self.is_loaded:
            # Fallback if model was not trained yet
            logger.warning("Predictor invoked without loaded model. Using baseline heuristic.")
            amount = float(txn_dict.get("TransactionAmt", txn_dict.get("amount", 100.0)))
            fallback_prob = min(0.95, max(0.05, amount / 5000.0 * 0.5))
            return {
                "ml_probability": round(fallback_prob, 4),
                "ml_risk_score": round(fallback_prob * 100.0, 2),
                "model_status": "untrained_fallback",
                "factors": ["Warning: Real ML model not loaded; heuristic baseline used."],
            }

        # Normalize incoming field names to IEEE-CIS column standards
        mapped_dict = self._map_incoming_fields(txn_dict)

        # Preprocess features into 2D numpy array
        X_vec = self.preprocessor.preprocess_single_transaction(mapped_dict)

        # Predict probability
        proba = float(self.model.predict_proba(X_vec)[0, 1])
        ml_score = proba * 100.0

        factors = []
        if proba > 0.65:
            factors.append(f"High ML fraud pattern affinity: {proba*100:.1f}% fraud probability detected by ensemble model.")
        elif proba > 0.35:
            factors.append(f"Moderate ML fraud signature: {proba*100:.1f}% probability based on transaction features.")
        else:
            factors.append(f"Low ML fraud signature: {proba*100:.1f}% probability indicates normal transaction characteristics.")

        return {
            "ml_probability": round(proba, 4),
            "ml_risk_score": round(ml_score, 2),
            "model_status": "active",
            "factors": factors,
        }

    def predict_batch_probabilities(self, df: pd.DataFrame) -> np.ndarray:
        """Predicts probabilities for a batch DataFrame."""
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded.")
        X_mat = self.preprocessor.transform(df)
        return self.model.predict_proba(X_mat)[:, 1]

    def _map_incoming_fields(self, raw_txn: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates human-readable transaction inputs to IEEE-CIS features.
        """
        mapped = dict(raw_txn)

        # Map Amount
        if "amount" in raw_txn and "TransactionAmt" not in raw_txn:
            mapped["TransactionAmt"] = raw_txn["amount"]

        # Map Card Network
        if "card_network" in raw_txn and "card4" not in raw_txn:
            mapped["card4"] = str(raw_txn["card_network"]).lower()

        # Map Card Type
        if "card_type" in raw_txn and "card6" not in raw_txn:
            mapped["card6"] = str(raw_txn["card_type"]).lower()

        # Map Device Type
        if "device_type" in raw_txn and "DeviceType" not in raw_txn:
            mapped["DeviceType"] = str(raw_txn["device_type"]).lower()

        # Map Email Domain
        if "email_domain" in raw_txn and "P_emaildomain" not in raw_txn:
            mapped["P_emaildomain"] = str(raw_txn["email_domain"]).lower()

        # Map Product / Channel Code
        if "channel" in raw_txn and "ProductCD" not in raw_txn:
            channel = str(raw_txn["channel"]).upper()
            mapping = {"WEB": "W", "MOBILE": "C", "POS": "R", "UPI": "H", "OTHER": "S"}
            mapped["ProductCD"] = mapping.get(channel, "W")
        elif "ProductCD" not in mapped:
            mapped["ProductCD"] = "W"

        return mapped


# Singleton instance for fast live reuse
_predictor_instance = None


def get_fraud_predictor() -> FraudPredictor:
    """Returns singleton FraudPredictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = FraudPredictor()
    return _predictor_instance


if __name__ == "__main__":
    predictor = get_fraud_predictor()
    test_txn = {
        "amount": 250.0,
        "card_network": "visa",
        "card_type": "credit",
        "email_domain": "gmail.com",
        "device_type": "mobile",
        "channel": "WEB",
    }
    result = predictor.predict_transaction_probability(test_txn)
    print("Test Prediction:")
    for k, v in result.items():
        print(f"  {k}: {v}")
