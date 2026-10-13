"""
FinGuard AI - Configuration Module
Banking Fraud Detection and Smart Transaction Protection System
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = DATA_DIR / "finguard.db"

# Dataset Source Candidates
CANDIDATE_DATA_PATHS = [
    Path(r"C:\Users\bhanu\Downloads\train_transaction.csv"),
    BASE_DIR / "data" / "train_transaction.csv",
]

CANDIDATE_IDENTITY_PATHS = [
    Path(r"C:\Users\bhanu\Downloads\train_identity.csv"),
    BASE_DIR / "data" / "train_identity.csv",
]

CANDIDATE_MERGED_PATHS = [
    Path(r"C:\Users\bhanu\Downloads\ieee_train_merged.csv"),
    Path(r"C:\Users\bhanu\Downloads\balanced_40percent.csv"),
]

# Processed Sample Paths (for fast app startup and reproducible metrics)
SAMPLE_TRAIN_PATH = DATA_DIR / "ieee_sample_train.parquet"
SAMPLE_TEST_PATH = DATA_DIR / "ieee_sample_test.parquet"

# Trained Model Artifacts
BEST_MODEL_PATH = MODELS_DIR / "best_fraud_model.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"
MODEL_COMPARISON_PATH = MODELS_DIR / "model_comparison.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.json"

# Core Risk Score Engine Weights (Default: sum to 1.0)
DEFAULT_WEIGHT_ML = 0.40
DEFAULT_WEIGHT_BEHAVIORAL = 0.35
DEFAULT_WEIGHT_CONTEXTUAL = 0.25

# Cold-Start Weight Allocation (When historical behavioral data is absent)
COLD_START_WEIGHT_ML = 0.45
COLD_START_WEIGHT_CONTEXTUAL = 0.45
COLD_START_WEIGHT_PRIOR = 0.10
COLD_START_DEFAULT_PRIOR = 35.0  # Neutral-prudent baseline prior (out of 100)
COLD_START_TXN_THRESHOLD = 5     # Minimum transactions to exit cold-start status

# Risk Thresholds
THRESHOLD_LOW_RISK = 30.0    # 0 <= Score < 30 : LOW RISK -> ALLOW
THRESHOLD_MEDIUM_RISK = 70.0 # 30 <= Score < 70 : MEDIUM RISK -> VERIFY
                             # 70 <= Score <= 100 : HIGH RISK -> BLOCK

# Decision Categories
DECISION_ALLOW = "ALLOW"
DECISION_VERIFY = "VERIFY"
DECISION_BLOCK = "BLOCK"

# Selected IEEE-CIS Features for Training & Live Inference
# These features have high predictive power in fraud detection literature
# and can be mapped cleanly to incoming live transaction parameters
NUMERICAL_FEATURES = [
    "TransactionAmt",
    "card1",
    "card2",
    "card3",
    "card5",
    "addr1",
    "addr2",
    "dist1",
    "C1",
    "C2",
    "C5",
    "C6",
    "C9",
    "C11",
    "C13",
    "C14",
    "D1",
    "D2",
    "D3",
    "D4",
    "D10",
    "D15",
    "V12",
    "V45",
    "V87",
    "V128",
    "V258",
    "V281",
    "V283",
    "V307",
    "V310",
    "V317",
]

CATEGORICAL_FEATURES = [
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
    "R_emaildomain",
    "DeviceType",
]

TARGET_COL = "isFraud"
TRANSACTION_ID_COL = "TransactionID"
