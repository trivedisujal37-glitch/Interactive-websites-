import pandas as pd
import numpy as np

# Column constants
COL_DATE = "date"
COL_DEMAND = "demand"
COL_ITEM = "item_id"
COL_CATEGORY = "category"
COL_SUPPLIER = "supplier_id"

def analyze_demand(df: pd.DataFrame, agg_level: str = None) -> dict:
    if df is None or df.empty:
        return {"status": "error", "reason": "Empty data provided for demand analysis."}
    
    if COL_DEMAND not in df.columns or COL_DATE not in df.columns or COL_ITEM not in df.columns:
        return {"status": "error", "reason": "Missing required columns: date, demand, and item_id."}

    # Defensive check: Drop invalid dates/demand
    df = df.dropna(subset=[COL_DATE, COL_DEMAND]).copy()
    if df.empty:
        return {"status": "error", "reason": "No valid data after removing missing dates/demand."}

    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors='coerce')
    df = df.dropna(subset=[COL_DATE]).copy()
    if df.empty:
        return {"status": "error", "reason": "Invalid dates present."}

    metrics = {
        "status": "success",
        "total": float(df[COL_DEMAND].sum()),
        "average": float(df[COL_DEMAND].mean()),
        "min": float(df[COL_DEMAND].min()),
        "max": float(df[COL_DEMAND].max()),
        "variability": float(df[COL_DEMAND].std()) if len(df) > 1 else 0.0,
        "demand_trend": "stable"
    }
    
    if len(df) > 1:
        # Simple trend: compare first half average to second half
        df_sorted = df.sort_values(COL_DATE)
        half = len(df_sorted) // 2
        first_half = df_sorted[COL_DEMAND].iloc[:half].mean()
        second_half = df_sorted[COL_DEMAND].iloc[half:].mean()
        if second_half > first_half * 1.05:
            metrics["demand_trend"] = "increasing"
        elif second_half < first_half * 0.95:
            metrics["demand_trend"] = "decreasing"

    # Aggregations
    aggregations = {}
    
    if agg_level in ['daily', 'weekly', 'monthly']:
        freq = 'D' if agg_level == 'daily' else 'W-MON' if agg_level == 'weekly' else 'ME'
        agg_df = df.set_index(COL_DATE).resample(freq)[COL_DEMAND].sum().reset_index()
        agg_df[COL_DATE] = agg_df[COL_DATE].astype(str)
        aggregations["by_date"] = agg_df.to_dict(orient='records')
        
    if agg_level == 'item':
        aggregations["by_item"] = df.groupby(COL_ITEM)[COL_DEMAND].sum().to_dict()
        
    if agg_level == 'category' and COL_CATEGORY in df.columns:
        aggregations["by_category"] = df.groupby(COL_CATEGORY)[COL_DEMAND].sum().to_dict()
        
    if agg_level == 'supplier' and COL_SUPPLIER in df.columns:
        aggregations["by_supplier"] = df.groupby(COL_SUPPLIER)[COL_DEMAND].sum().to_dict()

    return {
        "status": "success",
        "metrics": metrics,
        "aggregations": aggregations,
        "metadata": {
            "input_field": COL_DEMAND,
            "aggregation_method": "sum/mean/std",
            "period": agg_level or "all",
            "missing_data_behavior": "dropped rows with missing demand or date",
            "limitation": "Trend is a basic first-half vs second-half average comparison."
        }
    }
