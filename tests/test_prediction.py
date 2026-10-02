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
