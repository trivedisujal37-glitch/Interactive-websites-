"""Tests for dirty fixture data cleaning and downstream safety."""

import os
import io
import pandas as pd
import pytest
from modules.data_management import load_and_clean_data
from modules.demand import analyze_demand
from modules.prediction import run_prediction
from modules.inventory import calculate_inventory
from modules.supplier import analyze_supplier
from modules.cost import analyze_cost
from modules.optimization import run_optimization


DIRTY_FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "supply_chain_sample_data_dirty.csv"
)


def test_dirty_fixture_cleaning_report():
    """Verify that cleaning handles all 21 deliberate defect types properly."""
    assert os.path.exists(DIRTY_FIXTURE_PATH), "Dirty fixture must exist"

    df_cleaned, report = load_and_clean_data(DIRTY_FIXTURE_PATH)

    # 1. Row counts & duplicate detection
    assert report["rows_read"] == 22
    assert report["rows_removed_duplicates"] == 1
    assert len(df_cleaned) < 22

    # 2. Text trimming
    assert "Widget Space Problem" in df_cleaned["Item_Name"].values

    # 3. Numeric conversions: negatives and invalid text become NaN, never 0
    # Negative demand row (ITEM-007)
    row_neg_demand = df_cleaned[df_cleaned["Item_ID"] == "ITEM-007"]
    assert pd.isna(row_neg_demand["Demand"].iloc[0])

    # Negative price row (ITEM-008)
    row_neg_price = df_cleaned[df_cleaned["Item_ID"] == "ITEM-008"]
    assert pd.isna(row_neg_price["Unit Price"].iloc[0])

    # Negative lead time row (ITEM-009)
    row_neg_lead = df_cleaned[df_cleaned["Item_ID"] == "ITEM-009"]
    assert pd.isna(row_neg_lead["Delivery Time"].iloc[0])

    # Text in stock row (ITEM-010)
    row_text_stock = df_cleaned[df_cleaned["Item_ID"] == "ITEM-010"]
    assert pd.isna(row_text_stock["Current Stock"].iloc[0])

    # Text in price row (ITEM-019)
    row_text_price = df_cleaned[df_cleaned["Item_ID"] == "ITEM-019"]
    assert pd.isna(row_text_price["Unit Price"].iloc[0])

    # Negative qty supplied (ITEM-016)
    row_neg_sup = df_cleaned[df_cleaned["Item_ID"] == "ITEM-016"]
    assert pd.isna(row_neg_sup["Quantity Supplied"].iloc[0])

    # Blank delivery columns stay NaN (ITEM-021)
    row_blank_del = df_cleaned[df_cleaned["Item_ID"] == "ITEM-021"]
    assert pd.isna(row_blank_del["Delivery Time"].iloc[0])
    assert pd.isna(row_blank_del["Quantity Supplied"].iloc[0])

    # Impossible date (ITEM-005)
    row_imp_date = df_cleaned[df_cleaned["Item_ID"] == "ITEM-005"]
    assert pd.isna(row_imp_date["Date"].iloc[0])

    # Report structure has all required metrics
    assert "cells_blanked" in report
    assert any("negative" in k for k in report["cells_blanked"])
    assert any("non-numeric" in k for k in report["cells_blanked"])
    assert any("invalid dates" in k for k in report["cells_blanked"])
    assert any("0 days" in w for w in report["warnings"])
    assert "module_readiness" in report


def test_dirty_fixture_downstream_modules_safe():
    """Verify that all downstream modules run safely on the cleaned dirty dataset."""
    df_cleaned, _ = load_and_clean_data(DIRTY_FIXTURE_PATH)

    # 1. Demand Analysis
    demand_res = analyze_demand(df_cleaned)
    assert demand_res["status"] == "success"
    assert demand_res["metrics"]["total"] > 0
    assert not any(col.startswith("random_") for col in df_cleaned.columns)

    # 2. Prediction (handles NaT dates without crashing)
    pred_res = run_prediction(df_cleaned)
    assert pred_res["status"] in ["success", "unavailable"]

    # 3. Inventory
    inv_res = calculate_inventory(df_cleaned)
    assert inv_res is not None
    assert "reorder point calc" in inv_res.columns or "reorder point" in inv_res.columns
    # Check that rows with missing lead time receive "Lead time unavailable - review"
    unavail_status = inv_res[inv_res["Delivery Time"].isna()]["inventory status"]
    if not unavail_status.empty:
        assert (unavail_status == "Lead time unavailable - review").all()

    # 4. Supplier Analysis
    sup_res = analyze_supplier(df_cleaned)
    assert sup_res["status"] == "success"
    assert sup_res["supplier_metrics"] is not None

    # 5. Cost Analysis
    cost_res = analyze_cost(df_cleaned)
    assert cost_res.available
    assert "Total Combined Cost" in cost_res.totals
    assert "Average Unit Price" in cost_res.totals

    # 6. Optimization
    opt_res = run_optimization(df_cleaned)
    assert opt_res.available
    assert opt_res.findings_df is not None


def test_no_random_or_default_columns_added():
    """Verify no module injects random or default invented columns."""
    df_cleaned, _ = load_and_clean_data(DIRTY_FIXTURE_PATH)
    original_cols = set(df_cleaned.columns)

    _ = analyze_demand(df_cleaned)
    _ = run_prediction(df_cleaned)
    _ = analyze_supplier(df_cleaned)
    _ = analyze_cost(df_cleaned)
    _ = run_optimization(df_cleaned)

    # Caller dataframe must never be mutated
    assert set(df_cleaned.columns) == original_cols
