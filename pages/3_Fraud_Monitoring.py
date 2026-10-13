"""
FinGuard AI - Fraud Monitoring Ledger & Forensic Inspection
Filter, inspect, and analyze all evaluated banking transactions.
Displays risk level classifications, factor explanations, and forensic transaction drill-downs.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pandas as pd
import streamlit as st

import config
from src.ui_components import apply_custom_theme, render_risk_gauge
from src.storage import get_database_manager

st.set_page_config(
    page_title="Fraud Monitoring - FinGuard AI",
    page_icon="🚨",
    layout="wide",
)

apply_custom_theme()
db = get_database_manager()

st.title("🚨 Fraud Monitoring & Audit Ledger")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Forensic inspection terminal: Real-time ledger of evaluated transactions with automated threat categorization."
    "</p>",
    unsafe_allow_html=True,
)

# Fetch transactions
all_txns = db.get_recent_transactions(limit=300)

if not all_txns:
    st.info("No transaction records found in the audit ledger.")
    st.stop()

df = pd.DataFrame(all_txns)

# Filter Controls
st.markdown("#### 🔍 Filter & Search Parameters")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    risk_filter = st.selectbox(
        "Risk Level",
        options=["ALL", "HIGH RISK", "MEDIUM RISK", "LOW RISK"],
        index=0,
    )

with f_col2:
    decision_filter = st.selectbox(
        "Policy Decision",
        options=["ALL", "BLOCK", "VERIFY", "ALLOW"],
        index=0,
    )

with f_col3:
    categories = ["ALL"] + sorted(list(df["merchant_category"].dropna().unique()))
    cat_filter = st.selectbox("Merchant Category", options=categories, index=0)

with f_col4:
    search_query = st.text_input("Search (Txn ID or User ID)", value="", placeholder="e.g. USER_202 or TXN-1003")

# Apply Filters
filtered_df = df.copy()

if risk_filter != "ALL":
    filtered_df = filtered_df[filtered_df["risk_level"] == risk_filter]

if decision_filter != "ALL":
    filtered_df = filtered_df[filtered_df["decision"] == decision_filter]

if cat_filter != "ALL":
    filtered_df = filtered_df[filtered_df["merchant_category"] == cat_filter]

if search_query:
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["transaction_id"].str.lower().str.contains(q)
        | filtered_df["user_id"].str.lower().str.contains(q)
    ]

# Summary Metrics for Filtered Set
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Records Found", len(filtered_df))
with m2:
    blocked_count = len(filtered_df[filtered_df["decision"] == config.DECISION_BLOCK])
    st.metric("Flagged / Blocked", blocked_count)
with m3:
    verify_count = len(filtered_df[filtered_df["decision"] == config.DECISION_VERIFY])
    st.metric("Step-up Verifications", verify_count)
with m4:
    avg_score = filtered_df["dynamic_risk_score"].mean() if not filtered_df.empty else 0.0
    st.metric("Average Risk Score", f"{avg_score:.1f}/100")

st.markdown("<br>", unsafe_allow_html=True)

# Transaction Table
st.markdown("#### 📋 Evaluated Transactions Ledger")

if filtered_df.empty:
    st.warning("No transactions match the selected filters.")
else:
    table_df = filtered_df[
        [
            "transaction_id",
            "timestamp",
            "user_id",
            "amount",
            "merchant_category",
            "dynamic_risk_score",
            "risk_level",
            "decision",
            "is_cold_start",
        ]
    ].copy()

    table_df["amount"] = table_df["amount"].apply(lambda x: f"${x:,.2f}")
    table_df["dynamic_risk_score"] = table_df["dynamic_risk_score"].apply(lambda x: f"{x:.1f}")
    table_df["is_cold_start"] = table_df["is_cold_start"].apply(lambda x: "Yes 🌱" if x == 1 else "No")

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_id": "Transaction ID",
            "timestamp": "Timestamp",
            "user_id": "Account ID",
            "amount": "Amount",
            "merchant_category": "Merchant Category",
            "dynamic_risk_score": "Risk Score",
            "risk_level": "Risk Level",
            "decision": "Decision",
            "is_cold_start": "Cold Start",
        },
    )

    # Export to CSV
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Ledger to CSV (Audit Trail)",
        data=csv_bytes,
        file_name="finguard_fraud_audit_ledger.csv",
        mime="text/csv",
    )

st.divider()

# Deep Dive Transaction Inspector
st.markdown("### 🔬 Forensic Transaction Inspector")
st.markdown(
    "<span style='color: #94a3b8; font-size: 0.88rem;'>Select a specific transaction ID to inspect its comprehensive factor breakdown and raw signal parameters:</span>",
    unsafe_allow_html=True,
)

txn_ids = filtered_df["transaction_id"].tolist() if not filtered_df.empty else df["transaction_id"].tolist()
selected_inspect_id = st.selectbox("Inspect Transaction ID", options=txn_ids)

if selected_inspect_id:
    txn_row = df[df["transaction_id"] == selected_inspect_id].iloc[0]

    insp_col1, insp_col2 = st.columns([4, 6])

    with insp_col1:
        score_val = float(txn_row["dynamic_risk_score"])
        gauge = render_risk_gauge(score_val, title="Dynamic Risk Score")
        st.plotly_chart(gauge, use_container_width=True)

        badge_class = f"badge-{txn_row['decision'].lower()}"
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: -10px;">
                <span class="{badge_class}" style="font-size: 1.1rem;">
                    {txn_row['risk_level']}: {txn_row['decision']}
                </span>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 8px;">
                    Amount: <b>${txn_row['amount']:,.2f}</b> | Account: <b>{txn_row['user_id']}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insp_col2:
        st.markdown("##### 🧩 Signal Pillars Breakdown")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("ML Fraud Risk", f"{txn_row.get('ml_risk_score', 0.0):.1f}/100")
        with p2:
            st.metric("Behavioral Risk", f"{txn_row.get('behavioral_risk_score', 0.0):.1f}/100")
        with p3:
            st.metric("Contextual Risk", f"{txn_row.get('contextual_risk_score', 0.0):.1f}/100")

        st.markdown("##### 📝 Explanatory Factor Log")
        raw_factors = txn_row.get("factors_json", "[]")
        try:
            factors_list = json.loads(raw_factors) if isinstance(raw_factors, str) else raw_factors
        except Exception:
            factors_list = []

        if factors_list:
            for fact in factors_list:
                f_low = fact.lower()
                if any(w in f_low for w in ["severe", "critical", "high-risk", "brute-force", "burst", "impossible", "blocked"]):
                    css = "factor-item-alert"
                    ic = "🚨"
                elif any(w in f_low for w in ["elevated", "moderate", "abnormal", "retry", "deviation", "cold-start", "new device", "unusual", "unverified"]):
                    css = "factor-item-warn"
                    ic = "⚠️"
                else:
                    css = "factor-item-pass"
                    ic = "✅"

                st.markdown(f"<div class='{css}'><b>{ic}</b> {fact}</div>", unsafe_allow_html=True)
        else:
            st.info("No specific factor flags logged for this transaction.")

    # Expandable Raw JSON payload
    with st.expander("🛠️ View Raw Stored Record Payload (JSON)"):
        st.json(dict(txn_row))
