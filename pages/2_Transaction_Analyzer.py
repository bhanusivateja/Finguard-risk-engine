"""
FinGuard AI - Transaction Risk Analyzer
Interactive real-time transaction risk evaluation terminal.
Computes ML fraud probability, behavioral deviations, contextual gateway risk,
and final dynamic risk score with comprehensive explainability.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import streamlit as st

import config
from src.ui_components import apply_custom_theme, render_risk_gauge, render_contribution_bar
from src.decision_engine import get_decision_engine
from src.storage import get_database_manager

st.set_page_config(
    page_title="Transaction Risk Analyzer - FinGuard AI",
    page_icon="⚡",
    layout="wide",
)

apply_custom_theme()
decision_engine = get_decision_engine()
db = get_database_manager()

st.title("⚡ Real-Time Transaction Risk Analyzer")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Pre-Authorization Risk Evaluation Engine: Evaluates dynamic risk score (0-100) before fund transfer."
    "</p>",
    unsafe_allow_html=True,
)

# Demonstration Presets
st.markdown("#### 🚀 Rapid Demonstration Presets")
st.markdown(
    "<span style='color: #94a3b8; font-size: 0.85rem;'>Select a pre-configured banking scenario to populate the input parameters instantly:</span>",
    unsafe_allow_html=True,
)

col_p1, col_p2, col_p3, col_p4, col_p5, col_p6 = st.columns(6)

# Session state initialization for form inputs
if "form_user_id" not in st.session_state:
    st.session_state.form_user_id = "USER_101"
if "form_amount" not in st.session_state:
    st.session_state.form_amount = 42.50
if "form_merchant" not in st.session_state:
    st.session_state.form_merchant = "grocery"
if "form_card_network" not in st.session_state:
    st.session_state.form_card_network = "visa"
if "form_device" not in st.session_state:
    st.session_state.form_device = "trusted_device"
if "form_ip" not in st.session_state:
    st.session_state.form_ip = "clean_residential"
if "form_loc" not in st.session_state:
    st.session_state.form_loc = "home_location"
if "form_failed" not in st.session_state:
    st.session_state.form_failed = 0
if "form_txns_1h" not in st.session_state:
    st.session_state.form_txns_1h = 0
if "form_kyc" not in st.session_state:
    st.session_state.form_kyc = "fully_verified"
if "form_age_days" not in st.session_state:
    st.session_state.form_age_days = 320
if "form_child_safe" not in st.session_state:
    st.session_state.form_child_safe = False

with col_p1:
    if st.button("☕ Normal Coffee\n(Low Risk)", use_container_width=True):
        st.session_state.form_user_id = "USER_101"
        st.session_state.form_amount = 4.80
        st.session_state.form_merchant = "grocery"
        st.session_state.form_device = "trusted_device"
        st.session_state.form_ip = "clean_residential"
        st.session_state.form_loc = "home_location"
        st.session_state.form_failed = 0
        st.session_state.form_txns_1h = 0
        st.session_state.form_kyc = "fully_verified"
        st.session_state.form_age_days = 320
        st.session_state.form_child_safe = False
        st.rerun()

with col_p2:
    if st.button("🌱 Cold-Start New User\n(Adaptive Prior)", use_container_width=True):
        st.session_state.form_user_id = "USER_303"
        st.session_state.form_amount = 65.00
        st.session_state.form_merchant = "retail"
        st.session_state.form_device = "new_device"
        st.session_state.form_ip = "clean_residential"
        st.session_state.form_loc = "home_location"
        st.session_state.form_failed = 0
        st.session_state.form_txns_1h = 0
        st.session_state.form_kyc = "unverified"
        st.session_state.form_age_days = 2
        st.session_state.form_child_safe = False
        st.rerun()

with col_p3:
    if st.button("⚠️ Spending Spike\n(Step-up Verify)", use_container_width=True):
        st.session_state.form_user_id = "USER_101"
        st.session_state.form_amount = 480.00
        st.session_state.form_merchant = "electronics"
        st.session_state.form_device = "new_device"
        st.session_state.form_ip = "clean_residential"
        st.session_state.form_loc = "domestic_travel"
        st.session_state.form_failed = 1
        st.session_state.form_txns_1h = 2
        st.session_state.form_kyc = "fully_verified"
        st.session_state.form_age_days = 320
        st.session_state.form_child_safe = False
        st.rerun()

with col_p4:
    if st.button("🚨 Rapid Draining\n(High Risk Attack)", use_container_width=True):
        st.session_state.form_user_id = "USER_202"
        st.session_state.form_amount = 890.00
        st.session_state.form_merchant = "p2p_transfer"
        st.session_state.form_device = "new_device"
        st.session_state.form_ip = "vpn_proxy"
        st.session_state.form_loc = "domestic_travel"
        st.session_state.form_failed = 3
        st.session_state.form_txns_1h = 5
        st.session_state.form_kyc = "tier_1_verified"
        st.session_state.form_age_days = 45
        st.session_state.form_child_safe = False
        st.rerun()

with col_p5:
    if st.button("⛔ Casino / Tor\n(Blocked Fraud)", use_container_width=True):
        st.session_state.form_user_id = "USER_202"
        st.session_state.form_amount = 4500.00
        st.session_state.form_merchant = "gambling"
        st.session_state.form_device = "emulator_rooted"
        st.session_state.form_ip = "tor_blacklisted"
        st.session_state.form_loc = "impossible_velocity"
        st.session_state.form_failed = 4
        st.session_state.form_txns_1h = 6
        st.session_state.form_kyc = "unverified"
        st.session_state.form_age_days = 45
        st.session_state.form_child_safe = False
        st.rerun()

with col_p6:
    if st.button("🎮 Child Gaming Spend\n(Parental Shield)", use_container_width=True):
        st.session_state.form_user_id = "USER_101"
        st.session_state.form_amount = 89.99
        st.session_state.form_merchant = "gaming"
        st.session_state.form_device = "trusted_device"
        st.session_state.form_ip = "clean_residential"
        st.session_state.form_loc = "home_location"
        st.session_state.form_failed = 0
        st.session_state.form_txns_1h = 3
        st.session_state.form_kyc = "fully_verified"
        st.session_state.form_age_days = 320
        st.session_state.form_child_safe = True
        st.rerun()

st.divider()

# Input Configuration Form
st.markdown("### 📝 Transaction Risk Evaluation Form")

with st.form("transaction_eval_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 👤 Account & Transaction Details")
        user_profiles = db.list_user_profiles()
        user_options = {p["user_id"]: f"{p['user_id']} - {p['account_name']}" for p in user_profiles}
        user_ids = list(user_options.keys())

        curr_user_idx = user_ids.index(st.session_state.form_user_id) if st.session_state.form_user_id in user_ids else 0
        selected_user = st.selectbox(
            "Target Account Profile",
            options=user_ids,
            index=curr_user_idx,
            format_func=lambda x: user_options.get(x, x),
            help="Select an account to load historical baseline behavioral statistics",
        )

        amount_val = st.number_input(
            "Transaction Amount ($ USD)",
            min_value=0.50,
            max_value=100000.0,
            value=float(st.session_state.form_amount),
            step=10.0,
            format="%.2f",
        )

        merchant_options = [
            "grocery",
            "utilities",
            "retail",
            "gaming",
            "electronics",
            "travel_airline",
            "p2p_transfer",
            "luxury_jewelry",
            "crypto",
            "gambling",
        ]
        merchant_idx = merchant_options.index(st.session_state.form_merchant) if st.session_state.form_merchant in merchant_options else 2
        selected_merchant = st.selectbox(
            "Merchant Category",
            options=merchant_options,
            index=merchant_idx,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        card_network_options = ["visa", "mastercard", "discover", "american express"]
        selected_card_net = st.selectbox("Card Payment Network", options=card_network_options, index=0)

        child_safe_checked = st.checkbox(
            "🛡️ Enable Child-Safe Protection Shield",
            value=bool(st.session_state.get("form_child_safe", False)),
            help="Enforces parental biometric/OTP confirmation for gaming & digital micro-purchases",
        )

    with col2:
        st.markdown("##### 🌐 Contextual Gateway Indicators")
        device_opts = ["trusted_device", "new_device", "emulator_rooted"]
        dev_idx = device_opts.index(st.session_state.form_device) if st.session_state.form_device in device_opts else 0
        selected_device = st.selectbox(
            "Device Fingerprint Familiarity",
            options=device_opts,
            index=dev_idx,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        ip_opts = ["clean_residential", "datacenter_cloud", "vpn_proxy", "tor_blacklisted"]
        ip_idx = ip_opts.index(st.session_state.form_ip) if st.session_state.form_ip in ip_opts else 0
        selected_ip = st.selectbox(
            "IP Network Intelligence",
            options=ip_opts,
            index=ip_idx,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        loc_opts = ["home_location", "domestic_travel", "international_travel", "impossible_velocity"]
        loc_idx = loc_opts.index(st.session_state.form_loc) if st.session_state.form_loc in loc_opts else 0
        selected_loc = st.selectbox(
            "Geolocation Consistency",
            options=loc_opts,
            index=loc_idx,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        kyc_opts = ["fully_verified", "tier_1_verified", "unverified"]
        kyc_idx = kyc_opts.index(st.session_state.form_kyc) if st.session_state.form_kyc in kyc_opts else 0
        selected_kyc = st.selectbox(
            "KYC / Security Tier",
            options=kyc_opts,
            index=kyc_idx,
            format_func=lambda x: x.replace("_", " ").title(),
        )

    with col3:
        st.markdown("##### ⏱️ Behavioral & Velocity Inputs")
        failed_attempts_val = st.number_input(
            "Recent Failed PIN/OTP Attempts",
            min_value=0,
            max_value=10,
            value=int(st.session_state.form_failed),
            step=1,
            help="Preceding authentication retries in the last 24 hours",
        )

        txns_1h_val = st.number_input(
            "Transactions in Last 1 Hour",
            min_value=0,
            max_value=25,
            value=int(st.session_state.form_txns_1h),
            step=1,
            help="High velocity burst indicator",
        )

        account_age_val = st.number_input(
            "Account Age (Days)",
            min_value=0,
            max_value=3000,
            value=int(st.session_state.form_age_days),
            step=5,
        )

        txn_hour_val = st.slider(
            "Transaction Hour of Day (24h)",
            min_value=0,
            max_value=23,
            value=datetime.now().hour,
            help="Dormant nocturnal hours (01:00-05:00) carry temporal anomaly flags",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_submitted = st.form_submit_button(
        "⚡ Analyze Transaction Risk (Pre-Authorization)",
        use_container_width=True,
        type="primary",
    )

# Execution & Results Display
if analyze_submitted:
    txn_request = {
        "user_id": selected_user,
        "amount": amount_val,
        "merchant_category": selected_merchant,
        "card_network": selected_card_net,
        "device_status": selected_device,
        "ip_status": selected_ip,
        "location_status": selected_loc,
        "failed_attempts": failed_attempts_val,
        "txns_last_1h": txns_1h_val,
        "account_age_days": account_age_val,
        "hour_of_day": txn_hour_val,
        "kyc_status": selected_kyc,
        "child_safe_mode": child_safe_checked,
    }

    with st.spinner("Processing transaction through FinGuard Multi-Layer Risk Engine..."):
        result = decision_engine.evaluate(txn_request, save_record=True)

    st.success(f"Transaction Evaluated & Persisted: Record ID **{result['transaction_id']}**")

    # Primary Decision Header
    st.markdown("### 🎯 Transaction Decision & Risk Scoring Output")

    # Render Active Smart Shield Alerts
    if result.get("shields_active"):
        for s_alert in result.get("shield_alerts", []):
            st.markdown(
                f"""
                <div style="background-color: rgba(239, 68, 68, 0.12); border-left: 4px solid #ef4444; padding: 12px 18px; border-radius: 0 8px 8px 0; margin-bottom: 16px;">
                    <b style="color: #f87171; font-size: 1rem;">{s_alert['icon']} Smart Shield Triggered: {s_alert['shield']} ({s_alert['severity']})</b>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 4px; margin-bottom: 0;">
                        {s_alert['message']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    col_res_left, col_res_right = st.columns([4, 6])

    with col_res_left:
        # Radial Gauge
        gauge_fig = render_risk_gauge(result["dynamic_risk_score"])
        st.plotly_chart(gauge_fig, use_container_width=True)

        # Decision Badge & Recommended Action
        badge_class = f"badge-{result['decision'].lower()}"
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: -10px;">
                <span class="{badge_class}" style="font-size: 1.15rem;">
                    {result['risk_level']}: {result['decision']}
                </span>
                <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 10px; font-weight: 500;">
                    <b>Policy Action:</b> {result['recommended_action']}
                </p>
                <p style="color: #94a3b8; font-size: 0.85rem; padding: 0 10px;">
                    {result['decision_detail']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_res_right:
        # 3 Pillar Metric Cards
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(
                "ML Fraud Risk",
                f"{result['component_scores']['ml_risk_score']:.1f}/100",
                delta=f"Prob: {result['ml_probability']*100:.1f}%",
                help="Prediction from trained IEEE-CIS ML ensemble model",
            )
        with col_m2:
            st.metric(
                "Behavioral Risk",
                f"{result['component_scores']['behavioral_risk_score']:.1f}/100",
                delta="Cold-Start" if result["is_cold_start"] else "Established",
                delta_color="off",
                help="Deviation from user spending history, velocity, and timing",
            )
        with col_m3:
            st.metric(
                "Contextual Risk",
                f"{result['component_scores']['contextual_risk_score']:.1f}/100",
                delta=result.get("primary_driver", "Gateway"),
                delta_color="off",
                help="Gateway threat indicators (device, IP reputation, location, KYC)",
            )

        # Signal Contribution Breakdown Chart
        contributions = {
            f"ML Engine ({result['weights_used']['ml_weight']*100:.0f}%)": result["component_contributions"]["ml_contribution_points"],
            f"Behavioral ({result['weights_used']['behavioral_weight']*100:.0f}%)": result["component_contributions"]["behavioral_contribution_points"],
            f"Contextual ({result['weights_used']['contextual_weight']*100:.0f}%)": result["component_contributions"]["contextual_contribution_points"],
        }
        contrib_chart = render_contribution_bar(contributions)
        st.plotly_chart(contrib_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Explainability & Contributing Factors Section
    st.markdown("#### 🔍 Explainable AI & Contributing Factors")

    if result["is_cold_start"]:
        st.markdown("""
        <div style="background-color: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 16px; border-radius: 0 6px 6px 0; margin-bottom: 12px; font-size: 0.88rem; color: #fde68a;">
            🌱 <b>Cold-Start Adaptive Assessment Active:</b> Account lacks sufficient historical spending transactions. Dynamic risk weights were rebalanced towards contextual gateway signals and a calibrated neutral-prudent prior.
        </div>
        """, unsafe_allow_html=True)

    factors = result.get("explanation_factors", [])
    if factors:
        for f in factors:
            f_lower = f.lower()
            if any(w in f_lower for w in ["severe", "critical", "high-risk", "brute-force", "burst", "impossible", "blocked"]):
                css_class = "factor-item-alert"
                icon = "🚨"
            elif any(w in f_lower for w in ["elevated", "moderate", "abnormal", "retry", "deviation", "cold-start", "new device", "unusual", "unverified"]):
                css_class = "factor-item-warn"
                icon = "⚠️"
            else:
                css_class = "factor-item-pass"
                icon = "✅"

            st.markdown(
                f"""
                <div class="{css_class}">
                    <b>{icon}</b> {f}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No notable risk anomalies detected. Clean baseline transaction profile.")
