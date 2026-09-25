"""Cost analysis module for Supply Chain Optimization System.

Analyzes unit price, purchase, holding, and transportation costs.
"""

from dataclasses import dataclass, field
import pandas as pd

SUPPORTED_COST_COLUMNS = [
    "Unit Price",
    "Purchase Cost",
    "Holding Cost",
    "Transportation Cost",
]

UNAVAILABLE_MESSAGE = (
    "Cost analysis unavailable because no supported cost columns were provided."
)

_CATEGORY_CANDIDATES = [
    "Category",
    "category",
    "Item Category",
    "Product Category",
]


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
    """Analyze cost metrics across supported cost columns."""
    if df is None or df.empty:
        return CostAnalysisResult(
            available=False,
            message=UNAVAILABLE_MESSAGE,
        )

    columns_used = [col for col in SUPPORTED_COST_COLUMNS if col in df.columns]
    if not columns_used:
        return CostAnalysisResult(
            available=False,
            message=UNAVAILABLE_MESSAGE,
        )

    df_numeric = df.copy()
    for col in columns_used:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce").fillna(0.0)

    totals = {col: float(df_numeric[col].sum()) for col in columns_used}
    totals["Total Combined Cost"] = float(sum(totals[col] for col in columns_used))

    item_level = None
    if item_col and item_col in df_numeric.columns:
        item_cols = [item_col] + columns_used
        item_level = df_numeric[item_cols].copy()
        item_level["Total Cost"] = df_numeric[columns_used].sum(axis=1)
        item_level = item_level.sort_values(
            by="Total Cost", ascending=False
        ).reset_index(drop=True)

    target_category_col = category_col
    if not target_category_col:
        for candidate in _CATEGORY_CANDIDATES:
            if candidate in df_numeric.columns:
                target_category_col = candidate
                break

    category_level = None
    if target_category_col and target_category_col in df_numeric.columns:
        category_level = (
            df_numeric.groupby(target_category_col, as_index=False)[columns_used]
            .sum()
        )
        category_level["Total Cost"] = category_level[columns_used].sum(axis=1)
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
