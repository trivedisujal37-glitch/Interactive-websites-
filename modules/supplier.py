import pandas as pd
import numpy as np

COL_SUPPLIER = "supplier_id"
COL_DELIVERY_TIME = "delivery_time_days"
COL_QUANTITY_SUPPLIED = "quantity_supplied"

def analyze_supplier(df: pd.DataFrame) -> dict:
    if df is None or df.empty or COL_SUPPLIER not in df.columns:
        return {"status": "error", "reason": "Supplier analysis unavailable because supplier information was not provided."}

    df = df.dropna(subset=[COL_SUPPLIER]).copy()
    if df.empty:
        return {"status": "error", "reason": "Supplier analysis unavailable because supplier information was not provided."}

    supplier_stats = {}
    grouped = df.groupby(COL_SUPPLIER)

    for supplier_id, group in grouped:
        stats = {}
        
        if COL_QUANTITY_SUPPLIED in df.columns:
            stats["total_quantity_supplied"] = float(group[COL_QUANTITY_SUPPLIED].sum())
        else:
            stats["total_quantity_supplied"] = None
            
        if COL_DELIVERY_TIME in df.columns:
            stats["average_delivery_time_days"] = float(group[COL_DELIVERY_TIME].mean())
            stats["supply_consistency_std"] = float(group[COL_DELIVERY_TIME].std()) if len(group) > 1 else 0.0
        else:
            stats["average_delivery_time_days"] = None
            stats["supply_consistency_std"] = None

        supplier_stats[str(supplier_id)] = stats

    return {
        "status": "success",
        "supplier_metrics": supplier_stats
    }
