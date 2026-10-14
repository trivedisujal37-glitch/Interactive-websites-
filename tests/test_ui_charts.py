"""Unit tests for modules/ui_charts.py (S1-S7 and D1-D7 chart functions)."""

import numpy as np
import pandas as pd
import pytest
from modules.ui_charts import (
    compute_demand_kpis,
    compute_supplier_kpis,
    plot_d1_demand_trend,
    plot_d2_demand_by_month,
    plot_d3_demand_by_weekday,
    plot_d4_top_items_demand,
    plot_d5_demand_by_category,
    plot_d6_weekday_month_heatmap,
    plot_d7_demand_distribution,
    plot_s1_lead_time_by_supplier,
    plot_s2_supplier_price_index,
    plot_s3_quantity_supplied_share,
    plot_s4_transportation_cost_by_supplier,
    plot_s5_delivery_time_distribution,
    plot_s6_monthly_delivery_trend,
    plot_s7_delivery_scatter,
)


@pytest.fixture
def normal_sample_df():
    """Realistic dataset with deliveries on some days and blank delivery fields on other days."""
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    data = {
        "Date": dates,
        "Item_ID": [f"SKU-{i % 3}" for i in range(30)],
        "Item_Name": [f"Item {i % 3}" for i in range(30)],
        "Category": ["Electronics" if i % 2 == 0 else "Hardware" for i in range(30)],
        "Quantity_Demanded": [20 + (i % 10) for i in range(30)],
        "Unit_Price": [50.0 for _ in range(30)],
        # Supplier delivery only every 3 days
        "Supplier_ID": [f"SUP-0{1 + (i % 3)}" if i % 3 == 0 else None for i in range(30)],
        "Delivery_Time": [3.5 + (i % 3) if i % 3 == 0 else None for i in range(30)],
        "Quantity_Supplied": [150 + (i * 10) if i % 3 == 0 else None for i in range(30)],
        "Supplier_Unit_Price": [48.0 if i % 3 == 0 else None for i in range(30)],
        "Transportation_Cost": [120.0 if i % 3 == 0 else None for i in range(30)],
    }
    return pd.DataFrame(data)


def test_supplier_charts_normal_data(normal_sample_df):
    """Test S1-S7 charts generate valid figures and ignore blank-delivery rows."""
    # S1
    r1 = plot_s1_lead_time_by_supplier(normal_sample_df)
    assert r1.available is True
    assert r1.figure is not None
    
    # S2
    r2 = plot_s2_supplier_price_index(normal_sample_df)
    assert r2.available is True
    assert r2.figure is not None
    
    # S3
    r3 = plot_s3_quantity_supplied_share(normal_sample_df)
    assert r3.available is True
    assert r3.figure is not None
    
    # S4
    r4 = plot_s4_transportation_cost_by_supplier(normal_sample_df)
    assert r4.available is True
    assert r4.figure is not None
    
    # S5
    r5 = plot_s5_delivery_time_distribution(normal_sample_df)
    assert r5.available is True
    assert r5.figure is not None
    
    # S6
    r6 = plot_s6_monthly_delivery_trend(normal_sample_df)
    assert r6.available is True
    assert r6.figure is not None
    
    # S7
    r7 = plot_s7_delivery_scatter(normal_sample_df)
    assert r7.available is True
    assert r7.figure is not None
    
    # Supplier KPIs
    kpis = compute_supplier_kpis(normal_sample_df)
    assert "Total Deliveries" in kpis
    assert kpis["Total Deliveries"][0] == "10"  # 10 delivery rows out of 30


def test_demand_charts_normal_data(normal_sample_df):
    """Test D1-D7 charts generate valid figures."""
    # D1
    r1 = plot_d1_demand_trend(normal_sample_df, freq="daily")
    assert r1.available is True
    assert r1.figure is not None
    
    r1_w = plot_d1_demand_trend(normal_sample_df, freq="weekly")
    assert r1_w.available is True
    assert r1_w.figure is not None
    
    # D2
    r2 = plot_d2_demand_by_month(normal_sample_df)
    assert r2.available is True
    assert r2.figure is not None
    
    # D3
    r3 = plot_d3_demand_by_weekday(normal_sample_df)
    assert r3.available is True
    assert r3.figure is not None
    
    # D4
    r4 = plot_d4_top_items_demand(normal_sample_df, top_n=5)
    assert r4.available is True
    assert r4.figure is not None
    
    # D5
    r5 = plot_d5_demand_by_category(normal_sample_df)
    assert r5.available is True
    assert r5.figure is not None
    
    # D6
    r6 = plot_d6_weekday_month_heatmap(normal_sample_df)
    assert r6.available is True
    assert r6.figure is not None
    
    # D7
    r7 = plot_d7_demand_distribution(normal_sample_df)
    assert r7.available is True
    assert r7.figure is not None
    
    # Demand KPIs
    kpis = compute_demand_kpis(normal_sample_df)
    assert "Total Demand" in kpis
    assert "Average Daily Demand" in kpis
    assert kpis["Total Demand"][0] != "-"


def test_charts_empty_dataframe():
    """Verify all chart functions handle empty dataframe without crashing."""
    empty_df = pd.DataFrame()
    
    # Supplier
    assert plot_s1_lead_time_by_supplier(empty_df).available is False
    assert plot_s2_supplier_price_index(empty_df).available is False
    assert plot_s3_quantity_supplied_share(empty_df).available is False
    assert plot_s4_transportation_cost_by_supplier(empty_df).available is False
    assert plot_s5_delivery_time_distribution(empty_df).available is False
    assert plot_s6_monthly_delivery_trend(empty_df).available is False
    assert plot_s7_delivery_scatter(empty_df).available is False
    assert compute_supplier_kpis(empty_df)["Total Deliveries"][0] == "-"
    
    # Demand
    assert plot_d1_demand_trend(empty_df).available is False
    assert plot_d2_demand_by_month(empty_df).available is False
    assert plot_d3_demand_by_weekday(empty_df).available is False
    assert plot_d4_top_items_demand(empty_df).available is False
    assert plot_d5_demand_by_category(empty_df).available is False
    assert plot_d6_weekday_month_heatmap(empty_df).available is False
    assert plot_d7_demand_distribution(empty_df).available is False
    assert compute_demand_kpis(empty_df)["Total Demand"][0] == "-"


def test_charts_missing_columns():
    """Verify graceful handling when optional columns are absent."""
    minimal_df = pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02"],
        "Demand": [10, 20],
    })
    # S1 missing Delivery_Time & Supplier
    res_s1 = plot_s1_lead_time_by_supplier(minimal_df)
    assert res_s1.available is False
    assert "Supplier column not in this dataset" in res_s1.unavailable_reason
    
    # D5 missing Category
    res_d5 = plot_d5_demand_by_category(minimal_df)
    assert res_d5.available is False
    assert "Category column not in this dataset" in res_d5.unavailable_reason


def test_charts_all_nan_columns():
    """Verify all-NaN columns do not crash."""
    nan_df = pd.DataFrame({
        "Date": [np.nan, np.nan],
        "Supplier_ID": [np.nan, np.nan],
        "Delivery_Time": [np.nan, np.nan],
        "Demand": [np.nan, np.nan],
    })
    assert plot_s1_lead_time_by_supplier(nan_df).available is False
    assert plot_d1_demand_trend(nan_df).available is False
