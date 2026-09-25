"""Supply Chain Optimization System - Streamlit Application.

Anshu's portion: Cost Analysis, Optimization, Recommendations, Reporting, Export & App Integration.
"""

import pandas as pd
import streamlit as st

from modules.cost import analyze_cost
from modules.optimization import run_optimization
from modules.recommendations import HUMAN_REVIEW_TEXT, build_recommendations
from utils.export import (
    export_to_csv,
    export_to_excel,
    get_available_export_formats,
)

st.set_page_config(page_title="Supply Chain Optimization System", layout="wide")

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


# Exact sidebar radio navigation list and order
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

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", PAGES)

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

# -------------------------------------------------------------
# 3-6. Teammate Owned Pages
# -------------------------------------------------------------
elif page in [
    "Inventory Analysis",
    "Demand Analysis",
    "Demand Prediction",
    "Supplier Analysis",
]:
    st.title(page)
    st.info(
        f"**{page}** is not yet available — this page is owned by "
        "Sujal/Manthan and has not been merged into `main` yet."
    )

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
        summary_info = {
            "Dataset Name": st.session_state.dataset_name or "In-Memory",
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Identified Item Column": item_col,
        }
        st.json(summary_info)

        # 2. Cost Analysis Summary
        st.subheader("2. Cost Findings")
        cost_res = analyze_cost(df, item_col=item_col)
        if cost_res.available:
            st.write(f"**Cost Columns Analyzed:** {', '.join(cost_res.columns_used)}")
            st.json(cost_res.totals)
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
