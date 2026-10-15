"""Optimization module for Supply Chain Optimization System.

Finds observational optimization issues based on inventory, demand,
prediction, supplier, and cost evidence without making automatic decisions.
"""

from dataclasses import dataclass, field
import pandas as pd
from utils.columns import find_col


@dataclass
class OptimizationResult:
    available: bool
    message: str | None = None
    findings: list[dict] = field(default_factory=list)
    findings_df: pd.DataFrame | None = None


def find_optimization_issues(
    inventory_df: pd.DataFrame | None = None,
    demand_df: pd.DataFrame | None = None,
    prediction_df: pd.DataFrame | None = None,
    supplier_df: pd.DataFrame | None = None,
    cost_df: pd.DataFrame | None = None,
    item_col: str = "Item",
) -> OptimizationResult:
    """Analyze inventory against thresholds and evidence sources to produce findings."""
    if inventory_df is None or inventory_df.empty:
        return OptimizationResult(
            available=False,
            message="Optimization unavailable: no inventory data provided.",
            findings=[],
            findings_df=pd.DataFrame(
                columns=["item", "finding_type", "trigger_condition", "explanation"]
            ),
        )

    # Determine item column name
    resolved_item_col = (
        (item_col if item_col in inventory_df.columns else None)
        or find_col(inventory_df, "item_id")
        or find_col(inventory_df, "item_name")
        or inventory_df.columns[0]
    )

    col_stock = find_col(inventory_df, "current_stock")
    col_reorder = find_col(inventory_df, "reorder_point")
    col_max_stock = find_col(inventory_df, "max_stock")

    findings: list[dict] = []

    # 1. Reorder Review
    if col_stock and col_reorder:
        for idx, row in inventory_df.iterrows():
            stock = pd.to_numeric(row[col_stock], errors="coerce")
            reorder = pd.to_numeric(row[col_reorder], errors="coerce")
            if pd.isna(stock) or pd.isna(reorder):
                continue
            if stock < reorder:
                diff = float(stock - reorder)
                item_name = str(row[resolved_item_col])
                findings.append(
                    {
                        "item": item_name,
                        "finding_type": "Reorder Review",
                        "trigger_condition": "Current Stock < Reorder Point",
                        "current_stock": float(stock),
                        "reorder_point": float(reorder),
                        "difference": diff,
                        "explanation": (
                            f"Current Stock ({stock:g}) is below the Reorder Point "
                            f"({reorder:g}) by {abs(diff):g} units."
                        ),
                    }
                )

    # 2. Overstock Review
    if col_stock and col_max_stock:
        for idx, row in inventory_df.iterrows():
            stock = pd.to_numeric(row[col_stock], errors="coerce")
            max_stock = pd.to_numeric(row[col_max_stock], errors="coerce")
            if pd.isna(stock) or pd.isna(max_stock):
                continue
            if stock > max_stock:
                diff = float(stock - max_stock)
                item_name = str(row[resolved_item_col])
                findings.append(
                    {
                        "item": item_name,
                        "finding_type": "Overstock Review",
                        "trigger_condition": "Current Stock > Max Stock Level",
                        "current_stock": float(stock),
                        "max_stock_level": float(max_stock),
                        "difference": diff,
                        "explanation": (
                            f"Current Stock ({stock:g}) exceeds the Max Stock Level "
                            f"({max_stock:g}) by {abs(diff):g} units."
                        ),
                    }
                )

    # 3. Demand Coverage Risk
    if (
        demand_df is not None
        and not demand_df.empty
        and col_stock
    ):
        dem_item_col = (
            resolved_item_col if resolved_item_col in demand_df.columns
            else (find_col(demand_df, "item_id") or find_col(demand_df, "item_name"))
        )
        dem_col = "Demand" if "Demand" in demand_df.columns else find_col(demand_df, "demand")
        if dem_item_col and dem_col:
            try:
                merged_demand = pd.merge(
                    inventory_df[[resolved_item_col, col_stock]],
                    demand_df[[dem_item_col, dem_col]],
                    left_on=resolved_item_col,
                    right_on=dem_item_col,
                    how="inner",
                )
                for idx, row in merged_demand.iterrows():
                    stock = pd.to_numeric(row[col_stock], errors="coerce")
                    demand = pd.to_numeric(row[dem_col], errors="coerce")
                    if pd.isna(stock) or pd.isna(demand):
                        continue
                    if demand > stock:
                        diff = float(stock - demand)
                        item_name = str(row[resolved_item_col])
                        findings.append(
                            {
                                "item": item_name,
                                "finding_type": "Demand Coverage Risk",
                                "trigger_condition": "Demand > Current Stock",
                                "current_stock": float(stock),
                                "demand": float(demand),
                                "difference": diff,
                                "explanation": (
                                    f"Current Stock ({stock:g}) is below the Demand "
                                    f"({demand:g}) by {abs(diff):g} units."
                                ),
                            }
                        )
            except Exception:
                pass

    # 4. Predicted Demand Coverage Risk
    if (
        prediction_df is not None
        and not prediction_df.empty
        and col_stock
    ):
        pred_item_col = (
            resolved_item_col if resolved_item_col in prediction_df.columns
            else (find_col(prediction_df, "item_id") or find_col(prediction_df, "item_name"))
        )
        pred_col = "Predicted Demand" if "Predicted Demand" in prediction_df.columns else find_col(prediction_df, "demand")
        if pred_item_col and pred_col:
            try:
                merged_pred = pd.merge(
                    inventory_df[[resolved_item_col, col_stock]],
                    prediction_df[[pred_item_col, pred_col]],
                    left_on=resolved_item_col,
                    right_on=pred_item_col,
                    how="inner",
                )
                for idx, row in merged_pred.iterrows():
                    stock = pd.to_numeric(row[col_stock], errors="coerce")
                    pred_demand = pd.to_numeric(row[pred_col], errors="coerce")
                    if pd.isna(stock) or pd.isna(pred_demand):
                        continue
                    if pred_demand > stock:
                        diff = float(stock - pred_demand)
                        item_name = str(row[resolved_item_col])
                        findings.append(
                            {
                                "item": item_name,
                                "finding_type": "Predicted Demand Coverage Risk",
                                "trigger_condition": "Predicted Demand > Current Stock",
                                "current_stock": float(stock),
                                "predicted_demand": float(pred_demand),
                                "difference": diff,
                                "explanation": (
                                    f"Current Stock ({stock:g}) is below the Predicted Demand "
                                    f"({pred_demand:g}) by {abs(diff):g} units."
                                ),
                            }
                        )
            except Exception:
                pass

    if findings:
        findings_df = pd.DataFrame(findings)
    else:
        findings_df = pd.DataFrame(
            columns=["item", "finding_type", "trigger_condition", "explanation"]
        )

    return OptimizationResult(
        available=True,
        message=None,
        findings=findings,
        findings_df=findings_df,
    )


def run_optimization(
    raw_df: pd.DataFrame | None, item_col: str = "Item"
) -> OptimizationResult:
    """Integration wrapper: extracts per-item demand evidence and finds optimization issues."""
    if raw_df is None or raw_df.empty:
        return find_optimization_issues(None)

    col_item = (
        (item_col if item_col in raw_df.columns else None)
        or find_col(raw_df, "item_id")
        or find_col(raw_df, "item_name")
        or raw_df.columns[0]
    )
    col_demand = find_col(raw_df, "demand")

    demand_df = None
    if col_item and col_demand and col_item in raw_df.columns and col_demand in raw_df.columns:
        df_copy = raw_df[[col_item, col_demand]].copy()
        df_copy[col_demand] = pd.to_numeric(df_copy[col_demand], errors="coerce")
        df_clean = df_copy.dropna(subset=[col_demand])
        if not df_clean.empty:
            demand_df = (
                df_clean.groupby(col_item, as_index=False)[col_demand]
                .mean()
                .rename(columns={col_demand: "Demand"})
            )

    return find_optimization_issues(
        inventory_df=raw_df,
        demand_df=demand_df,
        prediction_df=None,
        supplier_df=None,
        cost_df=None,
        item_col=col_item,
    )

