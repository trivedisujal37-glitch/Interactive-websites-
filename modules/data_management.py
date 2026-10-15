"""Data management module for Supply Chain Optimization System.

Handles file loading, structural validation, cleaning, and reporting
while preserving original column headers and legitimate missing values.
"""

from typing import Any
import io
import numpy as np
import pandas as pd
from utils.columns import find_col, ALIAS_TABLE


def load_and_clean_data(file_or_df: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and clean dataset according to strict data integrity rules.

    Accepts a filepath string, file-like buffer (e.g. UploadedFile), or existing DataFrame.
    Preserves original column names. Coerces invalid cells to NaN without fillna(0).
    Returns (cleaned_df, cleaning_report).
    """
    if file_or_df is None:
        return pd.DataFrame(), {"error": "No file or dataframe provided."}

    # 1. Read file or copy DataFrame
    if isinstance(file_or_df, pd.DataFrame):
        df = file_or_df.copy()
    else:
        # Determine format
        is_excel = False
        filename = getattr(file_or_df, "name", None)
        if isinstance(file_or_df, str) and file_or_df.lower().endswith((".xlsx", ".xls")):
            is_excel = True
        elif filename and str(filename).lower().endswith((".xlsx", ".xls")):
            is_excel = True

        try:
            if is_excel:
                df = pd.read_excel(file_or_df)
            else:
                df = pd.read_csv(file_or_df)
        except Exception as e:
            return pd.DataFrame(), {"error": f"Failed to read file: {e}"}

    if df.empty:
        return pd.DataFrame(), {
            "initial": 0,
            "final": 0,
            "fixed": 0,
            "rows_read": 0,
            "rows_removed_empty": 0,
            "rows_removed_duplicates": 0,
            "cells_blanked": {},
            "warnings": ["Dataset is empty."],
            "module_readiness": {},
        }

    # 2. Preserve original column names, trim whitespace, deduplicate identical headers
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]

    # Check for recognizable columns
    has_recognized = False
    for canon_key in ALIAS_TABLE.keys():
        if find_col(df, canon_key) is not None:
            has_recognized = True
            break

    if not has_recognized:
        return pd.DataFrame(), {
            "error": "No recognizable supply chain columns found (e.g., Item, Stock, Demand, Cost)."
        }

    rows_read = len(df)

    # 3. Trim string values
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # 4. Drop completely empty rows
    df_non_empty = df.dropna(how="all")
    empty_rows_dropped = rows_read - len(df_non_empty)
    df = df_non_empty

    # 5. Drop exact duplicate rows
    df_no_dups = df.drop_duplicates()
    duplicate_rows_dropped = len(df) - len(df_no_dups)
    df = df_no_dups.copy()

    cells_blanked: dict[str, int] = {}
    warnings: list[str] = []

    # 6. Clean Date column
    col_date = find_col(df, "date")
    if col_date and col_date in df.columns:
        raw_dates = df[col_date]
        parsed_dates = pd.to_datetime(raw_dates, errors="coerce")
        invalid_dates_count = int((raw_dates.notna() & parsed_dates.isna()).sum())
        if invalid_dates_count > 0:
            cells_blanked[f"{col_date} (invalid dates)"] = invalid_dates_count
        df[col_date] = parsed_dates

    # 7. Clean Numeric columns (non-numeric -> NaN, negative -> NaN, blank stays NaN)
    numeric_keys = [
        "demand", "current_stock", "unit_price", "delivery_time",
        "quantity_supplied", "supplier_unit_price", "transportation_cost",
        "holding_cost", "purchase_cost", "reorder_point", "max_stock"
    ]
    for key in numeric_keys:
        col = find_col(df, key)
        if col and col in df.columns:
            raw_col = df[col]
            coerced = pd.to_numeric(raw_col, errors="coerce")
            non_numeric_count = int((raw_col.notna() & coerced.isna()).sum())
            if non_numeric_count > 0:
                cells_blanked[f"{col} (non-numeric text)"] = non_numeric_count

            neg_mask = coerced < 0
            neg_count = int(neg_mask.sum())
            if neg_count > 0:
                cells_blanked[f"{col} (negative value)"] = neg_count
                coerced[neg_mask] = np.nan

            df[col] = coerced

    # 8. Check for lead time of 0
    col_lead = find_col(df, "delivery_time")
    if col_lead and col_lead in df.columns:
        zero_leads = int((df[col_lead] == 0).sum())
        if zero_leads > 0:
            warnings.append(f"{zero_leads} row(s) report 0 days delivery/lead time (review delivery feasibility).")

    # 9. Normalize category casing per item
    col_cat = find_col(df, "category")
    col_item = find_col(df, "item_id") or find_col(df, "item_name")
    if col_cat and col_cat in df.columns:
        df[col_cat] = df[col_cat].map(
            lambda x: " ".join(str(x).split()).title() if pd.notna(x) and str(x).strip() != "" else np.nan
        )
        if col_item and col_item in df.columns:
            df[col_cat] = df.groupby(col_item)[col_cat].transform(lambda s: s.ffill().bfill())

    # 10. Module readiness assessments
    missing_by_module: dict[str, str] = {}
    c_date = find_col(df, "date")
    c_dem = find_col(df, "demand")
    c_stock = find_col(df, "current_stock")
    c_sup = find_col(df, "supplier_id")
    c_cost = any(
        find_col(df, k) for k in [
            "unit_price", "purchase_cost", "holding_cost",
            "transportation_cost", "supplier_unit_price"
        ]
    )

    pred_miss = [k for k, p in [("date", c_date), ("demand", c_dem)] if not p]
    if pred_miss:
        missing_by_module["Demand Prediction"] = f"Needs date, demand. Missing: {', '.join(pred_miss)}."

    dem_miss = [k for k, p in [("demand", c_dem), ("date", c_date)] if not p]
    if dem_miss:
        missing_by_module["Demand Analysis"] = f"Needs demand, date. Missing: {', '.join(dem_miss)}."

    inv_miss = [k for k, p in [("current stock", c_stock), ("demand", c_dem)] if not p]
    if inv_miss:
        missing_by_module["Inventory Analysis"] = f"Needs current stock, demand. Missing: {', '.join(inv_miss)}."

    if not c_sup:
        missing_by_module["Supplier Analysis"] = "Needs supplier ID. Missing: supplier ID."

    if not c_cost:
        missing_by_module["Cost Analysis"] = "Needs at least one cost column. Missing: all cost columns."

    if not c_stock:
        missing_by_module["Optimization"] = "Needs current stock. Missing: current stock."

    cleaning_report = {
        "initial": rows_read,
        "final": len(df),
        "fixed": empty_rows_dropped + duplicate_rows_dropped,
        "rows_read": rows_read,
        "rows_removed_empty": empty_rows_dropped,
        "rows_removed_duplicates": duplicate_rows_dropped,
        "cells_blanked": cells_blanked,
        "warnings": warnings,
        "module_readiness": missing_by_module,
    }

    return df, cleaning_report
