import pandas as pd
import numpy as np

COL_DATE = "date"
COL_DEMAND = "demand"

def run_prediction(df: pd.DataFrame, future_periods: int = 7) -> dict:
    if df is None or df.empty:
        return {"status": "Prediction unavailable", "reason": "No data provided."}
    
    if COL_DEMAND not in df.columns or COL_DATE not in df.columns:
        return {"status": "Prediction unavailable", "reason": f"Missing required columns: {COL_DATE}, {COL_DEMAND}."}

    df = df.dropna(subset=[COL_DATE, COL_DEMAND]).copy()
    if df.empty:
        return {"status": "Prediction unavailable", "reason": "No valid data after removing missing dates/demand."}

    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors='coerce')
    df = df.dropna(subset=[COL_DATE]).copy()
    
    # Needs chronological sort for strict train/test split without leakage
    df = df.sort_values(COL_DATE).reset_index(drop=True)
    
    total_obs = len(df)
    if total_obs < 14:
        return {"status": "Prediction unavailable", "reason": f"Insufficient observations: {total_obs}. Minimum 14 required."}

    time_span = (df[COL_DATE].iloc[-1] - df[COL_DATE].iloc[0]).days
    if time_span < 13:
        return {"status": "Prediction unavailable", "reason": f"Unreasonable time coverage: spans {time_span} days, requires at least 14 days."}

    # Chronological split: 80% train, 20% test
    train_size = int(total_obs * 0.8)
    if train_size < 10 or (total_obs - train_size) < 4:
        return {"status": "Prediction unavailable", "reason": "Not enough training or testing rows after split."}

    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]

    # Method: Simple Moving Average (3 periods)
    window = 3
    if len(train_df) < window:
        return {"status": "Prediction unavailable", "reason": "Insufficient training rows for moving average window."}

    # Testing phase: predict test set using SMA
    train_values = train_df[COL_DEMAND].values
    test_actuals = test_df[COL_DEMAND].values
    
    test_preds = []
    history = list(train_values[-window:])
    for _ in range(len(test_df)):
        pred = sum(history) / window
        test_preds.append(pred)
        history.append(pred)
        history.pop(0)

    mae = float(np.mean(np.abs(test_actuals - np.array(test_preds))))
    rmse = float(np.sqrt(np.mean((test_actuals - np.array(test_preds)) ** 2)))

    # Future prediction
    future_preds = []
    history = list(df[COL_DEMAND].values[-window:])
    for _ in range(future_periods):
        pred = sum(history) / window
        future_preds.append(pred)
        history.append(pred)
        history.pop(0)
        
    last_date = df[COL_DATE].iloc[-1]
    future_dates = [str((last_date + pd.Timedelta(days=i)).date()) for i in range(1, future_periods + 1)]

    return {
        "status": "success",
        "method": "Simple Moving Average (window=3)",
        "training_period": {"start": str(train_df[COL_DATE].iloc[0].date()), "end": str(train_df[COL_DATE].iloc[-1].date())},
        "testing_period": {"start": str(test_df[COL_DATE].iloc[0].date()), "end": str(test_df[COL_DATE].iloc[-1].date())},
        "prediction_period": {"start": future_dates[0], "end": future_dates[-1]},
        "observation_counts": {"total": total_obs, "train": len(train_df), "test": len(test_df)},
        "evaluation": {"mae": mae, "rmse": rmse},
        "actual_values": [float(x) for x in test_actuals],
        "predicted_values": [float(x) for x in test_preds],
        "future_predictions": dict(zip(future_dates, [float(x) for x in future_preds]))
    }
