import pytest
import pandas as pd
from modules.supplier import analyze_supplier

def test_supplier_missing_data():
    df = pd.DataFrame({"demand": [10, 20]})
    res = analyze_supplier(df)
    assert res["status"] == "error"
    assert res["reason"] == "Supplier analysis unavailable because supplier information was not provided."

def test_supplier_metrics():
    df = pd.DataFrame({
        "supplier_id": ["S1", "S1", "S2"],
        "delivery_time_days": [2.0, 4.0, 3.0],
        "quantity_supplied": [100, 150, 200]
    })
    res = analyze_supplier(df)
    assert res["status"] == "success"
    assert "S1" in res["supplier_metrics"]
    assert "S2" in res["supplier_metrics"]
    
    assert res["supplier_metrics"]["S1"]["total_quantity_supplied"] == 250.0
    assert res["supplier_metrics"]["S1"]["average_delivery_time_days"] == 3.0
    assert res["supplier_metrics"]["S1"]["supply_consistency_std"] > 0.0

def test_supplier_metrics_without_delivery_time():
    df = pd.DataFrame({
        "supplier_id": ["S1"],
        "quantity_supplied": [100]
    })
    res = analyze_supplier(df)
    assert res["status"] == "success"
    assert res["supplier_metrics"]["S1"]["total_quantity_supplied"] == 100.0
    assert res["supplier_metrics"]["S1"]["average_delivery_time_days"] is None
