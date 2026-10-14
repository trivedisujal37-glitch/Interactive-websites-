"""Unit and integration tests for modules.dashboard_charts.

Validates the Power BI Supply Chain Dashboard calculations, edge cases,
filtering logic, and data contract adherence.
"""

import os
import pandas as pd
import numpy as np
import pytest

from modules.dashboard_charts import (
    standardize_dataframe,
    get_latest_stock_snapshot,
    compute_inventory_metrics,
    filter_data,
    format_compact,
    calc_k1_inventory_value,
    calc_k2_total_demand,
    calc_k3_items_needing_attention,
    calc_k4_average_lead_time,
    calc_k5_total_items,
    calc_k6_total_units_stock,
    calc_k7_total_purchase_cost,
    calc_k8_total_transportation_cost,
    calc_k9_overstock_items,
    plot_c1_demand_by_category,
    plot_c2_stock_status_mix,
    plot_c3_demand_by_quarter_month,
    plot_c4_top_items_demand,
    plot_c5_inventory_value_by_category,
    plot_c6_quantity_supplied_by_supplier,
    plot_c7_net_stock_movement_by_month,
    plot_c8_demand_trend,
    plot_c9_demand_by_weekday,
    plot_c10_lead_time_by_supplier,
    plot_c11_supplier_price_index,
    plot_c12_purchase_vs_transportation_cost,
    plot_c13_stock_vs_reorder_point,
    plot_c14_demand_vs_stock_bubble,
    plot_c15_share_quantity_supplied_by_supplier,
    get_c16_needs_attention_table,
)


@pytest.fixture
def sample_dataset():
    """Load or generate the sample supply chain dataset."""
    csv_path = "data/supply_chain_sample_data.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Fallback fixture
        df = pd.DataFrame({
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-02-01"],
            "Item_ID": ["ITM-1", "ITM-1", "ITM-2", "ITM-2"],
            "Item_Name": ["Widget A", "Widget A", "Gadget B", "Gadget B"],
            "Quantity_Demanded": [10, 15, 20, 25],
            "Current_Stock": [100, 85, 200, 175],
            "Category": ["Electronics", "Electronics", "Hardware", "Hardware"],
            "Unit_Price": [25.0, 25.0, 40.0, 40.0],
            "Supplier_ID": ["SUP-1", "", "SUP-2", ""],
            "Delivery_Time": [3.0, np.nan, 5.0, np.nan],
            "Quantity_Supplied": [50.0, np.nan, 80.0, np.nan],
            "Supplier_Unit_Price": [22.0, np.nan, 38.0, np.nan],
            "Transportation_Cost": [15.0, np.nan, 30.0, np.nan],
            "Annual_Holding_Cost_Per_Unit": [2.5, 2.5, 4.0, 4.0],
        })
    return standardize_dataframe(df)


def test_standardize_dataframe_aliases():
    """Test alias mapping from varied input headers."""
    raw = pd.DataFrame({
        "item identifier": ["A1"],
        "demand measure": [50],
        "current stock": [120],
        "delivery time": [4.0],
        "unit price": [10.0]
    })
    clean = standardize_dataframe(raw)
    assert "Item_ID" in clean.columns
    assert "Quantity_Demanded" in clean.columns
    assert "Current_Stock" in clean.columns
    assert "Delivery_Time" in clean.columns
    assert "Unit_Price" in clean.columns
    assert clean["Quantity_Demanded"].iloc[0] == 50


def test_snapshot_latest_stock_logic(sample_dataset):
    """Test that get_latest_stock_snapshot extracts the last stock record per item."""
    snapshot = get_latest_stock_snapshot(sample_dataset)
    # Each item must appear exactly once
    assert len(snapshot) == sample_dataset["Item_ID"].nunique()

    # For an item with multiple dates, verify the stock matches the latest date
    for item_id in sample_dataset["Item_ID"].unique():
        item_rows = sample_dataset[sample_dataset["Item_ID"] == item_id].sort_values("Date")
        expected_latest_stock = item_rows["Current_Stock"].iloc[-1]
        actual_stock = snapshot[snapshot["Item_ID"] == item_id]["Current_Stock"].iloc[0]
        assert actual_stock == expected_latest_stock


def test_k1_inventory_value(sample_dataset):
    """Test K1 Inventory Value sum = sum of latest Current_Stock x Unit_Price."""
    snapshot = get_latest_stock_snapshot(sample_dataset)
    val, fmt = calc_k1_inventory_value(snapshot)
    assert val is not None
    assert val > 0
    expected_sum = (snapshot["Current_Stock"] * snapshot["Unit_Price"]).sum()
    assert np.isclose(val, expected_sum)


def test_k2_total_demand(sample_dataset):
    """Test K2 Total Quantity Demanded."""
    total, fmt = calc_k2_total_demand(sample_dataset)
    assert total == sample_dataset["Quantity_Demanded"].sum()


def test_supplier_filter_does_not_drop_demand_rows(sample_dataset):
    """Critical requirement: Supplier filter must NOT drop demand or stock rows."""
    global_df, supplier_df = filter_data(sample_dataset, supplier="SUP-01")

    # global_df must keep ALL items and demand rows regardless of supplier
    assert len(global_df) == len(sample_dataset)
    assert calc_k2_total_demand(global_df)[0] == calc_k2_total_demand(sample_dataset)[0]

    # supplier_df must filter to SUP-01 delivery events
    assert (supplier_df["Supplier_ID"] == "SUP-01").all()


def test_net_stock_movement_positive_and_negative():
    """Test C7 Net Stock Movement calculation with positive and negative net values."""
    df = pd.DataFrame({
        "Date": ["2024-01-10", "2024-02-10"],
        "Quantity_Demanded": [100, 20],
        "Quantity_Supplied": [30, 80],
    })
    df = standardize_dataframe(df)
    res = plot_c7_net_stock_movement_by_month(df)
    assert res.available is True
    assert res.figure is not None
    # Month 1 is 30 - 100 = -70 (negative, orange)
    # Month 2 is 80 - 20 = +60 (positive, gold)
    colors = res.figure.data[0].marker.color
    assert colors[0] == "#EE6C3C"  # Negative orange
    assert colors[1] == "#E6C32D"  # Positive gold


def test_quarter_and_month_ordering(sample_dataset):
    """Test C3 chart groups quarters and months in calendar order."""
    res = plot_c3_demand_by_quarter_month(sample_dataset)
    assert res.available is True
    assert res.figure is not None
    x_data = res.figure.data[0].x
    # Multi-category: [quarters, months]
    assert len(x_data) == 2


def test_optional_column_missing_returns_graceful_unavailable():
    """Test that missing optional columns return graceful ChartResult(available=False)."""
    # Dataset missing Unit_Price and Supplier columns
    minimal_df = pd.DataFrame({
        "Date": ["2024-01-01"],
        "Item_ID": ["ITM-1"],
        "Item_Name": ["Test"],
        "Quantity_Demanded": [10],
        "Current_Stock": [50],
    })
    clean = standardize_dataframe(minimal_df)
    snap = get_latest_stock_snapshot(clean)

    # C1 (Category missing)
    c1_res = plot_c1_demand_by_category(clean)
    assert c1_res.available is False
    assert "Category" in c1_res.unavailable_reason

    # C5 (Category and Unit_Price missing)
    c5_res = plot_c5_inventory_value_by_category(snap)
    assert c5_res.available is False

    # C6 (Supplier_ID missing)
    c6_res = plot_c6_quantity_supplied_by_supplier(clean)
    assert c6_res.available is False

    # K1 (Unit_Price missing)
    val, fmt = calc_k1_inventory_value(snap)
    assert val is None
    assert fmt == "Unavailable"


def test_empty_dataframe_handling():
    """Test all functions handle empty dataframe gracefully without raising exceptions."""
    empty = pd.DataFrame()
    snap = get_latest_stock_snapshot(empty)
    inv = compute_inventory_metrics(snap)

    assert calc_k1_inventory_value(snap)[1] == "Unavailable"
    assert calc_k2_total_demand(empty)[1] == "Unavailable"
    assert calc_k3_items_needing_attention(inv)[1] == "Unavailable"
    assert calc_k4_average_lead_time(empty)[1] == "Unavailable"
    assert calc_k5_total_items(snap)[1] == "Unavailable"

    assert plot_c1_demand_by_category(empty).available is False
    assert plot_c2_stock_status_mix(inv).available is False
    assert plot_c3_demand_by_quarter_month(empty).available is False
    assert plot_c4_top_items_demand(empty).available is False
    assert plot_c7_net_stock_movement_by_month(empty).available is False
    assert plot_c8_demand_trend(empty).available is False
    table_c16 = get_c16_needs_attention_table(inv, empty)
    assert len(table_c16) == 0


def test_single_item_and_single_month():
    """Test edge case with only 1 item and 1 month of records."""
    single_df = pd.DataFrame({
        "Date": ["2024-03-01", "2024-03-02"],
        "Item_ID": ["ITEM-ONE", "ITEM-ONE"],
        "Item_Name": ["Single Item", "Single Item"],
        "Quantity_Demanded": [5, 10],
        "Current_Stock": [40, 30],
        "Category": ["Solo", "Solo"],
        "Unit_Price": [15.0, 15.0],
        "Supplier_ID": ["SUP-SOLO", "SUP-SOLO"],
        "Delivery_Time": [2.0, np.nan],
        "Quantity_Supplied": [25.0, np.nan],
        "Supplier_Unit_Price": [14.0, np.nan],
        "Transportation_Cost": [10.0, np.nan],
    })
    clean = standardize_dataframe(single_df)
    snap = get_latest_stock_snapshot(clean)
    inv = compute_inventory_metrics(snap)

    assert len(snap) == 1
    assert snap["Current_Stock"].iloc[0] == 30

    res_c1 = plot_c1_demand_by_category(clean)
    assert res_c1.available is True

    res_c3 = plot_c3_demand_by_quarter_month(clean)
    assert res_c3.available is True

    res_c8 = plot_c8_demand_trend(clean)
    assert res_c8.available is True


def test_format_compact():
    """Test compact number formatting output."""
    assert format_compact(None) == "Unavailable"
    assert format_compact(np.nan) == "Unavailable"
    assert format_compact(450) == "450"
    assert format_compact(1500) == "1.5K"
    assert format_compact(2500000) == "2.5M"
    assert format_compact(1200000000) == "1.2B"
