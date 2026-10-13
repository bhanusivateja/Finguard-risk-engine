"""
FinGuard AI - Risk Engine Simulator & Policy Tuner
Allows compliance officers and system administrators to experiment with
dynamic risk weights, policy thresholds, and observe simulated impacts in real time.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from src.ui_components import apply_custom_theme
from src.decision_engine import get_decision_engine

st.set_page_config(
    page_title="Risk Engine Simulator - FinGuard AI",
    page_icon="🎛️",
    layout="wide",
)

apply_custom_theme()
engine = get_decision_engine()

st.title("🎛️ Risk Engine Simulator & Policy Tuner")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Simulate policy rules, tune dynamic risk weights, and evaluate impact across real-world banking scenarios."
    "</p>",
    unsafe_allow_html=True,
)

# Simulation Controls
st.markdown("### ⚙️ Dynamic Risk Weight & Threshold Tuning")

col_w1, col_w2, col_w3 = st.columns(3)

with col_w1:
    raw_w_ml = st.slider(
        "Machine Learning Weight",
        min_value=0.05,
        max_value=0.80,
        value=float(config.DEFAULT_WEIGHT_ML),
        step=0.05,
        help="Weight assigned to IEEE-CIS trained model fraud probability",
    )

with col_w2:
    raw_w_beh = st.slider(
        "Behavioral Deviation Weight",
        min_value=0.05,
        max_value=0.80,
        value=float(config.DEFAULT_WEIGHT_BEHAVIORAL),
        step=0.05,
        help="Weight assigned to user spending deviations, frequency, and retry attempts",
    )

with col_w3:
    raw_w_ctx = st.slider(
        "Contextual Threat Weight",
        min_value=0.05,
        max_value=0.80,
        value=float(config.DEFAULT_WEIGHT_CONTEXTUAL),
        step=0.05,
        help="Weight assigned to gateway environment (merchant, device, IP, location, KYC)",
    )

# Normalize weights so they total 1.0
total_raw = raw_w_ml + raw_w_beh + raw_w_ctx
norm_w_ml = raw_w_ml / total_raw
norm_w_beh = raw_w_beh / total_raw
norm_w_ctx = raw_w_ctx / total_raw

st.markdown(
    f"""
    <div style="background-color: #131b2e; border: 1px solid #1e293b; padding: 10px 18px; border-radius: 8px; margin-bottom: 20px;">
        <span style="color: #94a3b8; font-size: 0.88rem;"><b>Normalized Active Weights:</b></span> &nbsp;
        <span style="color: #38bdf8; font-weight: 600;">ML: {norm_w_ml*100:.1f}%</span> &nbsp;|&nbsp;
        <span style="color: #818cf8; font-weight: 600;">Behavioral: {norm_w_beh*100:.1f}%</span> &nbsp;|&nbsp;
        <span style="color: #c084fc; font-weight: 600;">Contextual: {norm_w_ctx*100:.1f}%</span> &nbsp;
        <span style="color: #10b981; font-size: 0.85rem;">(Sum = 100.0%)</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Threshold Tuning
st.markdown("#### 🎯 Decision Boundary Thresholds")
col_t1, col_t2 = st.columns(2)
with col_t1:
    thresh_low = st.slider(
        "Low Risk Cutoff (ALLOW)",
        min_value=15.0,
        max_value=45.0,
        value=float(config.THRESHOLD_LOW_RISK),
        step=5.0,
        help="Transactions below this score are automatically approved",
    )
with col_t2:
    thresh_high = st.slider(
        "High Risk Cutoff (BLOCK)",
        min_value=55.0,
        max_value=85.0,
        value=float(config.THRESHOLD_MEDIUM_RISK),
        step=5.0,
        help="Transactions at or above this score are declined/blocked",
    )

custom_weights = {"ml": norm_w_ml, "behavioral": norm_w_beh, "contextual": norm_w_ctx}
custom_thresholds = {"low": thresh_low, "medium": thresh_high}

st.divider()

# Batch Scenario Testing Matrix
st.markdown("### 🧪 Live Batch Policy Impact Simulation")
st.markdown(
    "<span style='color: #94a3b8; font-size: 0.88rem;'>Evaluates 6 standardized real-world banking test cases with the currently tuned parameters:</span>",
    unsafe_allow_html=True,
)

test_scenarios = [
    {
        "name": "1. Routine Grocery Run",
        "req": {
            "user_id": "USER_101",
            "amount": 34.50,
            "merchant_category": "grocery",
            "device_status": "trusted_device",
            "ip_status": "clean_residential",
            "location_status": "home_location",
        },
    },
    {
        "name": "2. Cold-Start First Purchase",
        "req": {
            "user_id": "USER_303",
            "amount": 55.00,
            "merchant_category": "retail",
            "device_status": "new_device",
            "ip_status": "clean_residential",
            "location_status": "home_location",
            "kyc_status": "unverified",
            "account_age_days": 2,
        },
    },
    {
        "name": "3. Moderate Spending Surge",
        "req": {
            "user_id": "USER_101",
            "amount": 320.00,
            "merchant_category": "electronics",
            "device_status": "new_device",
            "ip_status": "clean_residential",
            "location_status": "domestic_travel",
            "failed_attempts": 1,
        },
    },
    {
        "name": "4. Enterprise Business Wire",
        "req": {
            "user_id": "USER_404",
            "amount": 850.00,
            "merchant_category": "travel_airline",
            "device_status": "trusted_device",
            "ip_status": "clean_residential",
            "location_status": "home_location",
        },
    },
    {
        "name": "5. Rapid Velocity Burst",
        "req": {
            "user_id": "USER_202",
            "amount": 750.00,
            "merchant_category": "p2p_transfer",
            "device_status": "new_device",
            "ip_status": "vpn_proxy",
            "location_status": "domestic_travel",
            "failed_attempts": 3,
            "txns_last_1h": 5,
        },
    },
    {
        "name": "6. Cross-Border Tor Casino Attack",
        "req": {
            "user_id": "USER_202",
            "amount": 4200.00,
            "merchant_category": "gambling",
            "device_status": "emulator_rooted",
            "ip_status": "tor_blacklisted",
            "location_status": "impossible_velocity",
            "failed_attempts": 4,
            "txns_last_1h": 7,
        },
    },
]

sim_rows = []
for sc in test_scenarios:
    res = engine.evaluate(
        sc["req"],
        custom_weights=custom_weights,
        custom_thresholds=custom_thresholds,
        save_record=False,
    )
    sim_rows.append({
        "Scenario": sc["name"],
        "Amount": f"${sc['req']['amount']:,.2f}",
        "ML Score": f"{res['component_scores']['ml_risk_score']:.1f}",
        "Beh Score": f"{res['component_scores']['behavioral_risk_score']:.1f}",
        "Ctx Score": f"{res['component_scores']['contextual_risk_score']:.1f}",
        "Dynamic Score": res["dynamic_risk_score"],
        "Risk Level": res["risk_level"],
        "Decision": res["decision"],
        "Primary Driver": res["primary_driver"],
    })

df_sim = pd.DataFrame(sim_rows)

# Render colored table
st.dataframe(
    df_sim,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Scenario": "Scenario Name",
        "Amount": "Amount",
        "ML Score": "ML Risk",
        "Beh Score": "Beh Risk",
        "Ctx Score": "Ctx Risk",
        "Dynamic Score": "Dynamic Score (0-100)",
        "Risk Level": "Risk Level",
        "Decision": "Policy Decision",
        "Primary Driver": "Primary Driver",
    },
)

# Comparison Bar Chart
fig_sim = px.bar(
    df_sim,
    x="Scenario",
    y="Dynamic Score",
    color="Decision",
    color_discrete_map={
        "ALLOW": "#10b981",
        "VERIFY": "#f59e0b",
        "BLOCK": "#ef4444",
    },
    text="Dynamic Score",
)
fig_sim.add_hline(y=thresh_low, line_dash="dash", line_color="#38bdf8", annotation_text="Low Cutoff")
fig_sim.add_hline(y=thresh_high, line_dash="dash", line_color="#ef4444", annotation_text="High Cutoff")
fig_sim.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#94a3b8",
    yaxis=dict(gridcolor="#1e293b", range=[0, 100]),
    xaxis=dict(gridcolor="#1e293b"),
    margin=dict(l=20, r=20, t=20, b=20),
)
st.plotly_chart(fig_sim, use_container_width=True)
