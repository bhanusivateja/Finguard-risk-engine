"""
FinGuard AI - UI Components & Styling Module
Provides modern dark-themed banking cybersecurity styling, custom CSS,
Plotly gauges, and risk factor visualization cards for Streamlit.
"""

import plotly.graph_objects as go
import streamlit as st


def apply_custom_theme():
    """Injects high-end banking cybersecurity CSS styling."""
    custom_css = """
    <style>
        /* Global Background & Font */
        .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Top Header Styling */
        header[data-testid="stHeader"] {
            background-color: rgba(11, 15, 25, 0.85);
            backdrop-filter: blur(8px);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #080c14;
            border-right: 1px solid #1e293b;
        }
        section[data-testid="stSidebar"] .stMarkdown h1, 
        section[data-testid="stSidebar"] .stMarkdown h2, 
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #38bdf8;
        }

        /* Metric Card Boxes */
        div[data-testid="stMetric"] {
            background-color: #131b2e;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 14px 18px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        /* Cards & Containers */
        .finguard-card {
            background-color: #131b2e;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
        }

        /* Decision Banner Badges */
        .badge-allow {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.35) 100%);
            border: 1px solid #10b981;
            color: #34d399;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            display: inline-block;
            letter-spacing: 0.5px;
        }
        .badge-verify {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.35) 100%);
            border: 1px solid #f59e0b;
            color: #fbbf24;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            display: inline-block;
            letter-spacing: 0.5px;
        }
        .badge-block {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.35) 100%);
            border: 1px solid #ef4444;
            color: #f87171;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            display: inline-block;
            letter-spacing: 0.5px;
        }

        /* Factor Explanation Items */
        .factor-item-alert {
            background-color: rgba(239, 68, 68, 0.08);
            border-left: 3px solid #ef4444;
            padding: 8px 14px;
            margin-bottom: 8px;
            border-radius: 0 6px 6px 0;
            font-size: 0.92rem;
            color: #fca5a5;
        }
        .factor-item-warn {
            background-color: rgba(245, 158, 11, 0.08);
            border-left: 3px solid #f59e0b;
            padding: 8px 14px;
            margin-bottom: 8px;
            border-radius: 0 6px 6px 0;
            font-size: 0.92rem;
            color: #fde68a;
        }
        .factor-item-pass {
            background-color: rgba(16, 185, 129, 0.08);
            border-left: 3px solid #10b981;
            padding: 8px 14px;
            margin-bottom: 8px;
            border-radius: 0 6px 6px 0;
            font-size: 0.92rem;
            color: #a7f3d0;
        }

        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            border-color: #38bdf8;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_risk_gauge(score: float, title: str = "Dynamic Risk Score"):
    """Creates a high-precision Plotly radial gauge for risk scores (0-100)."""
    # Color logic
    if score < 30.0:
        bar_color = "#10b981"  # Emerald green
    elif score < 70.0:
        bar_color = "#f59e0b"  # Amber orange
    else:
        bar_color = "#ef4444"  # Rose red

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 36, "color": "#f8fafc", "family": "Inter"}},
            title={"text": f"<b>{title}</b>", "font": {"size": 18, "color": "#94a3b8"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "#1e293b",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 30], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [30, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 100], "color": "rgba(239, 68, 68, 0.20)"},
                ],
                "threshold": {
                    "line": {"color": "#f87171", "width": 3},
                    "thickness": 0.8,
                    "value": 70,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=25, r=25, t=35, b=15),
    )
    return fig


def render_contribution_bar(contributions: dict):
    """Renders a horizontal bar breakdown of score contributions."""
    labels = list(contributions.keys())
    values = [round(v, 2) for v in contributions.values()]

    colors = ["#38bdf8", "#818cf8", "#c084fc"]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors[: len(labels)], line=dict(color="#0f172a", width=1.5)),
            text=[f"{v:.1f} pts" for v in values],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="<b>Dynamic Risk Contribution (Points by Signal)</b>",
        title_font=dict(size=14, color="#94a3b8"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Points Contributed (out of 100)",
            gridcolor="#1e293b",
            color="#94a3b8",
            range=[0, max(max(values) + 10, 45)],
        ),
        yaxis=dict(color="#e2e8f0"),
        height=200,
        margin=dict(l=10, r=10, t=35, b=25),
    )
    return fig
