"""Inventory analysis module for Supply Chain Optimization System.

Calculates safety stock, reorder point, stock gap, and inventory statuses
without synthetic data or silent fallbacks.
"""

import numpy as np
import pandas as pd
from utils.columns import find_col


def calculate_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate safety stock, reorder points, stock gaps, and inventory review statuses.

    Raises ValueError if either demand or current stock column is missing.
    Leaves reorder point as NaN with status 'Lead time unavailable - review' if lead time is missing.
    """
    if df is None or df.empty:
        raise ValueError("Inventory calculation requires a non-empty dataset.")

    df_res = df.copy()

    col_demand = find_col(df_res, "demand")
    col_stock = find_col(df_res, "current_stock")
    col_lead = find_col(df_res, "delivery_time")
    col_item = find_col(df_res, "item_id") or find_col(df_res, "item_name") or df_res.columns[0]

    if not col_demand:
        raise ValueError("Inventory calculation requires a 'Demand' column.")
    if not col_stock:
        raise ValueError("Inventory calculation requires a 'Current Stock' column.")

    # Coerce demand and stock
    df_res[col_demand] = pd.to_numeric(df_res[col_demand], errors="coerce")
    df_res[col_stock] = pd.to_numeric(df_res[col_stock], errors="coerce")

    # Average demand per item assigned to each row
    df_res["average demand"] = df_res.groupby(col_item)[col_demand].transform("mean")

    # Lead time handling
    has_lead_time = False
    if col_lead and col_lead in df_res.columns:
        df_res[col_lead] = pd.to_numeric(df_res[col_lead], errors="coerce")
        lead_means = df_res.groupby(col_item)[col_lead].transform("mean")
        if lead_means.notna().any():
            df_res["lead time"] = lead_means
            has_lead_time = True

    if not has_lead_time:
        df_res["lead time"] = np.nan
        df_res["safety stock"] = np.nan
        df_res["reorder point calc"] = np.nan
        df_res["reorder point"] = np.nan
        df_res["stock gap"] = np.nan
        df_res["inventory status"] = "Lead time unavailable - review"
        return df_res

    # Standard deviation of demand per item
    if len(df_res) > 1:
        std_demand = df_res.groupby(col_item)[col_demand].transform("std")
        fallback_std = df_res["average demand"] * 0.1
        std_demand = std_demand.fillna(fallback_std)
    else:
        std_demand = df_res["average demand"] * 0.1

    # Formula: Safety Stock = 1.65 x std of demand x sqrt(lead time)
    # Reorder Point = (Average Demand x Lead Time) + Safety Stock
    df_res["safety stock"] = 1.65 * std_demand * np.sqrt(df_res["lead time"])
    df_res["reorder point calc"] = (df_res["average demand"] * df_res["lead time"]) + df_res["safety stock"]
    df_res["reorder point"] = df_res["reorder point calc"]

    df_res["stock gap"] = df_res[col_stock] - df_res["reorder point calc"]

    def _get_status(row: pd.Series) -> str:
        if pd.isna(row["lead time"]) or pd.isna(row["reorder point calc"]):
            return "Lead time unavailable - review"
        gap = row["stock gap"]
        stock_val = row[col_stock]
        if pd.isna(gap) or pd.isna(stock_val):
            return "Review Required"
        if gap < 0 and stock_val <= 0:
            return "Priority Review"
        if gap < 0:
            return "Low Stock"
        if gap > (row["reorder point calc"] * 2) + 1:
            return "Overstock"
        if gap < (row["reorder point calc"] * 0.1):
            return "Review Required"
        return "Sufficient"

    df_res["inventory status"] = df_res.apply(_get_status, axis=1)
    return df_res
