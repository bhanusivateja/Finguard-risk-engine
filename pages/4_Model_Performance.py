"""
FinGuard AI - Model Performance & Research Evaluation
Presents empirical benchmarking results from training on the IEEE-CIS Fraud Detection dataset.
Includes comparative model metrics, confusion matrix heatmap, and feature importance analysis.
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config
from src.ui_components import apply_custom_theme

st.set_page_config(
    page_title="Model Performance - FinGuard AI",
    page_icon="🧠",
    layout="wide",
)

apply_custom_theme()

st.title("🧠 Machine Learning Model Performance & Evaluation")
st.markdown(
    "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
    "Empirical benchmarks trained on the IEEE-CIS Fraud Detection dataset. Zero fabricated metrics."
    "</p>",
    unsafe_allow_html=True,
)

# Load saved model artifacts
comparison_file = config.MODEL_COMPARISON_PATH
metadata_file = config.MODEL_METADATA_PATH
feature_file = config.FEATURE_IMPORTANCE_PATH

has_artifacts = comparison_file.exists() and metadata_file.exists() and feature_file.exists()

if not has_artifacts:
    st.warning("Model evaluation artifacts not detected. Please train the model pipeline.")
    if st.button("🚀 Run Model Training Pipeline Now", type="primary"):
        with st.spinner("Training Random Forest, Gradient Boosting, and XGBoost on IEEE-CIS dataset..."):
            from src.train_model import train_finguard_model
            train_finguard_model()
            st.success("Models trained successfully! Refreshing page...")
            st.rerun()
    st.stop()

with open(comparison_file, "r", encoding="utf-8") as f:
    comparison_data = json.load(f)

with open(metadata_file, "r", encoding="utf-8") as f:
    metadata_data = json.load(f)

with open(feature_file, "r", encoding="utf-8") as f:
    feature_importance_data = json.load(f)

selected_model_name = metadata_data.get("selected_model", "Random Forest")
best_metrics = metadata_data.get("metrics", {})

# Top Summary KPIs
st.markdown("#### 🏆 Optimal Production Model Summary")
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric("Selected Model", selected_model_name)
with c2:
    st.metric("ROC-AUC", f"{best_metrics.get('roc_auc', 0.0):.4f}")
with c3:
    st.metric("PR-AUC", f"{best_metrics.get('pr_auc', 0.0):.4f}")
with c4:
    st.metric("Recall (Fraud)", f"{best_metrics.get('recall', 0.0)*100:.1f}%")
with c5:
    st.metric("Precision", f"{best_metrics.get('precision', 0.0)*100:.1f}%")
with c6:
    st.metric("Overall Accuracy", f"{best_metrics.get('accuracy', 0.0)*100:.2f}%")

st.markdown("<br>", unsafe_allow_html=True)

# Comparative Benchmark Table
st.markdown("### 📊 Multi-Model Comparative Benchmark")
st.markdown(
    "<span style='color: #94a3b8; font-size: 0.88rem;'>Evaluated on the IEEE-CIS test partition under identical preprocessing and stratified class conditions:</span>",
    unsafe_allow_html=True,
)

comp_rows = []
for model_name, m in comparison_data.items():
    is_best = "⭐ (Selected)" if model_name == selected_model_name else ""
    comp_rows.append({
        "Model Architecture": f"{model_name} {is_best}",
        "Accuracy": f"{m['accuracy']*100:.2f}%",
        "Precision": f"{m['precision']*100:.2f}%",
        "Recall": f"{m['recall']*100:.2f}%",
        "F1-Score": f"{m['f1_score']:.4f}",
        "ROC-AUC": f"{m['roc_auc']:.4f}",
        "PR-AUC": f"{m['pr_auc']:.4f}",
    })

df_comp = pd.DataFrame(comp_rows)
st.dataframe(df_comp, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations: Confusion Matrix & Feature Importance
col_vis_left, col_vis_right = st.columns([5, 5])

with col_vis_left:
    st.markdown(f"#### 🔍 Confusion Matrix ({selected_model_name})")
    cm_dict = best_metrics.get("confusion_matrix", {})
    tn = cm_dict.get("true_negatives", 0)
    fp = cm_dict.get("false_positives", 0)
    fn = cm_dict.get("false_negatives", 0)
    tp = cm_dict.get("true_positives", 0)

    z_vals = [[tn, fp], [fn, tp]]
    x_labels = ["Predicted Legitimate", "Predicted Fraud"]
    y_labels = ["Actual Legitimate", "Actual Fraud"]

    # Annotations
    ann_text = [
        [f"TN: {tn:,}<br>(True Clean)", f"FP: {fp:,}<br>(False Alarm)"],
        [f"FN: {fn:,}<br>(Missed Fraud)", f"TP: {tp:,}<br>(Caught Fraud)"],
    ]

    fig_cm = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=x_labels,
            y=y_labels,
            text=ann_text,
            texttemplate="%{text}",
            textfont={"size": 13, "color": "#f8fafc"},
            colorscale=[[0, "#1e293b"], [0.5, "#0284c7"], [1, "#0369a1"]],
            showscale=False,
        )
    )

    fig_cm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=320,
        margin=dict(l=30, r=20, t=30, b=20),
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_cm, use_container_width=True)

with col_vis_right:
    st.markdown("#### 🌟 Top IEEE-CIS Feature Importances")
    if feature_importance_data:
        top_features = list(feature_importance_data.items())[:12]
        df_feats = pd.DataFrame(top_features, columns=["Feature", "Importance"])
        df_feats = df_feats.sort_values(by="Importance", ascending=True)

        fig_feat = px.bar(
            df_feats,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale="Viridis",
        )

        fig_feat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
        )
        st.plotly_chart(fig_feat, use_container_width=True)

st.divider()

# Technical Methodology Notes
st.markdown("### 🔬 Academic Methodology & Engineering Details")
col_tech1, col_tech2 = st.columns(2)

with col_tech1:
    st.markdown("""
    <div class="finguard-card">
        <h4 style="color: #38bdf8; margin-top: 0;">1. Class Imbalance Mitigation</h4>
        <p style="color: #94a3b8; font-size: 0.88rem;">
            Financial fraud datasets typically exhibit extreme class rarity (~3.5% fraud prevalence). 
            FinGuard AI addresses this challenge using:
        </p>
        <ul style="color: #cbd5e1; font-size: 0.85rem;">
            <li><b>Class Weight Tuning:</b> <code>class_weight='balanced'</code> penalty on minority fraud misclassifications.</li>
            <li><b>Gradient Boost Scale Pos Weight:</b> In XGBoost, <code>scale_pos_weight = N_neg / N_pos</code> balances gradient steps.</li>
            <li><b>Stratified Splits:</b> Ensures identical fraud prevalence across training and test partitions.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_tech2:
    st.markdown("""
    <div class="finguard-card">
        <h4 style="color: #38bdf8; margin-top: 0;">2. Data Leakage Prevention</h4>
        <p style="color: #94a3b8; font-size: 0.88rem;">
            Zero data leakage is enforced through a strictly encapsulated Scikit-learn ColumnTransformer pipeline:
        </p>
        <ul style="color: #cbd5e1; font-size: 0.85rem;">
            <li><b>Imputation & Scaling:</b> Median imputers and scalers fit strictly on the training partition.</li>
            <li><b>Safe Ordinal Categorical Encoding:</b> Unseen test and live inference categories map to <code>-1</code>.</li>
            <li><b>Target Isolation:</b> Feature matrices are strictly decoupled from labels before transformation.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Retraining option for evaluation defense
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("⚙️ Retrain Machine Learning Pipeline On-Demand"):
    st.markdown("Faculty examiners or evaluators can trigger a live retraining cycle to observe real-time fitting:")
    if st.button("🔄 Execute Live Model Retraining", type="secondary"):
        with st.spinner("Retraining Random Forest, HistGradientBoosting, and XGBoost..."):
            from src.train_model import train_finguard_model
            train_finguard_model()
            st.success("Retraining complete! Model artifacts refreshed.")
            st.rerun()
