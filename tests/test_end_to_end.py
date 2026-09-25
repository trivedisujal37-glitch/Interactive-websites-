"""End-to-end integration tests for Supply Chain Optimization System."""

import pandas as pd
import pytest
from modules.cost import UNAVAILABLE_MESSAGE, analyze_cost
from modules.optimization import find_optimization_issues, run_optimization
from modules.recommendations import HUMAN_REVIEW_TEXT, build_recommendations
from utils.export import export_to_csv


def test_full_pipeline_synthetic_df():
    # 1. Simulate uploaded synthetic DataFrame
    synthetic_df = pd.DataFrame(
        {
            "Item": ["Widget A", "Gadget B"],
            "Category": ["Electronics", "Electronics"],
            "Current Stock": [320, 1200],
            "Reorder Point": [700, 300],
            "Max Stock Level": [1000, 800],
            "Unit Price": [25.0, 45.0],
            "Purchase Cost": [8000.0, 54000.0],
            "Holding Cost": [320.0, 1200.0],
            "Transportation Cost": [450.0, 750.0],
        }
    )

    # 2. Cost Analysis
    cost_res = analyze_cost(synthetic_df, item_col="Item")
    assert cost_res.available
    assert cost_res.item_level is not None
    assert cost_res.totals["Total Combined Cost"] > 0

    # 3. Optimization (with missing prediction/supplier modules handled gracefully)
    opt_res = run_optimization(synthetic_df, item_col="Item")
    assert opt_res.available
    assert len(opt_res.findings) >= 2  # Widget A reorder, Gadget B overstock

    # 4. Recommendations
    rec_res = build_recommendations(opt_res.findings)
    assert rec_res.available
    assert rec_res.recommendations_df is not None
    assert len(rec_res.recommendations) >= 2

    # 5. Export
    csv_bytes = export_to_csv(rec_res.recommendations_df)
    assert csv_bytes is not None
    decoded_csv = csv_bytes.decode("utf-8")

    # Assert CSV contains both an item name and "Human approval required"
    assert "Widget A" in decoded_csv
    assert HUMAN_REVIEW_TEXT in decoded_csv


def test_missing_cost_columns_unavailable():
    # Only inventory columns provided, no cost columns
    df = pd.DataFrame(
        {
            "Item": ["Item 1", "Item 2"],
            "Current Stock": [100, 200],
            "Reorder Point": [150, 50],
        }
    )
    cost_res = analyze_cost(df, item_col="Item")
    assert not cost_res.available
    assert cost_res.message == UNAVAILABLE_MESSAGE


def test_empty_filtered_optimization_recommendations_unavailable():
    # Healthy inventory with no reorder or overstock issues
    df = pd.DataFrame(
        {
            "Item": ["Balanced Item"],
            "Current Stock": [500],
            "Reorder Point": [200],
            "Max Stock Level": [800],
            "Unit Price": [10.0],
        }
    )
    opt_res = run_optimization(df, item_col="Item")
    assert opt_res.available
    assert len(opt_res.findings) == 0

    # Recommendations must be unavailable when there are no findings (no fake rows)
    rec_res = build_recommendations(opt_res.findings)
    assert not rec_res.available
    assert (
        rec_res.message
        == "No recommendations: no optimization findings were generated."
    )
    assert len(rec_res.recommendations) == 0
    assert rec_res.recommendations_df is not None
    assert rec_res.recommendations_df.empty
