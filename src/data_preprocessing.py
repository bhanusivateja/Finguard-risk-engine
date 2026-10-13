"""
FinGuard AI - Data Preprocessing Pipeline
Handles IEEE-CIS Fraud Detection dataset loading, feature selection,
imputation, encoding, and inference transformations.
"""

import os
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinGuard_Preprocess")


class DataPreprocessor:
    """
    Robust Preprocessor for IEEE-CIS Fraud Detection dataset.
    Handles missing values, categorical encoding, and feature scaling.
    Ensures zero data leakage between train and test/live inference.
    """

    def __init__(self):
        self.numerical_cols = list(config.NUMERICAL_FEATURES)
        self.categorical_cols = list(config.CATEGORICAL_FEATURES)
        self.all_feature_cols = self.numerical_cols + self.categorical_cols
        self.pipeline: Optional[ColumnTransformer] = None
        self.feature_names_: list = []
        self.medians_: Dict[str, float] = {}
        self.modes_: Dict[str, str] = {}

    def find_dataset_files(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Locates available IEEE-CIS dataset files."""
        trans_path = None
        for p in config.CANDIDATE_DATA_PATHS:
            if p.exists():
                trans_path = p
                break

        id_path = None
        for p in config.CANDIDATE_IDENTITY_PATHS:
            if p.exists():
                id_path = p
                break

        return trans_path, id_path

    def load_stratified_sample(
        self,
        sample_size: int = 60000,
        fraud_ratio: float = 0.12,
        random_state: int = 42
    ) -> pd.DataFrame:
        """
        Loads an intelligent representative sample of the IEEE-CIS dataset.
        Preserves genuine feature correlations while enriching fraud representation
        so tree-based models learn meaningful boundary patterns without RAM exhaustion.
        """
        trans_path, id_path = self.find_dataset_files()
        if not trans_path:
            raise FileNotFoundError(
                f"Could not find IEEE-CIS train_transaction.csv. Looked in: {config.CANDIDATE_DATA_PATHS}"
            )

        logger.info(f"Loading IEEE-CIS transaction data from: {trans_path}")

        # Determine columns to read to conserve memory
        target_trans_cols = ["TransactionID", config.TARGET_COL] + [
            c for c in self.all_feature_cols if c not in ["DeviceType"]
        ]

        # Read transaction data in chunks or direct read with selective columns
        logger.info("Reading transaction records...")
        trans_df = pd.read_csv(trans_path, usecols=lambda c: c in target_trans_cols, nrows=120000)

        # Merge identity data if available
        if id_path and id_path.exists():
            logger.info(f"Merging identity features from: {id_path}")
            id_cols = ["TransactionID", "DeviceType"]
            id_df = pd.read_csv(id_path, usecols=lambda c: c in id_cols)
            merged_df = trans_df.merge(id_df, on="TransactionID", how="left")
        else:
            merged_df = trans_df
            merged_df["DeviceType"] = np.nan

        # Fill missing DeviceType with 'unknown'
        merged_df["DeviceType"] = merged_df["DeviceType"].fillna("unknown").astype(str)

        # Class balancing / Stratified representation
        fraud_df = merged_df[merged_df[config.TARGET_COL] == 1]
        non_fraud_df = merged_df[merged_df[config.TARGET_COL] == 0]

        target_frauds = int(sample_size * fraud_ratio)
        target_non_frauds = sample_size - target_frauds

        n_frauds = min(len(fraud_df), target_frauds)
        n_non_frauds = min(len(non_fraud_df), target_non_frauds)

        sampled_fraud = fraud_df.sample(n=n_frauds, random_state=random_state, replace=False)
        sampled_non_fraud = non_fraud_df.sample(n=n_non_frauds, random_state=random_state, replace=False)

        combined = pd.concat([sampled_fraud, sampled_non_fraud], ignore_index=True)
        combined = combined.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

        logger.info(
            f"Sample created: {len(combined)} rows | "
            f"Frauds: {combined[config.TARGET_COL].sum()} ({combined[config.TARGET_COL].mean()*100:.2f}%)"
        )
        return combined

    def fit(self, X: pd.DataFrame) -> "DataPreprocessor":
        """Fits numerical imputers, scalers, and categorical encoders."""
        # Ensure all required columns exist in input
        for col in self.numerical_cols:
            if col not in X.columns:
                X[col] = np.nan
        for col in self.categorical_cols:
            if col not in X.columns:
                X[col] = "unknown"

        # Calculate medians and modes for rapid live single-transaction inference
        for col in self.numerical_cols:
            med = X[col].median()
            self.medians_[col] = float(0.0 if pd.isna(med) else med)

        for col in self.categorical_cols:
            mode_series = X[col].dropna().mode()
            self.modes_[col] = str(mode_series.iloc[0]) if not mode_series.empty else "unknown"

        # Numerical Pipeline: Median Imputation + Standard Scaling
        num_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        # Categorical Pipeline: Constant Imputation + Ordinal Encoding (safe for unseen categories)
        cat_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
                (
                    "encoder",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value",
                        unknown_value=-1,
                        encoded_missing_value=-1,
                    ),
                ),
            ]
        )

        self.pipeline = ColumnTransformer(
            transformers=[
                ("num", num_transformer, self.numerical_cols),
                ("cat", cat_transformer, self.categorical_cols),
            ],
            remainder="drop",
        )

        self.pipeline.fit(X[self.all_feature_cols])
        self.feature_names_ = self.numerical_cols + self.categorical_cols
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transforms feature dataframe into scaled/encoded numpy array."""
        if self.pipeline is None:
            raise ValueError("Preprocessor pipeline has not been fitted.")

        X_copy = X.copy()
        for col in self.numerical_cols:
            if col not in X_copy.columns:
                X_copy[col] = self.medians_.get(col, 0.0)
            else:
                X_copy[col] = pd.to_numeric(X_copy[col], errors="coerce")

        for col in self.categorical_cols:
            if col not in X_copy.columns:
                X_copy[col] = self.modes_.get(col, "unknown")
            else:
                X_copy[col] = X_copy[col].fillna("unknown").astype(str)

        return self.pipeline.transform(X_copy[self.all_feature_cols])

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.fit(X).transform(X)

    def save(self, filepath: Path = config.PREPROCESSOR_PATH):
        """Saves fitted preprocessor and statistics to disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        artifact = {
            "pipeline": self.pipeline,
            "numerical_cols": self.numerical_cols,
            "categorical_cols": self.categorical_cols,
            "feature_names": self.feature_names_,
            "medians": self.medians_,
            "modes": self.modes_,
        }
        joblib.dump(artifact, filepath)
        logger.info(f"Preprocessor saved successfully to: {filepath}")

    @classmethod
    def load(cls, filepath: Path = config.PREPROCESSOR_PATH) -> "DataPreprocessor":
        """Loads fitted preprocessor from disk."""
        if not filepath.exists():
            raise FileNotFoundError(f"Preprocessor file not found at: {filepath}")

        artifact = joblib.load(filepath)
        instance = cls()
        instance.pipeline = artifact["pipeline"]
        instance.numerical_cols = artifact["numerical_cols"]
        instance.categorical_cols = artifact["categorical_cols"]
        instance.feature_names_ = artifact["feature_names"]
        instance.medians_ = artifact["medians"]
        instance.modes_ = artifact["modes"]
        instance.all_feature_cols = instance.numerical_cols + instance.categorical_cols
        return instance

    def preprocess_single_transaction(self, txn_dict: Dict[str, Any]) -> np.ndarray:
        """
        Converts a single incoming live transaction dictionary into
        a model-ready 2D feature matrix (1, N_features).
        Safely fills missing features using empirical dataset baselines.
        """
        row = {}
        # Map or fill numerical columns
        for col in self.numerical_cols:
            val = txn_dict.get(col, None)
            if val is None or pd.isna(val) or val == "":
                row[col] = self.medians_.get(col, 0.0)
            else:
                try:
                    row[col] = float(val)
                except (ValueError, TypeError):
                    row[col] = self.medians_.get(col, 0.0)

        # Map or fill categorical columns
        for col in self.categorical_cols:
            val = txn_dict.get(col, None)
            if val is None or pd.isna(val) or val == "":
                row[col] = self.modes_.get(col, "unknown")
            else:
                row[col] = str(val).strip().lower()

        df_row = pd.DataFrame([row])
        return self.transform(df_row)

    def generate_and_cache_dataset_splits(
        self, sample_size: int = 50000, test_ratio: float = 0.20
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Creates, splits, and caches train and test datasets as Parquet
        for rapid reproducible training and dashboard metric displays.
        """
        from sklearn.model_selection import train_test_split

        full_sample = self.load_stratified_sample(
            sample_size=sample_size, fraud_ratio=0.12, random_state=42
        )
        train_df, test_df = train_test_split(
            full_sample,
            test_size=test_ratio,
            random_state=42,
            stratify=full_sample[config.TARGET_COL],
        )

        # Save to parquet
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        train_df.to_parquet(config.SAMPLE_TRAIN_PATH, index=False)
        test_df.to_parquet(config.SAMPLE_TEST_PATH, index=False)

        logger.info(
            f"Saved cached train parquet: {config.SAMPLE_TRAIN_PATH} ({len(train_df)} rows)"
        )
        logger.info(
            f"Saved cached test parquet: {config.SAMPLE_TEST_PATH} ({len(test_df)} rows)"
        )
        return train_df, test_df


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    trans_p, id_p = preprocessor.find_dataset_files()
    print(f"Transaction file: {trans_p}")
    print(f"Identity file: {id_p}")

    sample_df = preprocessor.load_stratified_sample(sample_size=20000, fraud_ratio=0.10)
    print("Fitting preprocessor...")
    X_mat = preprocessor.fit_transform(sample_df)
    print(f"Transformed matrix shape: {X_mat.shape}")
    preprocessor.save()
    print("[SUCCESS] Preprocessing pipeline verified successfully!")
