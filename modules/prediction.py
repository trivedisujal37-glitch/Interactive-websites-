"""Demand prediction module for Supply Chain Optimization System.

Pure deterministic forecasting using Simple Moving Average (window=3)
aggregated to daily total demand series without random or synthetic data.
"""

from typing import Any
import numpy as np
import pandas as pd
from utils.columns import find_col

WINDOW = 3


def run_prediction(
    df: pd.DataFrame,
    future_periods: int = 7,
    item: Any | None = None
) -> dict:
    """Forecast demand using Simple Moving Average on daily total demand."""
    if df is None or df.empty:
        return {"status": "Prediction unavailable", "reason": "No data provided."}

    df_copy = df.copy()

    col_demand = find_col(df_copy, "demand")
    col_date = find_col(df_copy, "date")
    col_item = find_col(df_copy, "item_id") or find_col(df_copy, "item_name")

    if not col_demand or not col_date:
        missing = []
        if not col_demand:
            missing.append("demand")
        if not col_date:
            missing.append("date")
        return {
            "status": "Prediction unavailable",
            "reason": f"Prediction unavailable: missing {', '.join(missing)} column."
        }

    # Defensive check: Drop missing dates/demand
    df_clean = df_copy.dropna(subset=[col_date, col_demand]).copy()
    if df_clean.empty:
        return {"status": "Prediction unavailable", "reason": "No valid data after removing missing dates/demand."}

    df_clean[col_date] = pd.to_datetime(df_clean[col_date], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_date]).copy()
    if df_clean.empty:
        return {"status": "Prediction unavailable", "reason": "No valid data after removing missing dates/demand."}

    df_clean[col_demand] = pd.to_numeric(df_clean[col_demand], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_demand]).copy()
    if df_clean.empty:
        return {"status": "Prediction unavailable", "reason": "No valid data after removing missing dates/demand."}

    # Filter to specific item if requested and item column exists
    if item is not None and col_item and col_item in df_clean.columns:
        df_clean = df_clean[df_clean[col_item].astype(str) == str(item)].copy()
        if df_clean.empty:
            return {"status": "Prediction unavailable", "reason": f"No data found for item '{item}'."}

    # Aggregate into one series: total daily demand across items
    daily_demand = (
        df_clean.groupby(col_date, as_index=False)[col_demand]
        .sum()
        .sort_values(col_date)
        .reset_index(drop=True)
    )

    total_obs = len(daily_demand)
    if total_obs < 14:
        return {
            "status": "Prediction unavailable",
            "reason": f"Insufficient observations: {total_obs}. Minimum 14 required."
        }

    time_span = (daily_demand[col_date].iloc[-1] - daily_demand[col_date].iloc[0]).days
    if time_span < 2:
        return {
            "status": "Prediction unavailable",
            "reason": f"Unreasonable time coverage: spans {time_span} days, requires at least 2 days."
        }

    # Chronological split: 80% train, 20% test
    train_size = max(2, int(total_obs * 0.8))
    if train_size < WINDOW or (total_obs - train_size) < 1:
        return {
            "status": "Prediction unavailable",
            "reason": "Not enough training or testing rows after split."
        }

    train_df = daily_demand.iloc[:train_size]
    test_df = daily_demand.iloc[train_size:]

    # Testing phase: predict test set using SMA
    train_values = train_df[col_demand].values
    test_actuals = test_df[col_demand].values

    test_preds = []
    history = list(train_values[-WINDOW:])
    for _ in range(len(test_df)):
        pred = float(sum(history) / WINDOW)
        test_preds.append(pred)
        history.append(pred)
        history.pop(0)

    mae = float(np.mean(np.abs(test_actuals - np.array(test_preds))))
    rmse = float(np.sqrt(np.mean((test_actuals - np.array(test_preds)) ** 2)))

    # Future prediction
    future_preds = []
    history = list(daily_demand[col_demand].values[-WINDOW:])
    for _ in range(future_periods):
        pred = float(sum(history) / WINDOW)
        future_preds.append(pred)
        history.append(pred)
        history.pop(0)

    last_date = daily_demand[col_date].iloc[-1]
    future_dates = [str((last_date + pd.Timedelta(days=i)).date()) for i in range(1, future_periods + 1)]

    return {
        "status": "success",
        "method": f"Simple Moving Average (window={WINDOW})",
        "label": "Forecast of total daily demand across all items",
        "training_period": {
            "start": str(train_df[col_date].iloc[0].date()),
            "end": str(train_df[col_date].iloc[-1].date())
        },
        "testing_period": {
            "start": str(test_df[col_date].iloc[0].date()),
            "end": str(test_df[col_date].iloc[-1].date())
        },
        "prediction_period": {
            "start": future_dates[0],
            "end": future_dates[-1]
        },
        "observation_counts": {
            "total": total_obs,
            "train": len(train_df),
            "test": len(test_df)
        },
        "evaluation": {
            "mae": mae,
            "rmse": rmse
        },
        "actual_values": [float(x) for x in test_actuals],
        "predicted_values": [float(x) for x in test_preds],
        "future_predictions": dict(zip(future_dates, [float(x) for x in future_preds])),
        "limitation": "Recursive moving average flattens over the horizon. Forecast of total daily demand across all items."
    }
