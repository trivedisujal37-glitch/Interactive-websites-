"""Demand analysis module for Supply Chain Optimization System.

Pure calculation of demand aggregates, trends, and breakdowns using
canonical column resolution without synthetic data fallbacks.
"""

import pandas as pd
from utils.columns import find_col


def analyze_demand(df: pd.DataFrame, agg_level: str = None) -> dict:
    """Analyze demand metrics, trends, and aggregations across items, categories, and dates."""
    if df is None or df.empty:
        return {"status": "error", "reason": "Empty data provided for demand analysis."}

    df_copy = df.copy()

    col_demand = find_col(df_copy, "demand")
    col_date = find_col(df_copy, "date")
    col_item = find_col(df_copy, "item_id") or find_col(df_copy, "item_name")
    col_category = find_col(df_copy, "category")
    col_supplier = find_col(df_copy, "supplier_id")

    if not col_demand or not col_date:
        missing = []
        if not col_demand:
            missing.append("demand")
        if not col_date:
            missing.append("date")
        return {
            "status": "error",
            "reason": f"Demand analysis unavailable: missing {', '.join(missing)} column."
        }

    # Defensive check: Drop missing dates/demand
    df_clean = df_copy.dropna(subset=[col_date, col_demand]).copy()
    if df_clean.empty:
        return {"status": "error", "reason": "No valid data after removing missing dates/demand."}

    df_clean[col_date] = pd.to_datetime(df_clean[col_date], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_date]).copy()
    if df_clean.empty:
        return {"status": "error", "reason": "Invalid dates present."}

    df_clean[col_demand] = pd.to_numeric(df_clean[col_demand], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_demand]).copy()
    if df_clean.empty:
        return {"status": "error", "reason": "No valid data after removing missing dates/demand."}

    total_demand = float(df_clean[col_demand].sum())
    avg_demand = float(df_clean[col_demand].mean())
    min_demand = float(df_clean[col_demand].min())
    max_demand = float(df_clean[col_demand].max())
    var_demand = float(df_clean[col_demand].std()) if len(df_clean) > 1 else 0.0

    metrics = {
        "status": "success",
        "total": total_demand,
        "average": avg_demand,
        "min": min_demand,
        "max": max_demand,
        "variability": var_demand,
        "demand_trend": "stable"
    }

    if len(df_clean) > 1:
        df_sorted = df_clean.sort_values(col_date)
        half = len(df_sorted) // 2
        first_half = df_sorted[col_demand].iloc[:half].mean()
        second_half = df_sorted[col_demand].iloc[half:].mean()
        if second_half > first_half * 1.05:
            metrics["demand_trend"] = "increasing"
        elif second_half < first_half * 0.95:
            metrics["demand_trend"] = "decreasing"

    aggregations = {}

    if agg_level in ["daily", "weekly", "monthly"]:
        freq = "D" if agg_level == "daily" else "W-MON" if agg_level == "weekly" else "ME"
        agg_df = df_clean.set_index(col_date).resample(freq)[col_demand].sum().reset_index()
        agg_df[col_date] = agg_df[col_date].astype(str)
        aggregations["by_date"] = agg_df.to_dict(orient="records")

    if agg_level == "item" and col_item and col_item in df_clean.columns:
        aggregations["by_item"] = df_clean.groupby(col_item)[col_demand].sum().to_dict()

    if agg_level == "category" and col_category and col_category in df_clean.columns:
        aggregations["by_category"] = df_clean.groupby(col_category)[col_demand].sum().to_dict()

    if agg_level == "supplier" and col_supplier and col_supplier in df_clean.columns:
        aggregations["by_supplier"] = df_clean.groupby(col_supplier)[col_demand].sum().to_dict()

    return {
        "status": "success",
        "metrics": metrics,
        "aggregations": aggregations,
        "metadata": {
            "input_field": col_demand,
            "aggregation_method": "sum/mean/std",
            "period": agg_level or "all",
            "missing_data_behavior": "dropped rows with missing demand or date",
            "limitation": "Trend is a basic first-half vs second-half average comparison."
        }
    }
