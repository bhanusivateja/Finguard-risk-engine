"""
FinGuard AI - Executive Fraud Operations Dashboard
Visualizes transaction volumes, dynamic risk score distributions,
flagged fraudulent transactions, and real-time security telemetry.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config
from src.ui_components import apply_custom_theme
from src.storage import get_database_manager

st.set_page_config(
    page_title="Executive Dashboard - FinGuard AI",
    page_icon="📊",
    layout="wide",
)

apply_custom_theme()
db = get_database_manager()

st.title("📊 Executive Banking Security Dashboard")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Real-time fraud operations command center: Transaction volumes, dynamic risk distribution, and threat velocity."
    "</p>",
    unsafe_allow_html=True,
)

# Demarcation notice
st.markdown("""
<div style="background-color: rgba(56, 189, 248, 0.08); border-left: 3px solid #38bdf8; padding: 10px 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 0.88rem; color: #bae6fd;">
    ℹ️ <b>Operational Data Source:</b> Displays live evaluated transactions stored in the persistent database, alongside benchmark distributions from the IEEE-CIS Fraud Detection dataset.
</div>
""", unsafe_allow_html=True)

# Fetch database metrics & recent transactions
metrics = db.get_dashboard_metrics()
recent_txns = db.get_recent_transactions(limit=100)
df_txns = pd.DataFrame(recent_txns) if recent_txns else pd.DataFrame()

# Top KPI Metric Cards
c1, c2, c3, c4, c5 = st.columns(5)
total_count = metrics["total_transactions"]
blocked_count = metrics["blocked_transactions"]
fraud_rate = (blocked_count / max(total_count, 1)) * 100.0

with c1:
    st.metric("Total Evaluated", f"{total_count:,}", help="Total transactions processed through the dynamic risk engine")
with c2:
    st.metric("Avg Risk Score", f"{metrics['average_risk_score']:.1f}/100", help="Mean dynamic composite risk score across all sessions")
with c3:
    st.metric("Blocked Frauds", f"{blocked_count:,}", delta=f"{fraud_rate:.1f}% rate", delta_color="inverse", help="Transactions categorized as HIGH RISK and declined")
with c4:
    st.metric("Step-up Verifications", f"{metrics['verified_transactions']:,}", help="Medium-risk transactions requiring 2FA or biometric challenge")
with c5:
    st.metric("Clean Approvals", f"{metrics['allowed_transactions']:,}", help="Low-risk transactions approved seamlessly")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 1: Distribution & Donut
col_left, col_right = st.columns([6, 4])

with col_left:
    st.markdown("#### 📈 Dynamic Risk Score Distribution")
    if not df_txns.empty:
        fig_dist = px.histogram(
            df_txns,
            x="dynamic_risk_score",
            nbins=20,
            color="risk_level",
            color_discrete_map={
                "LOW RISK": "#10b981",
                "MEDIUM RISK": "#f59e0b",
                "HIGH RISK": "#ef4444",
            },
            labels={"dynamic_risk_score": "Dynamic Risk Score (0-100)", "count": "Transactions"},
        )
        fig_dist.add_vline(x=config.THRESHOLD_LOW_RISK, line_dash="dash", line_color="#38bdf8", annotation_text="Low Cutoff (30)")
        fig_dist.add_vline(x=config.THRESHOLD_MEDIUM_RISK, line_dash="dash", line_color="#ef4444", annotation_text="High Cutoff (70)")
        fig_dist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            xaxis=dict(gridcolor="#1e293b", range=[0, 100]),
            yaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No transaction data available to plot distribution.")

with col_right:
    st.markdown("#### 🎯 Decision Breakdown")
    if not df_txns.empty:
        decision_counts = df_txns["decision"].value_counts().reset_index()
        decision_counts.columns = ["decision", "count"]
        fig_pie = px.pie(
            decision_counts,
            values="count",
            names="decision",
            hole=0.55,
            color="decision",
            color_discrete_map={
                "ALLOW": "#10b981",
                "VERIFY": "#f59e0b",
                "BLOCK": "#ef4444",
            },
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No transaction data available.")

# Visualizations Row 2: Merchant Category Risk
st.markdown("#### 🏪 Merchant Category vs Risk Intensity")
if not df_txns.empty and "merchant_category" in df_txns.columns:
    cat_summary = (
        df_txns.groupby("merchant_category")
        .agg(
            count=("transaction_id", "count"),
            avg_risk=("dynamic_risk_score", "mean"),
        )
        .reset_index()
    )
    cat_summary["avg_risk"] = cat_summary["avg_risk"].round(1)

    fig_bar = px.bar(
        cat_summary,
        x="merchant_category",
        y="avg_risk",
        color="avg_risk",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        text="avg_risk",
        labels={"merchant_category": "Merchant Industry", "avg_risk": "Avg Dynamic Risk Score"},
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        xaxis=dict(gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b", range=[0, 100]),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Recent Live Transaction Feed Table
st.markdown("#### 📋 Recent Evaluated Transactions Feed")
if not df_txns.empty:
    display_df = df_txns[
        [
            "transaction_id",
            "timestamp",
            "user_id",
            "amount",
            "merchant_category",
            "dynamic_risk_score",
            "risk_level",
            "decision",
        ]
    ].copy()
    display_df["amount"] = display_df["amount"].apply(lambda v: f"${v:,.2f}")
    display_df["dynamic_risk_score"] = display_df["dynamic_risk_score"].apply(lambda v: f"{v:.1f}/100")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_id": "Txn ID",
            "timestamp": "Timestamp",
            "user_id": "Account",
            "amount": "Amount",
            "merchant_category": "Category",
            "dynamic_risk_score": "Risk Score",
            "risk_level": "Risk Level",
            "decision": "Decision",
        },
    )
else:
    st.info("No recent transactions recorded.")
