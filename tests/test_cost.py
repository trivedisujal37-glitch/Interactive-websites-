"""Tests for modules/cost.py."""

import pandas as pd
import pytest
from modules.cost import (
    SUPPORTED_COST_COLUMNS,
    UNAVAILABLE_MESSAGE,
    CostAnalysisResult,
    analyze_cost,
)


def test_analyze_cost_none_and_empty():
    res_none = analyze_cost(None)
    assert not res_none.available
    assert res_none.message == UNAVAILABLE_MESSAGE

    res_empty = analyze_cost(pd.DataFrame())
    assert not res_empty.available
    assert res_empty.message == UNAVAILABLE_MESSAGE


def test_analyze_cost_no_supported_columns():
    df = pd.DataFrame({"Item": ["A", "B"], "Color": ["Red", "Blue"]})
    res = analyze_cost(df)
    assert not res.available
    assert res.message == UNAVAILABLE_MESSAGE
    assert res.columns_used == []
    assert res.totals == {}
    assert res.item_level is None
    assert res.category_level is None


def test_analyze_cost_all_columns_present():
    data = {
        "Item": ["Widget", "Gadget"],
        "Category": ["Cat1", "Cat2"],
        "Unit Price": [10.0, 20.0],
        "Purchase Cost": [100.0, 200.0],
        "Holding Cost": [5.0, 15.0],
        "Transportation Cost": [2.0, 8.0],
    }
    df = pd.DataFrame(data)
    res = analyze_cost(df, item_col="Item", category_col="Category")

    assert res.available
    assert res.message is None
    assert set(res.columns_used) == set(SUPPORTED_COST_COLUMNS)
    assert "Unit Price" not in res.totals
    assert res.totals["Purchase Cost"] == 300.0
    assert res.totals["Holding Cost"] == 20.0
    assert res.totals["Transportation Cost"] == 10.0
    # Corrected per F1 & Fix 2: exclude Unit Price from totals and Total Combined Cost
    assert res.totals["Total Combined Cost"] == 330.0
    assert res.totals["Average Unit Price"] == 15.0

    # Item level assertions
    assert res.item_level is not None
    assert "Total Cost" in res.item_level.columns
    # Gadget expenditure total cost: 200 + 15 + 8 = 223; Widget: 100 + 5 + 2 = 107
    assert res.item_level.iloc[0]["Item"] == "Gadget"
    assert res.item_level.iloc[0]["Total Cost"] == 223.0
    assert res.item_level.iloc[1]["Item"] == "Widget"
    assert res.item_level.iloc[1]["Total Cost"] == 107.0

    # Category level assertions
    assert res.category_level is not None
    assert "Category" in res.category_level.columns
    assert "Total Cost" in res.category_level.columns


def test_analyze_cost_partial_columns():
    data = {
        "Item": ["Widget", "Gadget"],
        "Purchase Cost": [50.0, 150.0],
        "Holding Cost": [10.0, 20.0],
    }
    df = pd.DataFrame(data)
    res = analyze_cost(df, item_col="Item")

    assert res.available
    assert res.columns_used == ["Purchase Cost", "Holding Cost"]
    assert res.totals["Purchase Cost"] == 200.0
    assert res.totals["Holding Cost"] == 30.0
    assert res.totals["Total Combined Cost"] == 230.0
    assert res.item_level is not None
    assert res.category_level is None


def test_analyze_cost_category_auto_detection():
    data = {
        "Product": ["P1", "P2", "P3"],
        "Item Category": ["Electronics", "Electronics", "Hardware"],
        "Purchase Cost": [100.0, 200.0, 50.0],
    }
    df = pd.DataFrame(data)
    res = analyze_cost(df, item_col="Product")

    assert res.available
    assert res.category_level is not None
    assert "Item Category" in res.category_level.columns
    assert res.category_level.iloc[0]["Item Category"] == "Electronics"
    assert res.category_level.iloc[0]["Purchase Cost"] == 300.0
    assert res.category_level.iloc[0]["Total Cost"] == 300.0
    assert res.category_level.iloc[1]["Item Category"] == "Hardware"
    assert res.category_level.iloc[1]["Purchase Cost"] == 50.0


def test_analyze_cost_sample_dataset_expected_values():
    import os
    path = os.path.join(
        os.path.dirname(__file__), "..", "sample_datasets", "1_electronics_supply_chain.csv"
    )
    if os.path.exists(path):
        df = pd.read_csv(path)
        res = analyze_cost(df)
        assert res.available
        assert "Unit Price" not in res.totals
        assert round(res.totals["Purchase Cost"], 1) == 1782443.0
        assert round(res.totals["Holding Cost"], 1) == 74876.9
        assert round(res.totals["Transportation Cost"], 1) == 46937.6
        assert round(res.totals["Total Combined Cost"], 1) == 1904257.5
        assert round(res.totals["Average Unit Price"], 1) == 80.0

