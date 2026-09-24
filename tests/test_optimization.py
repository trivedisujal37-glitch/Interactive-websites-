"""Tests for modules/optimization.py."""

import pandas as pd
import pytest
from modules.optimization import find_optimization_issues, run_optimization


def test_missing_inventory_unavailable():
    res_none = find_optimization_issues(None)
    assert not res_none.available
    assert "Optimization unavailable" in res_none.message

    res_empty = find_optimization_issues(pd.DataFrame())
    assert not res_empty.available
    assert "Optimization unavailable" in res_empty.message


def test_worked_example_reorder_review():
    # WORKED EXAMPLE TO MATCH EXACTLY: Current Stock=320, Reorder Point=700 -> difference must equal -380
    df = pd.DataFrame(
        {
            "Item": ["Widget A"],
            "Current Stock": [320],
            "Reorder Point": [700],
        }
    )
    res = find_optimization_issues(inventory_df=df)
    assert res.available
    assert len(res.findings) == 1
    finding = res.findings[0]
    assert finding["item"] == "Widget A"
    assert finding["finding_type"] == "Reorder Review"
    assert finding["trigger_condition"] == "Current Stock < Reorder Point"
    assert finding["current_stock"] == 320.0
    assert finding["reorder_point"] == 700.0
    assert finding["difference"] == -380.0
    assert (
        finding["explanation"]
        == "Current Stock (320) is below the Reorder Point (700) by 380 units."
    )


def test_healthy_stock_no_findings():
    df = pd.DataFrame(
        {
            "Item": ["Healthy Widget"],
            "Current Stock": [500],
            "Reorder Point": [300],
            "Max Stock Level": [800],
        }
    )
    res = find_optimization_issues(inventory_df=df)
    assert res.available
    assert len(res.findings) == 0
    assert res.findings_df is not None
    assert res.findings_df.empty


def test_overstock_finding():
    df = pd.DataFrame(
        {
            "Item": ["Overstocked Item"],
            "Current Stock": [1200],
            "Reorder Point": [200],
            "Max Stock Level": [800],
        }
    )
    res = find_optimization_issues(inventory_df=df)
    assert res.available
    assert len(res.findings) == 1
    f = res.findings[0]
    assert f["item"] == "Overstocked Item"
    assert f["finding_type"] == "Overstock Review"
    assert f["trigger_condition"] == "Current Stock > Max Stock Level"
    assert f["difference"] == 400.0
    assert (
        f["explanation"]
        == "Current Stock (1200) exceeds the Max Stock Level (800) by 400 units."
    )


def test_demand_coverage_risk():
    inv_df = pd.DataFrame(
        {
            "Item": ["Part X"],
            "Current Stock": [100],
            "Reorder Point": [50],
        }
    )
    demand_df = pd.DataFrame(
        {
            "Item": ["Part X"],
            "Demand": [150],
        }
    )
    res = find_optimization_issues(inventory_df=inv_df, demand_df=demand_df)
    assert res.available
    # Since stock (100) >= reorder (50), no reorder finding, but demand (150) > stock (100) -> demand coverage finding
    assert len(res.findings) == 1
    f = res.findings[0]
    assert f["finding_type"] == "Demand Coverage Risk"
    assert f["difference"] == -50.0
    assert "Demand (150)" in f["explanation"]


def test_predicted_demand_coverage_risk():
    inv_df = pd.DataFrame(
        {
            "Item": ["Part Y"],
            "Current Stock": [120],
            "Reorder Point": [50],
        }
    )
    pred_df = pd.DataFrame(
        {
            "Item": ["Part Y"],
            "Predicted Demand": [200],
        }
    )
    res = find_optimization_issues(inventory_df=inv_df, prediction_df=pred_df)
    assert res.available
    assert len(res.findings) == 1
    f = res.findings[0]
    assert f["finding_type"] == "Predicted Demand Coverage Risk"
    assert f["difference"] == -80.0
    assert "Predicted Demand (200)" in f["explanation"]


def test_missing_demand_prediction_supplier_does_not_crash():
    df = pd.DataFrame(
        {
            "Item": ["Item Z"],
            "Current Stock": [100],
            "Reorder Point": [150],
        }
    )
    # run_optimization calls import hooks which return None without crashing
    res = run_optimization(df, item_col="Item")
    assert res.available
    assert len(res.findings) == 1
    assert res.findings[0]["finding_type"] == "Reorder Review"
