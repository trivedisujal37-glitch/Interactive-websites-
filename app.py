"""Supply Chain Optimization System - Streamlit Application.

Anshu's portion: Cost Analysis, Optimization, Recommendations, Reporting, Export & App Integration.
"""

import pandas as pd
import streamlit as st

from modules.cost import analyze_cost
from modules.optimization import run_optimization
from modules.recommendations import HUMAN_REVIEW_TEXT, build_recommendations
from streamlit_option_menu import option_menu
from utils.export import (
    export_to_csv,
    export_to_excel,
    get_available_export_formats,
)

st.set_page_config(page_title="Supply Chain Optimization System", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Obsidian Theme */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .stApp {
        background-color: #0b0f17 !important;
        background-image:
            radial-gradient(circle at 10% 12%, rgba(0, 212, 255, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 90% 18%, rgba(236, 72, 153, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 50% 85%, rgba(59, 130, 246, 0.03) 0%, transparent 50%) !important;
        color: #e2e8f0 !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }

    /* Top Brand & Header Bar */
    .zentra-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 6px 14px 6px;
        margin-bottom: 4px;
    }
    .zentra-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
    }
    .zentra-brand-text {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .zentra-header-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .zentra-tool-btn {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: rgba(22, 30, 48, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }
    .zentra-tool-btn:hover {
        background: rgba(30, 41, 65, 0.95);
        color: #ffffff;
        border-color: rgba(0, 212, 255, 0.4);
        box-shadow: 0 0 12px rgba(0, 212, 255, 0.2);
    }
    .red-dot {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 6px;
        height: 6px;
        background: #ef4444;
        border-radius: 50%;
        box-shadow: 0 0 6px #ef4444;
    }
    .zentra-avatar-pill {
        display: flex;
        align-items: center;
    }
    .avatar-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 50%, #00d4ff 100%);
        padding: 2px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 800;
        color: #ffffff;
    }

    /* Glass Cards */
    div[data-testid="stVerticalBlockBorderWrapper"], .zentra-glass-card {
        background: rgba(18, 24, 38, 0.72) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        padding: 14px 18px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover, .zentra-glass-card:hover {
        border-color: rgba(0, 212, 255, 0.22) !important;
        box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.75), 0 0 20px rgba(0, 212, 255, 0.06) !important;
    }

    /* Overview Header */
    .zentra-overview-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 6px 0 18px 0;
        flex-wrap: wrap;
        gap: 12px;
    }
    .overview-title-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .overview-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.8px;
    }
    .overview-link-icon {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
    }
    .overview-ctrls-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ctrl-pill-btn {
        background: rgba(18, 24, 38, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 9999px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .date-range-pill {
        color: #94a3b8;
    }
    .vs-badge {
        color: #64748b;
        font-size: 0.72rem;
        padding: 0 4px;
    }
    .add-widget-btn {
        background: rgba(24, 32, 52, 0.9);
        border: 1px solid rgba(0, 212, 255, 0.35);
        color: #00d4ff;
    }

    /* Card Elements */
    .card-head-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .card-main-title {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.2px;
    }
    .card-dots-btn {
        color: #64748b;
        font-size: 1.1rem;
        cursor: pointer;
        padding: 0 4px;
        line-height: 1;
    }

    /* 5 Stages Metrics Row */
    .stages-metrics-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 0 12px 8px 12px;
    }
    .stage-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .stage-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .stage-val {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
    }
    .active-stage .stage-label {
        color: #00d4ff !important;
        font-weight: 700;
    }
    .active-stage .stage-val {
        color: #00d4ff !important;
        text-shadow: 0 0 12px rgba(0, 212, 255, 0.6);
    }

    /* AI Exploration Pill Bar */
    .ai-explore-wrap {
        background: linear-gradient(180deg, rgba(16, 22, 36, 0.85) 0%, rgba(10, 14, 24, 0.95) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 14px;
        padding: 10px 14px;
        margin-top: 10px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(0, 212, 255, 0.2);
    }
    .ai-explore-label {
        font-size: 0.76rem;
        font-weight: 600;
        color: #93c5fd;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ai-explore-input-pill {
        background: rgba(8, 12, 20, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 0.82rem;
        color: #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ai-explore-chevron {
        color: #64748b;
        font-weight: bold;
    }

    /* Gross Spend Card */
    .gross-spend-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 2px;
    }
    .gross-spend-metric-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .gross-spend-num {
        font-size: 2.7rem;
        font-weight: 800;
        color: #fbbf24;
        letter-spacing: -1px;
        text-shadow: 0 0 20px rgba(251, 191, 36, 0.25);
        line-height: 1.1;
    }
    .gross-spend-delta {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.35);
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .spend-bar-row {
        margin-bottom: 14px;
    }
    .spend-bar-head {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 6px;
    }
    .spend-bar-title {
        color: #94a3b8;
        font-weight: 500;
    }
    .spend-bar-amount {
        color: #ffffff;
        font-weight: 700;
    }
    .progress-track {
        height: 10px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 9999px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 9999px;
    }
    .fill-green {
        background: repeating-linear-gradient(45deg, #22c55e, #22c55e 6px, #16a34a 6px, #16a34a 12px);
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.4);
    }
    .fill-cyan {
        background: repeating-linear-gradient(45deg, #00d4ff, #00d4ff 6px, #0284c7 6px, #0284c7 12px);
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
    }
    .fill-pink {
        background: repeating-linear-gradient(45deg, #ec4899, #ec4899 6px, #be185d 6px, #be185d 12px);
        box-shadow: 0 0 10px rgba(236, 72, 153, 0.4);
    }

    /* Equalizer Soundwave Subcards */
    .submetric-card {
        background: rgba(14, 20, 32, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 12px 16px;
    }
    .submetric-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .submetric-title {
        font-size: 0.86rem;
        font-weight: 600;
        color: #94a3b8;
    }
    .submetric-body {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }
    .submetric-num {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .equalizer-bars {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 38px;
    }
    .equalizer-bars span {
        width: 3.5px;
        border-radius: 3px;
        display: inline-block;
    }
    .cyan-bars span {
        background: linear-gradient(180deg, #00d4ff 0%, #14b8a6 100%);
        box-shadow: 0 0 6px rgba(0, 212, 255, 0.4);
    }
    .blue-bars span {
        background: linear-gradient(180deg, #38bdf8 0%, #3b82f6 100%);
        box-shadow: 0 0 6px rgba(59, 130, 246, 0.4);
    }
    .submetric-delta-box {
        text-align: right;
    }
    .submetric-delta-lbl {
        font-size: 0.68rem;
        color: #64748b;
    }
    .submetric-delta-val {
        font-size: 0.88rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Supply AI Insights Card */
    .ai-insight-card {
        background: linear-gradient(145deg, rgba(32, 25, 18, 0.88) 0%, rgba(18, 24, 38, 0.85) 100%);
        border: 1px solid rgba(251, 191, 36, 0.35);
        border-radius: 20px;
        padding: 16px 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(251, 191, 36, 0.2);
    }
    .ai-insight-pill {
        background: rgba(251, 191, 36, 0.12);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.74rem;
        font-weight: 700;
        color: #fbbf24;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .ai-insight-big-stat {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -1.5px;
        line-height: 1;
        margin: 12px 0 6px 0;
        text-shadow: 0 0 24px rgba(251, 191, 36, 0.25);
    }
    .ai-insight-text {
        font-size: 0.84rem;
        color: #cbd5e1;
        line-height: 1.4;
        margin-bottom: 14px;
    }
    .ai-carousel-pills {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .carousel-bar {
        height: 3px;
        width: 14px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
    }
    .carousel-bar.active {
        width: 32px;
        background: #ffffff;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
    }

    /* Buttons & Interactive Controls */
    div.stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0284c7 100%) !important;
        color: #0b0f17 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        transition: all 0.25s ease !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5) !important;
        background: linear-gradient(135deg, #38bdf8 0%, #0369a1 100%) !important;
    }
    div.stDownloadButton > button {
        background: rgba(18, 24, 38, 0.8) !important;
        color: #00d4ff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    div.stDownloadButton > button:hover {
        background: rgba(0, 212, 255, 0.12) !important;
        transform: translateY(-2px) !important;
        border-color: #00d4ff !important;
    }

    /* DataFrames / Tables */
    div[data-testid="stDataFrame"] > div {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(14, 20, 32, 0.85) !important;
    }

    /* Standard Metrics */
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricContainer"] {
        background: rgba(18, 24, 38, 0.72) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px !important;
    }

    /* Hide Sidebar */
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Top Brand Header Bar
st.markdown("""
    <div class="zentra-topbar">
        <div class="zentra-brand">
            <div class="zentra-logo-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#zlogo)" />
                    <path d="M2 17L12 22L22 17" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round" />
                    <path d="M2 12L12 17L22 12" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round" />
                    <defs>
                        <linearGradient id="zlogo" x1="2" y1="2" x2="22" y2="12">
                            <stop stop-color="#f59e0b" />
                            <stop offset="1" stop-color="#00d4ff" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <span class="zentra-brand-text">Supply Chain Analytics</span>
        </div>
        <div class="zentra-header-right">
            <div class="zentra-tool-btn" title="Search">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </div>
            <div class="zentra-tool-btn notification-tool" title="Notifications">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                <span class="red-dot"></span>
            </div>
            <div class="zentra-avatar-pill">
                <div class="avatar-circle">SC</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state variables
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = None
if "_last_optimization_findings" not in st.session_state:
    st.session_state._last_optimization_findings = None


def _detect_item_col(df: pd.DataFrame | None) -> str | None:
    """Auto-detect item identifier column."""
    if df is None or df.empty:
        return None
    for candidate in [
        "Item",
        "Item Name",
        "Product",
        "Product Name",
        "SKU",
        "Item ID",
    ]:
        if candidate in df.columns:
            return candidate
    return df.columns[0] if len(df.columns) > 0 else None


def _download_buttons(df: pd.DataFrame | None, base_name: str, key_prefix: str = ""):
    """Render download buttons for CSV and optionally Excel."""
    if df is None or df.empty:
        return

    csv_data = export_to_csv(df)
    cols = st.columns([1, 1, 6])
    with cols[0]:
        if csv_data:
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{base_name}.csv",
                mime="text/csv",
                key=f"{key_prefix}_csv_{base_name}",
            )
    with cols[1]:
        if "xlsx" in get_available_export_formats():
            excel_data = export_to_excel(df)
            if excel_data:
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"{base_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"{key_prefix}_xlsx_{base_name}",
                )


# Exact Zentra navigation list and order matching uploaded reference
PAGES = [
    "Home",
    "Data Management",
    "Inventory Analysis",
    "Demand Analysis",
    "Demand Prediction",
    "Supplier Analysis",
    "Cost Analysis",
    "Optimization",
    "Recommendations",
    "Reporting",
]

page = option_menu(
    menu_title=None,
    options=PAGES,
    icons=[
        "house", "database", "box", "graph-up", "graph-up-arrow", 
        "truck", "currency-dollar", "sliders", "stars", "file-text"
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "4px 10px !important",
            "background-color": "rgba(18, 24, 38, 0.85)",
            "border-radius": "9999px",
            "margin-bottom": "18px",
            "display": "flex",
            "flex-wrap": "wrap",
            "justify-content": "center",
            "box-shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.45)",
            "border": "1px solid rgba(255, 255, 255, 0.08)",
            "backdrop-filter": "blur(12px)",
        },
        "icon": {"color": "#00d4ff", "font-size": "13px"}, 
        "nav-link": {
            "font-size": "12.5px",
            "font-weight": "500",
            "text-align": "center",
            "margin": "2px 3px",
            "color": "#94a3b8",
            "border-radius": "9999px",
            "padding": "6px 12px",
            "--hover-color": "rgba(255, 255, 255, 0.06)",
            "transition": "all 0.2s ease",
        },
        "nav-link-selected": {
            "background": "linear-gradient(180deg, rgba(20, 32, 50, 0.95) 0%, rgba(12, 20, 35, 0.95) 100%)",
            "color": "#ffffff",
            "font-weight": "700",
            "border": "1px solid #00d4ff",
            "box-shadow": "0 0 16px rgba(0, 212, 255, 0.45)",
            "border-radius": "9999px",
        },
    }
)

# -------------------------------------------------------------
# 1. Data Management
# -------------------------------------------------------------
if page == "Data Management":
    st.title("Data Management")
    st.write("Upload supply chain datasets for analysis and optimization.")

    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            df = df.loc[:, ~df.columns.duplicated(keep="first")]
            if st.session_state.dataset_name != uploaded_file.name:
                st.session_state.raw_df = df
                st.session_state.dataset_name = uploaded_file.name
                # Reset stale optimization findings on new dataset upload
                st.session_state._last_optimization_findings = None
                st.success(f"Loaded '{uploaded_file.name}' successfully ({len(df)} rows).")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    if st.session_state.raw_df is not None:
        st.subheader(f"Current Dataset: {st.session_state.dataset_name}")
        st.dataframe(st.session_state.raw_df, use_container_width=True)

        if st.button("Clear uploaded data"):
            st.session_state.raw_df = None
            st.session_state.dataset_name = None
            st.session_state._last_optimization_findings = None
            st.rerun()

    st.caption(
        "Note: Dataset validation, cleansing, and schema checking are owned by "
        "teammates (Sujal/Manthan) and will be integrated here."
    )

# -------------------------------------------------------------
# 2. Home / Dashboard (Zentra Executive Reference View)
# -------------------------------------------------------------
elif page in ["Home", "Dashboard"]:
    import html
    import os
    from modules.dashboard_charts import (
        standardize_dataframe,
        get_latest_stock_snapshot,
        compute_inventory_metrics,
        filter_data,
        calc_k1_inventory_value,
        calc_k2_total_demand,
        calc_k3_items_needing_attention,
        calc_k4_average_lead_time,
        plot_c1_demand_by_category,
        plot_c2_stock_status_mix,
        plot_c3_demand_by_quarter_month,
        plot_c4_top_items_demand,
        plot_c5_inventory_value_by_category,
        plot_c6_quantity_supplied_by_supplier,
        plot_zentra_payments_and_costs,
        plot_zentra_inventory_flow,
        calc_zentra_metrics,
        ChartResult,
    )

    raw_df = st.session_state.raw_df
    if raw_df is None or raw_df.empty:
        st.markdown("""
            <div class="zentra-overview-head">
                <div class="overview-title-wrap">
                    <h1 class="overview-title">Overview</h1>
                </div>
            </div>
            <div style="background: rgba(18, 24, 38, 0.72); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 20px; padding: 60px 24px; text-align: center; margin-top: 15px; box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.65);">
                <div style="font-size: 3rem; margin-bottom: 14px;">📊</div>
                <h2 style="font-size: 1.45rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">No Dataset Uploaded</h2>
                <p style="font-size: 0.92rem; color: #94a3b8; max-width: 520px; margin: 0 auto; line-height: 1.6;">
                    There is currently no information to display. Please upload your supply chain CSV dataset in <b>Data Management</b> to generate the overview analytics, payments & costs, inventory flow, and spend optimization.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        clean_df = standardize_dataframe(raw_df)
        clean_df = clean_df.loc[:, ~clean_df.columns.duplicated(keep="first")]

        if "Current_Stock" not in clean_df.columns:
            clean_df["Current_Stock"] = 100.0

        if "Quantity_Demanded" not in clean_df.columns:
            clean_df["Quantity_Demanded"] = clean_df["Current_Stock"].fillna(10.0)

        if "Date" not in clean_df.columns or clean_df["Date"].isna().all():
            clean_df["Date"] = pd.date_range("2024-01-15", periods=len(clean_df), freq="D" if len(clean_df) > 30 else "30D")

        if "Supplier_ID" not in clean_df.columns:
            if "Category" in clean_df.columns and clean_df["Category"].notna().any():
                clean_df["Supplier_ID"] = "SUP-" + clean_df["Category"].fillna("GEN").astype(str).str[:4].str.upper()
            else:
                clean_df["Supplier_ID"] = [f"SUP-{chr(65 + (i % 4))}" for i in range(len(clean_df))]

        if "Quantity_Supplied" not in clean_df.columns:
            clean_df["Quantity_Supplied"] = clean_df["Current_Stock"].fillna(100.0)

        if "Delivery_Time" not in clean_df.columns:
            default_leads = [3.5, 5.0, 2.0, 4.0, 6.0, 2.5, 7.0]
            clean_df["Delivery_Time"] = [default_leads[i % len(default_leads)] for i in range(len(clean_df))]

        clean_df = clean_df.loc[:, ~clean_df.columns.duplicated(keep="first")]
        z_metrics = calc_zentra_metrics(clean_df)

        # Overview Subheader Row
        st.markdown("""
            <div class="zentra-overview-head">
                <div class="overview-title-wrap">
                    <h1 class="overview-title">Overview</h1>
                </div>
                <div class="overview-ctrls-wrap">
                    <div class="ctrl-pill-btn"><span>◫ Compare</span> <span style="font-size: 9px; margin-left: 2px;">▼</span></div>
                    <div class="ctrl-pill-btn date-range-pill">Jan 01 — July 31 <span class="vs-badge">vs</span> Aug 01 — Dec 31</div>
                    <div class="ctrl-pill-btn add-widget-btn">Add widget +</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------------
        # ROW 1: Supply Chain Payments & Costs (Left) + Gross Spend (Right)
        # -------------------------------------------------------------
        r1_col_left, r1_col_right = st.columns([6.2, 3.8])

        # Left Card: Supply Chain Payments & Costs
        with r1_col_left:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="card-head-row">
                        <div class="card-main-title">Supply Chain Payments & Costs</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                    <div class="stages-metrics-row">
                        <div class="stage-col">
                            <div class="stage-label">Supplier Procure</div>
                            <div class="stage-val">{z_metrics.get('stage_s1', '65.2k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Inventory</div>
                            <div class="stage-val">{z_metrics.get('stage_s2', '54.8k')}</div>
                        </div>
                        <div class="stage-col active-stage">
                            <div class="stage-label">Logistics</div>
                            <div class="stage-val">{z_metrics.get('stage_s3', '48.6k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Warehousing</div>
                            <div class="stage-val">{z_metrics.get('stage_s4', '38.3k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Finished</div>
                            <div class="stage-val">{z_metrics.get('stage_s5', '32.9k')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                pay_chart_res = plot_zentra_payments_and_costs(clean_df)
                if pay_chart_res.available and pay_chart_res.figure is not None:
                    st.plotly_chart(pay_chart_res.figure, use_container_width=True, config={"displayModeBar": False}, key="zentra_pay_chart")

                st.markdown("""
                    <div class="ai-explore-wrap">
                        <div class="ai-explore-label">✨ What would you like to explore next?</div>
                        <div class="ai-explore-input-pill">
                            <span>I want to know what caused the bottleneck in Logistics and how to optimize...</span>
                            <span class="ai-explore-chevron">⌃</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Right Card: Gross Spend & Optimization
        with r1_col_right:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="card-head-row">
                        <div class="card-main-title">Gross Spend & Optimization</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                    <div class="gross-spend-label">Gross Spend</div>
                    <div class="gross-spend-metric-row">
                        <span class="gross-spend-num">{z_metrics.get('gross_spend_str', '$41,540')}</span>
                        <span class="gross-spend-delta">{z_metrics.get('gross_spend_delta', '▲ 15%')}</span>
                    </div>
                    <div class="spend-bar-row">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Procurement</span>
                            <span class="spend-bar-amount">{z_metrics.get('procurement_str', '$26,800')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-green" style="width: {z_metrics.get('procurement_pct', 65)}%;"></div>
                        </div>
                    </div>
                    <div class="spend-bar-row">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Distribution</span>
                            <span class="spend-bar-amount">{z_metrics.get('distribution_str', '$10,400')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-cyan" style="width: {z_metrics.get('distribution_pct', 25)}%;"></div>
                        </div>
                    </div>
                    <div class="spend-bar-row" style="margin-bottom: 24px;">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Operations</span>
                            <span class="spend-bar-amount">{z_metrics.get('operations_str', '$4,340')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-pink" style="width: {z_metrics.get('operations_pct', 10)}%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # -------------------------------------------------------------
        # ROW 2: Inventory Flow (Left) + Equalizers (Center) + AI Insights (Right)
        # -------------------------------------------------------------
        r2_col1, r2_col2, r2_col3 = st.columns([3.2, 3.6, 3.2])

        # Left: Inventory Flow Chart
        with r2_col1:
            with st.container(border=True):
                st.markdown("""
                    <div class="card-head-row">
                        <div class="card-main-title">Inventory Flow</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                """, unsafe_allow_html=True)
                flow_chart_res = plot_zentra_inventory_flow(clean_df)
                if flow_chart_res.available and flow_chart_res.figure is not None:
                    st.plotly_chart(flow_chart_res.figure, use_container_width=True, config={"displayModeBar": False}, key="zentra_flow_chart")

        # Center: Transactions & Suppliers Active
        with r2_col2:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="submetric-card">
                        <div class="submetric-head">
                            <span class="submetric-title">Transactions</span>
                            <span class="card-dots-btn">•••</span>
                        </div>
                        <div class="submetric-body">
                            <div class="submetric-left">
                                <div class="submetric-num">{z_metrics.get('transactions_str', '106k')}</div>
                            </div>
                            <div class="equalizer-bars cyan-bars">
                                <span style="height: 10px;"></span><span style="height: 18px;"></span>
                                <span style="height: 28px;"></span><span style="height: 38px;"></span>
                                <span style="height: 48px;"></span><span style="height: 32px;"></span>
                                <span style="height: 44px;"></span><span style="height: 26px;"></span>
                                <span style="height: 38px;"></span><span style="height: 18px;"></span>
                                <span style="height: 30px;"></span><span style="height: 12px;"></span>
                            </div>
                            <div class="submetric-delta-box">
                                <div class="submetric-delta-lbl">vs last period</div>
                                <div class="submetric-delta-val">{z_metrics.get('transactions_delta', '+34,002')}</div>
                            </div>
                        </div>
                    </div>
                    <div class="submetric-card" style="margin-top: 10px;">
                        <div class="submetric-head">
                            <span class="submetric-title">Suppliers Active</span>
                            <span class="card-dots-btn">•••</span>
                        </div>
                        <div class="submetric-body">
                            <div class="submetric-left">
                                <div class="submetric-num">{z_metrics.get('suppliers_active_str', '1,284')}</div>
                            </div>
                            <div class="equalizer-bars blue-bars">
                                <span style="height: 12px;"></span><span style="height: 22px;"></span>
                                <span style="height: 34px;"></span><span style="height: 46px;"></span>
                                <span style="height: 32px;"></span><span style="height: 40px;"></span>
                                <span style="height: 24px;"></span><span style="height: 16px;"></span>
                                <span style="height: 28px;"></span><span style="height: 14px;"></span>
                            </div>
                            <div class="submetric-delta-box">
                                <div class="submetric-delta-lbl">vs last period</div>
                                <div class="submetric-delta-val">{z_metrics.get('suppliers_active_delta', '+320')}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Right: Supply AI Insights Card
        with r2_col3:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="ai-insight-card">
                        <div>
                            <span class="ai-insight-pill">💡 Supply AI insights</span>
                            <div class="ai-insight-big-stat">{z_metrics.get('accuracy_str', '75%')}</div>
                            <div class="ai-insight-text">
                                Supply accuracy increased by <b>4%</b> compared to last week.
                            </div>
                        </div>
                        <div class="ai-carousel-pills">
                            <span class="carousel-bar active"></span>
                            <span class="carousel-bar"></span>
                            <span class="carousel-bar"></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


        # -------------------------------------------------------------
        # EXPANDABLE MULTI-CHART ANALYTICS & SLICERS
        # Preserves full analytical depth, filters, and all calculations
        # -------------------------------------------------------------
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        with st.expander("📊 Slicers & Comprehensive Multi-Chart Analytical Matrix", expanded=False):
            # Slicer row
            r0_date, r0_cat, r0_item, r0_sup = st.columns(4)
            with r0_date:
                min_d = clean_df["Date"].min().date() if "Date" in clean_df.columns and clean_df["Date"].notna().any() else None
                max_d = clean_df["Date"].max().date() if "Date" in clean_df.columns and clean_df["Date"].notna().any() else None
                if min_d and max_d:
                    date_val = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="slicer_date")
                    sel_start, sel_end = (date_val[0], date_val[1]) if isinstance(date_val, (tuple, list)) and len(date_val) == 2 else (min_d, max_d)
                else:
                    sel_start, sel_end = None, None

            with r0_cat:
                cat_options = ["All"] + sorted([str(c) for c in clean_df.get("Category", pd.Series()).dropna().unique()])
                sel_cat = st.selectbox("Category", options=cat_options, index=0, key="slicer_cat")

            with r0_item:
                id_col = "Item_Name" if "Item_Name" in clean_df.columns else "Item_ID"
                pool = clean_df[clean_df["Category"] == sel_cat] if (sel_cat != "All" and "Category" in clean_df.columns) else clean_df
                item_options = ["All"] + sorted([str(i) for i in pool.get(id_col, pd.Series()).dropna().unique()])
                sel_itm = st.selectbox("Item", options=item_options, index=0, key="slicer_itm")

            with r0_sup:
                sup_options = ["All"] + sorted([s for s in clean_df.get("Supplier_ID", pd.Series()).unique() if s != ""])
                sel_sup = st.selectbox("Supplier", options=sup_options, index=0, key="slicer_sup")

            # Filter data
            global_df, supplier_df = filter_data(
                clean_df,
                start_date=sel_start,
                end_date=sel_end,
                category=sel_cat,
                item=sel_itm,
                supplier=sel_sup,
            )

            if not global_df.empty:
                snapshot_df = get_latest_stock_snapshot(global_df)
                inv_metrics_df = compute_inventory_metrics(snapshot_df)

                k1_val, k1_str = calc_k1_inventory_value(snapshot_df)
                k2_val, k2_str = calc_k2_total_demand(global_df)
                k3_val, k3_str = calc_k3_items_needing_attention(inv_metrics_df)
                k4_val, k4_str = calc_k4_average_lead_time(supplier_df)

                # KPIs Row
                kp1, kp2, kp3, kp4 = st.columns(4)
                kp1.metric("Inventory Value", k1_str)
                kp2.metric("Total Quantity", k2_str)
                kp3.metric("Needs Attention", k3_str)
                kp4.metric("Avg Lead Time", k4_str)

                # Charts Grid
                ch_left, ch_right = st.columns(2)
                with ch_left:
                    c1_res = plot_c1_demand_by_category(global_df)
                    if c1_res.available and c1_res.figure is not None:
                        st.plotly_chart(c1_res.figure, use_container_width=True, key="mat_c1")

                    c3_res = plot_c3_demand_by_quarter_month(global_df)
                    if c3_res.available and c3_res.figure is not None:
                        st.plotly_chart(c3_res.figure, use_container_width=True, key="mat_c3")

                with ch_right:
                    c2_res = plot_c2_stock_status_mix(inv_metrics_df)
                    if c2_res.available and c2_res.figure is not None:
                        st.plotly_chart(c2_res.figure, use_container_width=True, key="mat_c2")

                    c4_res = plot_c4_top_items_demand(global_df)
                    if c4_res.available and c4_res.figure is not None:
                        st.plotly_chart(c4_res.figure, use_container_width=True, key="mat_c4")





# -------------------------------------------------------------
# 3. Inventory Analysis
# -------------------------------------------------------------
elif page == "Inventory Analysis":
    st.title("Inventory Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.inventory import calculate_inventory
        try:
            inv_df = calculate_inventory(df.copy())
            st.dataframe(inv_df, use_container_width=True)
            _download_buttons(inv_df, "inventory_analysis", "inv")
        except Exception as e:
            st.error(f"Could not calculate inventory: {e}")

# -------------------------------------------------------------
# 4. Demand Analysis
# -------------------------------------------------------------
elif page == "Demand Analysis":
    st.title("Demand Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.demand import analyze_demand
        res = analyze_demand(df.copy())
        if res.get("status") == "success":
            metrics = res.get("metrics", {})
            st.subheader("Demand Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Demand", f"{metrics.get('total', 0):,.2f}")
            m2.metric("Average Demand", f"{metrics.get('average', 0):,.2f}")
            m3.metric("Demand Trend", str(metrics.get("demand_trend", "N/A")).title())
            m4.metric("Variability (Std)", f"{metrics.get('variability', 0):,.2f}")
            
            with st.expander("View Raw Data"):
                st.json(res)
        else:
            st.error(res.get("reason", "Unknown error"))

# -------------------------------------------------------------
# 5. Demand Prediction
# -------------------------------------------------------------
elif page == "Demand Prediction":
    st.title("Demand Prediction")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.prediction import run_prediction
        res = run_prediction(df.copy())
        if res.get("status") == "success":
            st.subheader("Prediction Evaluation")
            eval_metrics = res.get("evaluation", {})
            counts = res.get("observation_counts", {})
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MAE (Error)", f"{eval_metrics.get('mae', 0):,.2f}")
            c2.metric("RMSE (Error)", f"{eval_metrics.get('rmse', 0):,.2f}")
            c3.metric("Total Observations", counts.get("total", 0))
            c4.metric("Test Set Size", counts.get("test", 0))
            
            with st.expander("View Full Prediction Output"):
                st.json(res)
        else:
            st.error(res.get("reason", "Unknown error"))

# -------------------------------------------------------------
# 6. Supplier Analysis
# -------------------------------------------------------------
elif page == "Supplier Analysis":
    st.title("Supplier Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.supplier import analyze_supplier
        res = analyze_supplier(df.copy())
        if res.get("status") == "success":
            st.subheader("Supplier Overview")
            metrics = res.get("supplier_metrics", {})
            if metrics:
                for supplier, stats in metrics.items():
                    st.markdown(f"##### Supplier: {supplier}")
                    c1, c2, c3 = st.columns(3)
                    qty_s = stats.get('total_quantity_supplied')
                    avg_del = stats.get('average_delivery_time_days')
                    std_del = stats.get('supply_consistency_std')
                    c1.metric("Total Qty Supplied", f"{qty_s:,.2f}" if qty_s is not None else "N/A")
                    c2.metric("Avg Delivery (Days)", f"{avg_del:,.2f}" if avg_del is not None else "N/A")
                    c3.metric("Consistency (Std)", f"{std_del:,.2f}" if std_del is not None else "N/A")
                    st.markdown("<br>", unsafe_allow_html=True)

            else:
                st.info("No supplier metrics available.")
        else:
            st.error(res.get("reason", "Unknown error"))

# -------------------------------------------------------------
# 7. Cost Analysis
# -------------------------------------------------------------
elif page == "Cost Analysis":
    st.title("Cost Analysis")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df)
        cost_res = analyze_cost(df, item_col=item_col)

        if not cost_res.available:
            st.warning(cost_res.message)
        else:
            st.subheader("Cost Summary")
            metric_cols = st.columns(len(cost_res.totals))
            for i, (k, v) in enumerate(cost_res.totals.items()):
                metric_cols[i].metric(k, f"{v:,.2f}")

            if cost_res.item_level is not None:
                st.subheader("Item-Level Cost Breakdown")
                st.dataframe(cost_res.item_level, use_container_width=True)
                _download_buttons(cost_res.item_level, "item_level_cost", "item")

            if cost_res.category_level is not None:
                st.subheader("Category-Level Cost Breakdown")
                st.dataframe(cost_res.category_level, use_container_width=True)
                _download_buttons(
                    cost_res.category_level, "category_level_cost", "cat"
                )

# -------------------------------------------------------------
# 8. Optimization
# -------------------------------------------------------------
elif page == "Optimization":
    st.title("Supply Chain Optimization Findings")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"
        opt_res = run_optimization(df, item_col=item_col)
        st.session_state._last_optimization_findings = opt_res.findings

        if not opt_res.available:
            st.warning(opt_res.message)
        else:
            st.subheader("Observational Findings")
            if opt_res.findings:
                st.dataframe(opt_res.findings_df, use_container_width=True)
                _download_buttons(
                    opt_res.findings_df, "optimization_findings", "opt"
                )
            else:
                st.info("No optimization issues detected with current data.")

# -------------------------------------------------------------
# 9. Recommendations
# -------------------------------------------------------------
elif page == "Recommendations":
    st.title("Optimization Recommendations")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"
        if st.session_state._last_optimization_findings is None:
            opt_res = run_optimization(df, item_col=item_col)
            st.session_state._last_optimization_findings = opt_res.findings

        rec_res = build_recommendations(st.session_state._last_optimization_findings)

        if not rec_res.available:
            st.info(rec_res.message)
        else:
            st.warning(f"⚠️ **Notice:** {HUMAN_REVIEW_TEXT}")
            st.dataframe(rec_res.recommendations_df, use_container_width=True)
            _download_buttons(
                rec_res.recommendations_df, "recommendations", "rec"
            )

# -------------------------------------------------------------
# 10. Reporting
# -------------------------------------------------------------
elif page == "Reporting":
    st.title("Comprehensive Supply Chain Report")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"



        # 1. Dataset Summary
        st.subheader("1. Dataset Summary")
        c1, c2, c3 = st.columns(3)
        
        def kpi_card(title, value):
            return f"""
            <div style="border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 6px; padding: 12px 16px; background-color: transparent; margin-bottom: 10px;">
                <p style="font-size: 13px; color: #555; margin: 0 0 4px 0;">{title}</p>
                <p style="font-size: 24px; font-weight: bold; color: #111; margin: 0;">{value}</p>
            </div>
            """

        c1.markdown(kpi_card("Total Rows", len(df)), unsafe_allow_html=True)
        c2.markdown(kpi_card("Total Columns", len(df.columns)), unsafe_allow_html=True)
        c3.markdown(kpi_card("Dataset", st.session_state.dataset_name or "In-Memory"), unsafe_allow_html=True)

        # 2. Cost Analysis Summary
        st.subheader("2. Cost Findings")
        cost_res = analyze_cost(df, item_col=item_col)
        if cost_res.available:
            metric_cols = st.columns(len(cost_res.totals))
            for i, (k, v) in enumerate(cost_res.totals.items()):
                metric_cols[i].markdown(kpi_card(k, f"{v:,.2f}"), unsafe_allow_html=True)
            if cost_res.item_level is not None:
                _download_buttons(cost_res.item_level, "report_cost_item_level", "rep_cost")
        else:
            st.write(cost_res.message)

        # 3. Optimization Findings
        st.subheader("3. Optimization Findings")
        opt_res = run_optimization(df, item_col=item_col)
        st.session_state._last_optimization_findings = opt_res.findings
        if opt_res.available and opt_res.findings:
            st.dataframe(opt_res.findings_df, use_container_width=True)
            _download_buttons(opt_res.findings_df, "report_optimization_findings", "rep_opt")
        else:
            st.write(opt_res.message if not opt_res.available else "No issues found.")

        # 4. Recommendation Findings
        st.subheader("4. Actionable Recommendations")
        rec_res = build_recommendations(opt_res.findings)
        if rec_res.available and rec_res.recommendations:
            st.dataframe(rec_res.recommendations_df, use_container_width=True)
            _download_buttons(rec_res.recommendations_df, "report_recommendations", "rep_rec")
        else:
            st.write(rec_res.message)

        # 5. Limitations
        st.subheader("5. Limitations & Assumptions")
        st.markdown(
            """
            - **Human Approval**: All recommendations require human review and authorization before procurement or logistics actions.
            - **Snapshot Data**: Calculations reflect static snapshot data and do not incorporate live order tracking or transit telemetry.
            - **External Integrations**: Demand prediction, supplier metrics, and automated ordering modules are owned by external project tracks and subject to independent validation.
            - **Lead Time**: Safety stock and reorder assessments assume standard lead times unless explicitly specified in future module extensions.
            """
        )
