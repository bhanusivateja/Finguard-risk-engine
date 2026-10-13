# FinGuard AI: Intelligent Banking Fraud Detection and Smart Transaction Protection System with Dynamic Risk Scoring

**Final-Year B.Tech CSE (Artificial Intelligence & Machine Learning) Project**

---

## 📌 Executive Overview

**FinGuard AI** is a comprehensive, production-grade financial fraud defense platform engineered to evaluate transactional risk **before a transaction is approved or funds are transferred**. 

Traditional banking fraud detection systems operate retrospectively—alerting compliance teams hours or days after financial damage has occurred. FinGuard AI shifts the paradigm to **proactive, real-time pre-authorization evaluation** using a multi-layered **Dynamic Risk Score Engine (0–100)** combining:

1. **Machine Learning Fraud Probability:** Trained and benchmarked on the real-world **IEEE-CIS Fraud Detection** dataset.
2. **Behavioral Deviation Analytics:** Tracking historical spending z-scores, transaction frequency bursts, failed authentication retries, and temporal anomalies.
3. **Contextual Gateway Intelligence:** Assessing merchant risk, device fingerprint familiarity, IP network reputation (VPN/Tor), geographic consistency, and KYC tiers.
4. **Cold-Start Adaptive Prior:** Principled risk evaluation for brand-new accounts with zero transaction history without false-positive blocking.

---

## 🏛️ System Architecture

FinGuard AI operates as an integrated pre-authorization gateway following a strict 12-step decision lifecycle:

```
[ Incoming Transaction Request ]
              │
              ▼
    1. Input Validation & Schema Sanitization
              │
              ▼
    2. Extract Customer History & Baseline Profile (SQLite)
              │
              ├────────────────────────────────────────┬────────────────────────────────────────┐
              ▼                                        ▼                                        ▼
    3. ML Inference Engine                  4. Behavioral Analytics                  5. Contextual Risk
    • Feature vector mapping                • Amount Z-Score & Multiple              • Merchant Category Risk
    • Scikit-learn Pipeline                 • Velocity (1h / 24h burst)              • Device Familiarity
    • IEEE-CIS Trained Model                • Failed Authentication Retries          • IP Network Reputation
    • Calibrated P(Fraud)                   • Cold-Start Adaptive Prior              • Impossible Velocity / KYC
              │                                        │                                        │
              └────────────────────────────────────────┼────────────────────────────────────────┘
                                                       │
                                                       ▼
                                     6. Dynamic Risk Scoring Engine
                                  Score = (ML × w₁) + (Beh × w₂) + (Ctx × w₃)
                                                       │
                                                       ▼
                                        7. Policy Decision Mapping
                           ┌───────────────────────────┼───────────────────────────┐
                           ▼                           ▼                           ▼
                     [ 0 – 29 ]                   [ 30 – 69 ]                 [ 70 – 100 ]
                      LOW RISK                    MEDIUM RISK                  HIGH RISK
                       ALLOW                         VERIFY                      BLOCK
                 (Auto-Approved)               (Step-up 2FA / OTP)          (Account Frozen)
                                                       │
                                                       ▼
                                    8. Explainable AI & Audit Logging
                                 Persist to SQLite & Update Live Telemetry
```

---

## 📐 Mathematical Formulation

### 1. Dynamic Risk Score (0–100)

The composite risk score is computed through a normalized weighted linear combination:

$$\text{Dynamic Risk Score} = \left( P(\text{Fraud})_{\text{ML}} \times 100 \times w_{\text{ML}} \right) + \left( \text{Score}_{\text{Behavioral}} \times w_{\text{Beh}} \right) + \left( \text{Score}_{\text{Contextual}} \times w_{\text{Ctx}} \right)$$

Where default production weights satisfy:
$$w_{\text{ML}} = 0.40, \quad w_{\text{Beh}} = 0.35, \quad w_{\text{Ctx}} = 0.25 \quad \left( \sum w_i = 1.0 \right)$$

### 2. Multi-Vector Threat Corroboration Synergy
When multiple independent defense layers exhibit acute alarm levels simultaneously ($\text{Score}_{\text{Beh}} \ge 85$ and $\text{Score}_{\text{Ctx}} \ge 75$), an automated threat amplification factor is applied to reflect cross-channel corroboration of coordinated attacks.

### 3. Cold-Start Dynamic Weight Adaptation
For accounts with fewer than 5 historical transactions ($N < 5$), behavioral weights dynamically transition:
$$\alpha = \frac{N}{5}$$
$$w_{\text{ML}}(N) = w_{\text{ML}}^{\text{cold}}(1 - \alpha) + w_{\text{ML}}^{\text{default}}\alpha$$
$$w_{\text{Beh}}(N) = w_{\text{prior}}^{\text{cold}}(1 - \alpha) + w_{\text{Beh}}^{\text{default}}\alpha$$
$$w_{\text{Ctx}}(N) = w_{\text{Ctx}}^{\text{cold}}(1 - \alpha) + w_{\text{Ctx}}^{\text{default}}\alpha$$

---

## 📊 IEEE-CIS Machine Learning Model Benchmarks

Models were trained and evaluated on the **IEEE-CIS Fraud Detection dataset** under stratified validation and class-imbalance penalization:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Selection |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **95.39%** | **61.23%** | **67.42%** | **0.6418** | **0.9189** | **0.7053** | ⭐ **Optimal Selected** |
| **Gradient Boosting** | 90.56% | 37.16% | 78.40% | 0.5042 | 0.9195 | 0.6966 | Evaluated |
| **XGBoost (Hist)** | 90.43% | 36.66% | 77.35% | 0.4975 | 0.9169 | 0.6902 | Evaluated |

### Top Predictive Features Identified:
1. `V317`: Transaction aggregated volume ranking.
2. `C1`, `C13`, `C2`: Historical transaction and card association counting features.
3. `C5`: Associated domain / address frequency.
4. `TransactionAmt`: Payment amount in USD.

---

## 🛠️ Project Directory Structure

```
PROJECT DETAILSS/
├── app.py                         # Main Streamlit application & executive overview
├── config.py                      # Global configuration, weights, and file paths
├── requirements.txt               # Production Python dependencies
├── README.md                      # Comprehensive project documentation
├── data/
│   ├── finguard.db                # SQLite database for persistent logs & user profiles
│   ├── ieee_sample_train.parquet  # Stratified IEEE-CIS training partition
│   └── ieee_sample_test.parquet   # Stratified IEEE-CIS test benchmark partition
├── models/
│   ├── best_fraud_model.joblib    # Serialized optimal ML model artifact
│   ├── preprocessor.joblib        # Scikit-learn feature preprocessing pipeline
│   ├── model_metadata.json        # Production model metadata & hyperparameters
│   ├── model_comparison.json      # Empirical benchmark comparison results
│   └── feature_importance.json    # Top predictive feature rankings
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py      # Dataset loading, cleaning, imputation, and encoding
│   ├── train_model.py             # Model training, balancing, and benchmarking
│   ├── predict_fraud.py           # Real-time inference engine for single/batch txns
│   ├── behavioral_analysis.py     # User deviation, velocity, and timing scoring
│   ├── contextual_risk.py         # Gateway environment risk matrix (device, IP, geo)
│   ├── cold_start.py              # Zero-history cold-start assessment & prior weighting
│   ├── dynamic_risk_score.py      # Multi-pillar composite risk scoring algorithm
│   ├── decision_engine.py         # End-to-end 12-step transaction evaluation gateway
│   ├── storage.py                 # SQLite persistence layer and demo profiles
│   └── ui_components.py           # Custom dark theme CSS, Plotly gauges, and cards
├── pages/
│   ├── 1_Dashboard.py             # Executive operations dashboard & KPI telemetry
│   ├── 2_Transaction_Analyzer.py  # Interactive real-time transaction evaluation terminal
│   ├── 3_Fraud_Monitoring.py      # Forensic audit ledger, search, and CSV export
│   ├── 4_Model_Performance.py     # IEEE-CIS benchmark metrics, confusion matrix, ROC
│   └── 5_Risk_Engine_Simulator.py # Interactive weight sliders & batch policy testing
└── tests/
    ├── __init__.py
    ├── test_dynamic_risk.py       # Unit tests for scoring bounds, weights, & decisions
    ├── test_cold_start.py         # Unit tests for cold-start adaptation
    └── test_decision_engine.py    # Unit tests for end-to-end transaction pipeline
```

---

## 🚀 Quickstart & Installation Guide

### 1. Prerequisites
- Python 3.10 to 3.13
- Git & PowerShell / Bash

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Unit Test Suite
Verify that all 11 unit test suites pass cleanly:
```bash
python -m unittest discover tests
```

### 4. (Optional) Retrain Models
To run a fresh training and benchmarking cycle from the IEEE-CIS dataset:
```bash
python src/train_model.py
```

### 5. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

## 🧪 Demonstration Test Scenarios

The **Transaction Risk Analyzer** page includes 5 one-click demonstration presets:

1. **Normal Coffee (`$4.80`):** Established user (`USER_101`), trusted device, clean residential IP, home location. Result: **`LOW RISK (ALLOW)`** (~9/100).
2. **Cold-Start New Account (`$65.00`):** Brand new account (`USER_303`, 0 historical transactions), clean IP, unverified KYC. Result: **`LOW RISK (ALLOW)`** (~25/100) with cold-start adaptive prior explainability.
3. **Unusual Spending Surge (`$480.00`):** Regular shopper (`USER_101`, typical avg `$45.50`), new device, domestic travel, 1 retry attempt. Result: **`MEDIUM RISK (VERIFY)`** (~45/100, step-up OTP challenge recommended).
4. **Rapid Draining Attack (`$890.00`):** High-velocity account (`USER_202`), VPN proxy, 3 failed authentication retries, 5 transactions in last hour. Result: **`HIGH RISK (BLOCK)`** (~78/100).
5. **Cross-Border Tor / Casino Attack (`$4,500.00`):** Rooted emulator, Tor blacklisted network, impossible velocity anomaly, online gambling. Result: **`HIGH RISK (BLOCK)`** (~86/100, immediate transaction decline).

---

## 🔒 Security & Privacy Considerations

- **Zero Sensitive Data Storage:** No real credit card numbers, CVV codes, passwords, or PII are stored.
- **Explainable AI (XAI):** Every single decision provides plain-language reasons identifying exactly which signals raised or lowered the risk score.
- **Local SQLite Storage:** All logs and profiles remain securely isolated within the local workspace database (`data/finguard.db`).

---

## 🎓 Capstone Project Credits

- **Project Title:** FinGuard AI: Intelligent Banking Fraud Detection and Smart Transaction Protection System with Dynamic Risk Scoring
- **Department:** Computer Science & Engineering (Artificial Intelligence & Machine Learning)
- **Dataset:** IEEE Computational Intelligence Society Fraud Detection Benchmark
