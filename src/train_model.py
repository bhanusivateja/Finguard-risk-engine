"""
FinGuard AI - Model Training & Evaluation Pipeline
Trains and rigorously benchmarks Random Forest, Gradient Boosting, and XGBoost
on the IEEE-CIS Fraud Detection dataset. Evaluates Precision, Recall, F1, ROC-AUC,
PR-AUC, and Confusion Matrix, selecting and serializing the optimal production model.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)
import xgboost as xgb

import config
from src.data_preprocessing import DataPreprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinGuard_Train")


class ModelTrainer:
    """
    Orchestrates data preparation, multi-model benchmarking,
    metric evaluation, and production artifact serialization.
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.models: Dict[str, Any] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.best_model_name: str = ""
        self.best_model: Any = None
        self.feature_importance: Dict[str, float] = {}

    def prepare_data(
        self, sample_size: int = 50000, test_ratio: float = 0.20
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame, pd.DataFrame]:
        """Prepares or loads cached train/test splits and transforms features."""
        if config.SAMPLE_TRAIN_PATH.exists() and config.SAMPLE_TEST_PATH.exists():
            logger.info("Loading existing cached train/test datasets from Parquet...")
            train_df = pd.read_parquet(config.SAMPLE_TRAIN_PATH)
            test_df = pd.read_parquet(config.SAMPLE_TEST_PATH)
        else:
            logger.info("Generating and caching train/test splits from IEEE-CIS dataset...")
            train_df, test_df = self.preprocessor.generate_and_cache_dataset_splits(
                sample_size=sample_size, test_ratio=test_ratio
            )

        logger.info(f"Fitting preprocessor on training data ({len(train_df)} rows)...")
        self.preprocessor.fit(train_df)
        self.preprocessor.save(config.PREPROCESSOR_PATH)

        X_train = self.preprocessor.transform(train_df)
        y_train = train_df[config.TARGET_COL].values

        X_test = self.preprocessor.transform(test_df)
        y_test = test_df[config.TARGET_COL].values

        logger.info(
            f"Preprocessed features shape: X_train={X_train.shape}, X_test={X_test.shape} | "
            f"Train Fraud Rate: {y_train.mean()*100:.2f}% | Test Fraud Rate: {y_test.mean()*100:.2f}%"
        )
        return X_train, y_train, X_test, y_test, train_df, test_df

    def train_and_evaluate_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ):
        """Trains Random Forest, Gradient Boosting, and XGBoost, collecting metrics."""
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        scale_pos_weight = float(neg_count / max(pos_count, 1))

        # Model Definitions
        candidate_models = {
            "Random Forest": RandomForestClassifier(
                n_estimators=80,
                max_depth=12,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
            "Gradient Boosting": HistGradientBoostingClassifier(
                max_iter=90,
                max_depth=8,
                class_weight="balanced",
                random_state=42,
            ),
            "XGBoost": xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.08,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=42,
                tree_method="hist",
            ),
        }

        print("=" * 80)
        print("FINGUARD AI - MODEL BENCHMARKING (IEEE-CIS FRAUD DATASET)")
        print("=" * 80)

        best_score = -1.0

        for name, model in candidate_models.items():
            logger.info(f"Training {name}...")
            model.fit(X_train, y_train)

            # Predict probabilities and classes
            y_pred_prob = model.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_prob >= 0.50).astype(int)

            # Calculate evaluation metrics
            acc = float(accuracy_score(y_test, y_pred))
            prec = float(precision_score(y_test, y_pred, zero_division=0))
            rec = float(recall_score(y_test, y_pred, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, zero_division=0))
            roc_auc = float(roc_auc_score(y_test, y_pred_prob))
            pr_auc = float(average_precision_score(y_test, y_pred_prob))

            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = [int(v) for v in cm.ravel()]

            metrics = {
                "model_name": name,
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "confusion_matrix": {
                    "true_negatives": tn,
                    "false_positives": fp,
                    "false_negatives": fn,
                    "true_positives": tp,
                },
            }

            self.models[name] = model
            self.results[name] = metrics

            print(f"\n--- {name} Results ---")
            print(f"  • Accuracy:        {acc*100:.2f}%")
            print(f"  • Precision:       {prec*100:.2f}%")
            print(f"  • Recall:          {rec*100:.2f}%")
            print(f"  • F1-Score:        {f1:.4f}")
            print(f"  • ROC-AUC:         {roc_auc:.4f}")
            print(f"  • PR-AUC:          {pr_auc:.4f}")
            print(f"  • Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

            # Selection criterion: ROC-AUC combined with F1
            combined_metric = roc_auc * 0.6 + f1 * 0.4
            if combined_metric > best_score:
                best_score = combined_metric
                self.best_model_name = name
                self.best_model = model

        print("\n" + "=" * 80)
        print(f"[SELECTED OPTIMAL MODEL]: {self.best_model_name}")
        print("=" * 80)

        # Extract Feature Importance for the best model
        self._extract_feature_importance()
        self._save_production_artifacts()

    def _extract_feature_importance(self):
        """Extracts top predictive feature importances from best model."""
        feature_names = self.preprocessor.feature_names_
        importances = {}

        if hasattr(self.best_model, "feature_importances_"):
            raw_imp = self.best_model.feature_importances_
            total = np.sum(raw_imp)
            norm_imp = (raw_imp / total) if total > 0 else raw_imp
            for name, score in zip(feature_names, norm_imp):
                importances[name] = float(round(score, 5))
        else:
            # Fallback uniform
            for name in feature_names:
                importances[name] = 1.0 / len(feature_names)

        # Sort descending
        sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
        self.feature_importance = sorted_imp
        logger.info(f"Top 5 most important features: {list(sorted_imp.items())[:5]}")

    def _save_production_artifacts(self):
        """Serializes model, metadata, and comparisons to disk."""
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

        # Save Best Model
        joblib.dump(self.best_model, config.BEST_MODEL_PATH)
        logger.info(f"Saved best model to: {config.BEST_MODEL_PATH}")

        # Save Model Comparison
        with open(config.MODEL_COMPARISON_PATH, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Saved model comparison to: {config.MODEL_COMPARISON_PATH}")

        # Save Feature Importance
        with open(config.FEATURE_IMPORTANCE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.feature_importance, f, indent=2)
        logger.info(f"Saved feature importance to: {config.FEATURE_IMPORTANCE_PATH}")

        # Save Metadata
        metadata = {
            "selected_model": self.best_model_name,
            "metrics": self.results[self.best_model_name],
            "num_features": len(self.preprocessor.feature_names_),
            "features": self.preprocessor.feature_names_,
            "dataset": "IEEE-CIS Fraud Detection",
            "weights": {
                "ml_weight": config.DEFAULT_WEIGHT_ML,
                "behavioral_weight": config.DEFAULT_WEIGHT_BEHAVIORAL,
                "contextual_weight": config.DEFAULT_WEIGHT_CONTEXTUAL,
            },
            "thresholds": {
                "low": config.THRESHOLD_LOW_RISK,
                "medium": config.THRESHOLD_MEDIUM_RISK,
            },
        }

        with open(config.MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved model metadata to: {config.MODEL_METADATA_PATH}")


def train_finguard_model():
    """Main execution function for model training."""
    trainer = ModelTrainer()
    X_train, y_train, X_test, y_test, _, _ = trainer.prepare_data(sample_size=50000)
    trainer.train_and_evaluate_all(X_train, y_train, X_test, y_test)
    print("\n[SUCCESS] Model training and evaluation completed successfully!")


if __name__ == "__main__":
    train_finguard_model()
