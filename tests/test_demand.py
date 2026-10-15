import pytest
import pandas as pd
from modules.demand import analyze_demand

def test_demand_normal_data():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "demand": [10, 20, 30],
        "item_id": ["A", "B", "A"]
    })
    res = analyze_demand(df)
    assert res["status"] == "success"
    assert res["metrics"]["total"] == 60
    assert res["metrics"]["demand_trend"] == "increasing"

def test_demand_aggregations():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "demand": [10, 20, 30],
        "item_id": ["A", "B", "A"],
        "category": ["C1", "C2", "C1"],
        "supplier_id": ["S1", "S2", "S1"]
    })
    res = analyze_demand(df, agg_level='item')
    assert "by_item" in res["aggregations"]
    
    res = analyze_demand(df, agg_level='category')
    assert "by_category" in res["aggregations"]

    res = analyze_demand(df, agg_level='supplier')
    assert "by_supplier" in res["aggregations"]

def test_demand_zero_demand():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "demand": [0, 0],
        "item_id": ["A", "A"]
    })
    res = analyze_demand(df)
    assert res["status"] == "success"
    assert res["metrics"]["total"] == 0

def test_demand_invalid_dates():
    df = pd.DataFrame({
        "date": ["invalid", "2023-01-02"],
        "demand": [10, 20],
        "item_id": ["A", "A"]
    })
    res = analyze_demand(df)
    # The invalid row is dropped, leaving 1 valid row
    assert res["status"] == "success"
    assert res["metrics"]["total"] == 20

def test_demand_empty_filtered_data():
    df = pd.DataFrame({
        "date": ["invalid", "invalid"],
        "demand": [10, 20],
        "item_id": ["A", "A"]
    })
    res = analyze_demand(df)
    assert res["status"] == "error"
    assert res["reason"] == "Invalid dates present."

def test_demand_missing_optional_fields():
    df = pd.DataFrame({
        "date": ["2023-01-01"],
        "demand": [10],
        "item_id": ["A"]
    })
    # Passing category/supplier agg_level should not crash even if columns are missing
    res = analyze_demand(df, agg_level='category')
    assert res["status"] == "success"
    assert "by_category" not in res["aggregations"]


def test_demand_real_sum_and_no_mutation():
    import os
    sample_path = "sample_datasets/1_electronics_supply_chain.csv"
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        orig_cols = list(df.columns)
        res = analyze_demand(df)
        assert res["status"] == "success"
        assert res["metrics"]["total"] == 8536.0
        # Assert non-mutation of input
        assert list(df.columns) == orig_cols


def test_demand_missing_columns_returns_unavailable():
    df = pd.DataFrame({"Item": ["A", "B"], "Stock": [10, 20]})
    res = analyze_demand(df)
    assert res["status"] == "error"
    assert "Demand analysis unavailable" in res["reason"]
    # Verify no random column was injected
    assert "demand" not in df.columns
    assert "date" not in df.columns
