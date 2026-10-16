"""Cost analysis module for Supply Chain Optimization System.

Analyzes expenditure costs (Purchase, Holding, Transportation) and unit prices.
Excludes unit price from total expenditure sums; reports average unit price separately.
"""

from dataclasses import dataclass, field
import pandas as pd
from utils.columns import find_col

SUPPORTED_COST_COLUMNS = [
    "Unit Price",
    "Purchase Cost",
    "Holding Cost",
    "Transportation Cost",
]

UNAVAILABLE_MESSAGE = (
    "Cost analysis unavailable because no supported cost columns were provided."
)


@dataclass
class CostAnalysisResult:
    available: bool
    message: str | None = None
    columns_used: list = field(default_factory=list)
    totals: dict = field(default_factory=dict)
    item_level: pd.DataFrame | None = None
    category_level: pd.DataFrame | None = None


def analyze_cost(
    df: pd.DataFrame | None,
    item_col: str | None = None,
    category_col: str | None = None,
) -> CostAnalysisResult:
    """Analyze cost metrics across supported cost columns.

    Unit Price is excluded from 'Total Combined Cost' and row 'Total Cost',
    and is reported as 'Average Unit Price' (mean) separately.
    """
    if df is None or df.empty:
        return CostAnalysisResult(
            available=False,
            message=UNAVAILABLE_MESSAGE,
        )

    df_numeric = df.copy()

    # Find supported cost columns via canonical column resolver
    col_unit_price = find_col(df_numeric, "unit_price")
    col_purchase = find_col(df_numeric, "purchase_cost")
    col_holding = find_col(df_numeric, "holding_cost")
    col_transport = find_col(df_numeric, "transportation_cost")

    # Optional derivations when explicit totals are absent but source columns exist
    if not col_purchase:
        col_sup_price = find_col(df_numeric, "supplier_unit_price")
        col_qty_sup = find_col(df_numeric, "quantity_supplied")
        if col_sup_price and col_qty_sup and col_sup_price in df_numeric.columns and col_qty_sup in df_numeric.columns:
            sup_p = pd.to_numeric(df_numeric[col_sup_price], errors="coerce").fillna(0.0)
            qty_s = pd.to_numeric(df_numeric[col_qty_sup], errors="coerce").fillna(0.0)
            df_numeric["Purchase Cost (derived)"] = sup_p * qty_s
            col_purchase = "Purchase Cost (derived)"

    if not col_holding:
        col_stock = find_col(df_numeric, "current_stock")
        if "Annual_Holding_Cost_Per_Unit" in df_numeric.columns and col_stock and col_stock in df_numeric.columns:
            ann_h = pd.to_numeric(df_numeric["Annual_Holding_Cost_Per_Unit"], errors="coerce").fillna(0.0)
            stk = pd.to_numeric(df_numeric[col_stock], errors="coerce").fillna(0.0)
            df_numeric["Holding Cost (derived)"] = (ann_h / 365.0) * stk
            col_holding = "Holding Cost (derived)"

    columns_used = []
    for col in [col_unit_price, col_purchase, col_holding, col_transport]:
        if col and col in df_numeric.columns and col not in columns_used:
            columns_used.append(col)

    if not columns_used:
        return CostAnalysisResult(
            available=False,
            message=UNAVAILABLE_MESSAGE,
        )

    for col in columns_used:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce").fillna(0.0)

    # Expenditure columns (excluding Unit Price)
    expenditure_cols = [c for c in columns_used if c != col_unit_price]

    # Calculate individual expenditure column sums (Unit Price is an intensive rate, not summed)
    totals = {col: float(df_numeric[col].sum()) for col in expenditure_cols}
    totals["Total Combined Cost"] = float(sum(totals[col] for col in expenditure_cols))

    if col_unit_price and col_unit_price in df_numeric.columns:
        totals["Average Unit Price"] = float(df_numeric[col_unit_price].mean())

    resolved_item_col = item_col or find_col(df_numeric, "item_id") or find_col(df_numeric, "item_name")
    item_level = None
    if resolved_item_col and resolved_item_col in df_numeric.columns:
        item_cols = [resolved_item_col] + columns_used
        item_level = df_numeric[item_cols].copy()
        if expenditure_cols:
            item_level["Total Cost"] = df_numeric[expenditure_cols].sum(axis=1)
        else:
            item_level["Total Cost"] = 0.0
        item_level = item_level.sort_values(
            by="Total Cost", ascending=False
        ).reset_index(drop=True)

    resolved_category_col = category_col or find_col(df_numeric, "category")
    category_level = None
    if resolved_category_col and resolved_category_col in df_numeric.columns:
        category_summary_cols = expenditure_cols if expenditure_cols else columns_used
        category_level = (
            df_numeric.groupby(resolved_category_col, as_index=False)[category_summary_cols]
            .sum()
        )
        if expenditure_cols:
            category_level["Total Cost"] = category_level[expenditure_cols].sum(axis=1)
        else:
            category_level["Total Cost"] = 0.0
        category_level = category_level.sort_values(
            by="Total Cost", ascending=False
        ).reset_index(drop=True)

    return CostAnalysisResult(
        available=True,
        message=None,
        columns_used=columns_used,
        totals=totals,
        item_level=item_level,
        category_level=category_level,
    )
