"""
FinGuard AI - Federated Learning Consortium Simulation
Demonstrates privacy-preserving collaborative fraud detection across 3 regional bank nodes
using the Federated Averaging (FedAvg) algorithm without sharing raw customer PII.
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

from src.ui_components import apply_custom_theme
from src.federated_simulation import get_federated_simulator

st.set_page_config(
    page_title="Federated Learning - FinGuard AI",
    page_icon="🌐",
    layout="wide",
)

apply_custom_theme()
fed_sim = get_federated_simulator()

st.title("🌐 Privacy-Preserving Federated Machine Learning")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Multi-Bank Collaborative Fraud Detection using Federated Averaging (FedAvg). "
    "Institutions collaborate on global threat patterns with <b>zero raw customer data sharing</b>."
    "</p>",
    unsafe_allow_html=True,
)

# Academic Research Badge
st.markdown("""
<div style="background-color: rgba(56, 189, 248, 0.08); border-left: 3px solid #38bdf8; padding: 12px 18px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 0.9rem; color: #e0f2fe;">
    🎓 <b>Research Innovation (IEEE Proposal):</b> Addresses stringent banking privacy regulations (GDPR, RBI DPDP Act). 
    Rather than pooling sensitive customer financial records into a vulnerable central repository, FinGuard AI transmits 
    strictly encrypted mathematical weight updates ($\Delta W$), keeping raw transactions isolated within each bank's firewall.
</div>
""", unsafe_allow_html=True)

# Architecture Diagram
st.markdown("### 🏛️ Consortium Architecture")
st.markdown("""
<div class="finguard-card" style="text-align: center;">
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;">
        <div style="background: #1e293b; border: 1px solid #334155; padding: 15px 20px; border-radius: 10px; width: 280px; text-align: left;">
            <b style="color: #38bdf8; font-size: 1rem;">🏦 Bank Alpha</b>
            <p style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0;">Metropolitan Retail Bank</p>
            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.78rem; padding: 2px 8px; border-radius: 4px;">Data: 45% (Isolated)</span>
            <p style="color: #cbd5e1; font-size: 0.8rem; margin-top: 8px; margin-bottom: 0;">Local SGD Fit ➔ Sends Encrypted $\Delta W_1$</p>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; padding: 15px 20px; border-radius: 10px; width: 280px; text-align: left;">
            <b style="color: #818cf8; font-size: 1rem;">📱 Bank Beta</b>
            <p style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0;">Digital Neo-Bank / Fintech</p>
            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.78rem; padding: 2px 8px; border-radius: 4px;">Data: 35% (Isolated)</span>
            <p style="color: #cbd5e1; font-size: 0.8rem; margin-top: 8px; margin-bottom: 0;">Local SGD Fit ➔ Sends Encrypted $\Delta W_2$</p>
        </div>
        <div style="background: #1e293b; border: 1px solid #334155; padding: 15px 20px; border-radius: 10px; width: 280px; text-align: left;">
            <b style="color: #c084fc; font-size: 1rem;">💳 Bank Gamma</b>
            <p style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0;">Merchant Acquiring Bank</p>
            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.78rem; padding: 2px 8px; border-radius: 4px;">Data: 20% (Isolated)</span>
            <p style="color: #cbd5e1; font-size: 0.8rem; margin-top: 8px; margin-bottom: 0;">Local SGD Fit ➔ Sends Encrypted $\Delta W_3$</p>
        </div>
    </div>
    <div style="background: rgba(56, 189, 248, 0.1); border: 1px dashed #38bdf8; padding: 14px; border-radius: 8px; max-width: 650px; margin: 0 auto;">
        <b style="color: #f8fafc; font-size: 0.95rem;">🛡️ FinGuard Central Aggregator (FedAvg)</b>
        <p style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0;">
            $W_{global} = \\sum_{k=1}^K \\frac{n_k}{N} W_k$ &nbsp;|&nbsp; Zero Customer Records Transferred
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Interactive Simulation Controls
st.markdown("### ⚡ Live Federated Training Cycle")
col_act1, col_act2, col_act3 = st.columns([3, 3, 4])

with col_act1:
    if st.button("🚀 Execute FedAvg Training Round", use_container_width=True, type="primary"):
        with st.spinner("Executing local node updates and FedAvg aggregation..."):
            current_round = len(fed_sim.rounds_history) + 1
            fed_sim.run_federated_round(current_round)
            st.success(f"Federated Round {current_round} executed successfully!")
            st.rerun()

with col_act2:
    if st.button("🔄 Reset Consortium Simulation", use_container_width=True):
        fed_sim.global_weights = None
        fed_sim.rounds_history = []
        st.info("Consortium state reset.")
        st.rerun()

# Display Simulation History & Metrics
if fed_sim.rounds_history:
    df_history = pd.DataFrame(fed_sim.rounds_history)
    latest = fed_sim.rounds_history[-1]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📈 Latest Round Telemetry")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Completed Rounds", len(fed_sim.rounds_history))
    with k2:
        st.metric("Global ROC-AUC", f"{latest['global_roc_auc']:.4f}", delta=f"+{(latest['global_roc_auc'] - latest['single_isolated_bank_auc']):.4f} vs Isolated Bank")
    with k3:
        st.metric("Global F1-Score", f"{latest['global_f1']:.4f}")
    with k4:
        st.metric("Raw PII Transferred", "0 records", delta="100% Privacy Compliant", delta_color="normal")

    # Convergence Chart
    st.markdown("#### 📊 Convergence & Collaborative Advantage")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_roc = px.line(
            df_history,
            x="round",
            y=["global_roc_auc", "single_isolated_bank_auc"],
            markers=True,
            labels={"value": "ROC-AUC Score", "round": "Federated Training Round", "variable": "Model Strategy"},
            color_discrete_map={
                "global_roc_auc": "#38bdf8",
                "single_isolated_bank_auc": "#ef4444",
            },
        )
        fig_roc.update_layout(
            title="<b>Federated Consensus vs Isolated Single-Bank Model</b>",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            xaxis=dict(gridcolor="#1e293b", dtick=1),
            yaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with col_chart2:
        fig_comp = go.Figure(data=[
            go.Bar(name='Isolated Single Bank', x=df_history['round'], y=df_history['single_isolated_bank_auc'], marker_color='#64748b'),
            go.Bar(name='FinGuard FedAvg Global', x=df_history['round'], y=df_history['global_roc_auc'], marker_color='#10b981')
        ])
        fig_comp.update_layout(
            barmode='group',
            title="<b>ROC-AUC Gain through Privacy-Preserving Collaboration</b>",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            xaxis=dict(title="Round", gridcolor="#1e293b", dtick=1),
            yaxis=dict(title="ROC-AUC", gridcolor="#1e293b"),
            margin=dict(l=20, r=20, t=35, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # Round Summary Table
    st.markdown("#### 📋 Training Round Ledger")
    st.dataframe(
        df_history[["round", "global_roc_auc", "single_isolated_bank_auc", "global_f1", "global_accuracy", "total_collaborative_samples", "pii_records_shared"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "round": "Round #",
            "global_roc_auc": "Global ROC-AUC",
            "single_isolated_bank_auc": "Isolated Bank AUC",
            "global_f1": "Global F1",
            "global_accuracy": "Accuracy",
            "total_collaborative_samples": "Consortium Samples",
            "pii_records_shared": "PII Transferred",
        },
    )
else:
    st.info("Click 'Execute FedAvg Training Round' above to initiate the first collaborative training cycle.")
