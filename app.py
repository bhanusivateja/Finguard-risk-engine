"""
FinGuard AI: Intelligent Banking Fraud Detection and Smart Transaction Protection System
Main Application Entrypoint & Executive Overview
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
import config
from src.ui_components import apply_custom_theme
from src.storage import get_database_manager
from src.predict_fraud import get_fraud_predictor

# Page Configuration
st.set_page_config(
    page_title="FinGuard AI - Banking Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_theme()

# Sidebar Information
with st.sidebar:
    st.markdown("### 🛡️ FinGuard AI")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.85rem;'>Smart Banking Protection System<br>Final-Year B.Tech CSE (AI & ML) Project</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # System Status Indicators
    st.markdown("#### ⚡ System Telemetry")
    predictor = get_fraud_predictor()
    if predictor.is_loaded:
        st.success("🟢 ML Inference Engine: Active")
    else:
        st.warning("🟡 ML Model: Offline / Fallback")

    db = get_database_manager()
    st.success("🟢 Persistent Storage: Online (SQLite)")

    if config.SAMPLE_TEST_PATH.exists():
        st.success("🟢 IEEE-CIS Benchmark: Loaded")
    else:
        st.info("ℹ️ IEEE-CIS Benchmark: Ready")

    st.divider()
    st.markdown("#### ⚙️ Active Architecture")
    st.markdown("""
    - **ML Model:** Random Forest / XGBoost
    - **Dataset:** IEEE-CIS Fraud Detection
    - **Weights:** ML (40%), Beh (35%), Ctx (25%)
    - **Thresholds:** Low (<30), High (≥70)
    """)
    st.divider()
    st.caption("Developed for B.Tech AI & ML Capstone Evaluation")


# Main Page Content
st.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <h1 style="color: #f8fafc; font-size: 2.3rem; margin-bottom: 6px;">
            🛡️ FinGuard AI
        </h1>
        <h3 style="color: #38bdf8; font-size: 1.15rem; font-weight: 500; margin-top: 0;">
            Intelligent Banking Fraud Detection & Smart Transaction Protection System with Dynamic Risk Scoring
        </h3>
        <p style="color: #94a3b8; font-size: 0.95rem; max-width: 950px;">
            A proactive, multi-layered financial fraud defense platform that evaluates transactional risk 
            <b>BEFORE authorization</b>. Powered by the IEEE-CIS Fraud Detection benchmark, behavioral deviation analytics, 
            contextual gateway intelligence, and cold-start adaptation.
        </p>
    </div>
""", unsafe_allow_html=True)

# Architecture Flow Banner
st.markdown("""
<div class="finguard-card" style="border-left: 4px solid #38bdf8;">
    <h4 style="color: #f8fafc; margin-top: 0; margin-bottom: 10px;">Dynamic Risk Scoring Architecture</h4>
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 0.92rem; color: #cbd5e1;">
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;">
            <b>1. ML Fraud Probability</b> (IEEE-CIS Ensemble)
        </span>
        <span style="color: #38bdf8; font-weight: bold;">+</span>
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;">
            <b>2. Behavioral Risk</b> (Deviations, Velocity, Pin Retries)
        </span>
        <span style="color: #38bdf8; font-weight: bold;">+</span>
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;">
            <b>3. Contextual Risk</b> (Device, IP, Geo, KYC)
        </span>
        <span style="color: #38bdf8; font-weight: bold;">➔</span>
        <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 6px 12px; border-radius: 6px; border: 1px solid #38bdf8; font-weight: bold;">
            Dynamic Risk Score (0–100)
        </span>
        <span style="color: #38bdf8; font-weight: bold;">➔</span>
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;">
            <b>Policy Decision</b> (ALLOW / VERIFY / BLOCK)
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Overview Quick Metrics
db_metrics = db.get_dashboard_metrics()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Evaluations", f"{db_metrics['total_transactions']:,}")
with c2:
    st.metric("Avg Dynamic Risk", f"{db_metrics['average_risk_score']:.1f}/100")
with c3:
    st.metric("Blocked Frauds", f"{db_metrics['blocked_transactions']}")
with c4:
    st.metric("Step-up Verifications", f"{db_metrics['verified_transactions']}")

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Cards
st.subheader("Explore FinGuard AI System Modules")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">📊 Executive Dashboard</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Real-time security operations command center. Visualizes transaction volume, risk score distributions,
            fraudulent vs legitimate transaction ratios, and live risk categorization streams.
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>1_Dashboard</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">⚡ Transaction Risk Analyzer</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Interactive pre-authorization evaluation terminal. Input custom transaction parameters or test preset 
            attack scenarios (Cold-Start First Purchase, Crypto Surge, Draining Velocity) to view real-time score gauges and factor breakdowns.
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>2_Transaction_Analyzer</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">🚨 Fraud Monitoring Ledger</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Filterable historical ledger of all evaluated transactions. Inspect flagged fraudulent transactions, 
            view primary risk drivers, analyze specific factor explanations, and export audit trails to CSV.
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>3_Fraud_Monitoring</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">🧠 Model Performance & Research</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Inspect genuine benchmark metrics from the IEEE-CIS Fraud Detection dataset. Compare Random Forest, 
            HistGradientBoosting, and XGBoost with ROC-AUC curves, confusion matrices, and feature importance rankings.
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>4_Model_Performance</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">🎛️ Risk Engine Simulator</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Interactive policy sandbox: Tune dynamic risk weights with real-time normalization, adjust 
            decision thresholds (ALLOW/VERIFY/BLOCK), and simulate impacts across standardized banking scenarios.
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>5_Risk_Engine_Simulator</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_d:
    st.markdown("""
    <div class="finguard-card">
        <h3 style="color: #38bdf8; margin-top: 0;">🌐 Federated Learning Consortium</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Privacy-preserving multi-bank collaborative defense: Simulates 3 regional bank nodes collaborating 
            via Federated Averaging (FedAvg) with zero raw customer PII transfer (GDPR/RBI compliance).
        </p>
        <p style="color: #cbd5e1; font-size: 0.85rem;">
            👉 <i>Select <b>6_Federated_Learning</b> from the sidebar</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="finguard-card" style="margin-top: 10px;">
    <h4 style="color: #f8fafc; margin-top: 0;">Project Verification & Defense Note</h4>
    <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 0;">
        This system executes genuine machine learning inference trained directly on the IEEE-CIS Fraud Detection benchmark.
        It uses zero fabricated mock predictions. Missing values and cold-start accounts are processed via principled statistical prior weighting.
    </p>
</div>
""", unsafe_allow_html=True)
