import pytest
import pandas as pd
from datetime import datetime, timedelta
from modules.prediction import run_prediction

def test_prediction_insufficient_history():
    df = pd.DataFrame({
        "date": [str((datetime.today() + timedelta(days=i)).date()) for i in range(10)],
        "demand": [10] * 10
    })
    res = run_prediction(df)
    assert res["status"] == "Prediction unavailable"
    assert "Insufficient observations" in res["reason"]

def test_prediction_sufficient_history():
    df = pd.DataFrame({
        "date": [str((datetime.today() + timedelta(days=i)).date()) for i in range(20)],
        "demand": [10] * 20
    })
    res = run_prediction(df)
    assert res["status"] == "success"
    assert res["method"] == "Simple Moving Average (window=3)"
    assert res["evaluation"]["mae"] == 0.0  # constant demand should have 0 MAE with SMA
    assert res["evaluation"]["rmse"] == 0.0
    assert res["observation_counts"]["total"] == 20
    assert len(res["future_predictions"]) == 7

def test_prediction_invalid_dates():
    df = pd.DataFrame({
        "date": ["invalid"] * 20,
        "demand": [10] * 20
    })
    res = run_prediction(df)
    assert res["status"] == "Prediction unavailable"
    assert "No valid data" in res["reason"] or "Insufficient observations" in res["reason"]

def test_prediction_chronological_split():
    # Pass dates out of order
    dates = [str((datetime.today() + timedelta(days=i)).date()) for i in range(20)]
    dates_shuffled = dates.copy()
    dates_shuffled[0], dates_shuffled[-1] = dates_shuffled[-1], dates_shuffled[0]
    
    df = pd.DataFrame({
        "date": dates_shuffled,
        "demand": [10] * 20
    })
    res = run_prediction(df)
    assert res["status"] == "success"
    # Should correctly sort dates, training start should be the earliest date
    assert res["training_period"]["start"] == dates[0]


def test_prediction_deterministic_and_no_mutation():
    import os
    sample_path = "sample_datasets/1_electronics_supply_chain.csv"
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        orig_cols = list(df.columns)
        r1 = run_prediction(df)
        r2 = run_prediction(df)
        r3 = run_prediction(df)
        assert r1["status"] == "success"
        assert r1["evaluation"]["mae"] == r2["evaluation"]["mae"] == r3["evaluation"]["mae"]
        assert r1["future_predictions"] == r2["future_predictions"] == r3["future_predictions"]
        # Non-mutation of input
        assert list(df.columns) == orig_cols
        # Check limitation and label
        assert "limitation" in r1
        assert "label" in r1


def test_prediction_missing_columns_unavailable():
    df = pd.DataFrame({"Item": ["A", "B"], "Current Stock": [100, 200]})
    res = run_prediction(df)
    assert res["status"] == "Prediction unavailable"
    assert "missing" in res["reason"].lower()
    assert "demand" not in df.columns
    assert "date" not in df.columns
