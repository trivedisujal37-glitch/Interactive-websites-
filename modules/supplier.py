"""Supplier analysis module for Supply Chain Optimization System.

Calculates supplier delivery lead times, supply consistency, and total quantities supplied
using strict canonical column resolution without fuzzy column guessing.
"""

from typing import Any
import pandas as pd
from utils.columns import find_col


def analyze_supplier(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze supplier metrics across delivery time and quantity supplied."""
    if df is None or df.empty:
        return {"status": "error", "reason": "Supplier analysis unavailable because data is empty."}

    df_copy = df.copy()

    col_sup = find_col(df_copy, "supplier_id")
    if not col_sup:
        return {
            "status": "error",
            "reason": "Supplier analysis unavailable because supplier information was not provided."
        }

    col_del = find_col(df_copy, "delivery_time")
    col_qty = find_col(df_copy, "quantity_supplied")

    df_valid = df_copy.dropna(subset=[col_sup]).copy()
    if df_valid.empty:
        return {
            "status": "error",
            "reason": "Supplier analysis unavailable because supplier information was not provided."
        }

    supplier_stats = {}
    grouped = df_valid.groupby(col_sup)

    for supplier_id, group in grouped:
        stats: dict[str, Any] = {}

        if col_qty and col_qty in group.columns:
            qty_series = pd.to_numeric(group[col_qty], errors="coerce").dropna()
            if not qty_series.empty:
                stats["total_quantity_supplied"] = float(qty_series.sum())
            else:
                stats["total_quantity_supplied"] = None
                stats["quantity_note"] = "No valid quantity supplied values for this supplier."
        else:
            stats["total_quantity_supplied"] = None
            stats["quantity_note"] = "Quantity supplied column not provided in dataset."

        if col_del and col_del in group.columns:
            del_series = pd.to_numeric(group[col_del], errors="coerce").dropna()
            if not del_series.empty:
                stats["average_delivery_time_days"] = float(del_series.mean())
                stats["supply_consistency_std"] = float(del_series.std()) if len(del_series) > 1 else 0.0
            else:
                stats["average_delivery_time_days"] = None
                stats["supply_consistency_std"] = None
        else:
            stats["average_delivery_time_days"] = None
            stats["supply_consistency_std"] = None

        supplier_stats[str(supplier_id)] = stats

    return {
        "status": "success",
        "supplier_metrics": supplier_stats
    }
