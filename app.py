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

st.set_page_config(page_title="Supply Chain Optimization System", layout="wide")

st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #f5f6f8;
        background-image: none;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #111827;
        font-size: 2.2rem;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #6b7280;
        font-size: 1.1rem;
        font-weight: 500;
    }
    div[data-testid="stMetricContainer"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    
    /* Buttons */
    div.stButton > button {
        background: #16a34a;
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
        background: #15803d;
        border: none;
    }
    
    /* Download Buttons */
    div.stDownloadButton > button {
        background: #ffffff;
        color: #16a34a !important;
        border-radius: 12px;
        border: 1px solid #16a34a;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stDownloadButton > button:hover {
        background: rgba(22, 163, 74, 0.05);
        transform: translateY(-2px);
    }
    
    /* DataFrames / Tables wrappers */
    div[data-testid="stDataFrame"] > div {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #e5e7eb !important;
        background: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5 {
        color: #111827 !important;
        font-weight: 700 !important;
    }
    
    /* Info/Warning blocks */
    div.stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Hide the default sidebar completely since we moved nav to top */
    [data-testid="collapsedControl"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    </style>
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


# Exact top navigation list and order
PAGES = [
    "Data Management",
    "Dashboard",
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
        "database", "grid", "box", "graph-up", "graph-up-arrow", 
        "truck", "currency-dollar", "sliders", "stars", "file-text"
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffff", "border-radius": "16px", "margin-bottom": "30px", "display": "flex", "flex-wrap": "wrap", "justify-content": "center", "box-shadow": "0 2px 5px rgba(0,0,0,0.05)", "border": "1px solid #e5e7eb"},
        "icon": {"color": "#16a34a", "font-size": "16px"}, 
        "nav-link": {"font-size": "13px", "text-align": "center", "margin":"5px", "color": "#4b5563", "--hover-color": "rgba(22, 163, 74, 0.1)"},
        "nav-link-selected": {"background-color": "#16a34a", "color": "white", "font-weight": "bold"},
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
# 2. Dashboard
# -------------------------------------------------------------
elif page == "Dashboard":
    st.title("Supply Chain Dashboard")

    df = st.session_state.raw_df

    # Total Items
    if df is not None and not df.empty:
        total_items_kpi = str(len(df))
    else:
        total_items_kpi = "Unavailable"

    # Total Stock
    if df is not None and "Current Stock" in df.columns:
        stock_sum = pd.to_numeric(df["Current Stock"], errors="coerce").fillna(0).sum()
        total_stock_kpi = f"{stock_sum:g}"
    else:
        total_stock_kpi = "Unavailable"

    # Total Cost
    cost_res = analyze_cost(df)
    if cost_res.available and "Total Combined Cost" in cost_res.totals:
        total_cost_kpi = f"{cost_res.totals['Total Combined Cost']:,.2f}"
    else:
        total_cost_kpi = "Unavailable"

    # Items Needing Reorder Review
    if df is not None and not df.empty:
        item_col = _detect_item_col(df) or "Item"
        opt_res = run_optimization(df, item_col=item_col)
        if opt_res.available:
            reorder_count = sum(
                1 for f in opt_res.findings if f.get("finding_type") == "Reorder Review"
            )
            reorder_kpi = str(reorder_count)
            st.session_state._last_optimization_findings = opt_res.findings
        else:
            reorder_kpi = "Unavailable"
    else:
        reorder_kpi = "Unavailable"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", total_items_kpi)
    col2.metric("Total Stock", total_stock_kpi)
    col3.metric("Total Cost", total_cost_kpi)
    col4.metric("Items Needing Reorder Review", reorder_kpi)

    if df is None:
        st.info("Upload a dataset in 'Data Management' to view comprehensive analytics.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        
        item_col = _detect_item_col(df) or df.columns[0]
        
        # Add some vertical spacing to drop it down
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Create columns to restrict the width of the chart (Medium size)
        spacer1, chart_col, spacer2 = st.columns([1, 2, 1])
        
        with chart_col:
            st.markdown("#### Top Items by Stock")
            stock_col = next((c for c in df.columns if 'stock' in c.lower() or 'qty' in c.lower() or 'quantity' in c.lower()), None)
            if stock_col:
                top_stock = df.sort_values(by=stock_col, ascending=False).head(10)
                chart_df = top_stock.set_index(item_col)[stock_col]
                # Set a specific height to keep it well-proportioned
                st.bar_chart(chart_df, color="#16a34a", height=350)
            else:
                st.info("No stock data available to chart.")

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
                    c1.metric("Total Qty Supplied", f"{stats.get('total_quantity_supplied') or 0:,.2f}")
                    c2.metric("Avg Delivery (Days)", f"{stats.get('average_delivery_time_days') or 0:,.2f}")
                    c3.metric("Consistency (Std)", f"{stats.get('supply_consistency_std') or 0:,.2f}")
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
