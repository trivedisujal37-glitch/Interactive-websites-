"""Optimization module for Supply Chain Optimization System.

Finds observational optimization issues based on inventory, demand,
prediction, supplier, and cost evidence without making automatic decisions.
"""

from dataclasses import dataclass, field
import pandas as pd


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
    resolved_item_col = item_col
    if resolved_item_col not in inventory_df.columns:
        for candidate in ["Item", "Item Name", "Product", "Product Name", "SKU", "Item ID"]:
            if candidate in inventory_df.columns:
                resolved_item_col = candidate
                break
        else:
            resolved_item_col = inventory_df.columns[0]

    findings: list[dict] = []

    # 1. Reorder Review
    if "Current Stock" in inventory_df.columns and "Reorder Point" in inventory_df.columns:
        for idx, row in inventory_df.iterrows():
            stock = pd.to_numeric(row["Current Stock"], errors="coerce")
            reorder = pd.to_numeric(row["Reorder Point"], errors="coerce")
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
    if "Current Stock" in inventory_df.columns and "Max Stock Level" in inventory_df.columns:
        for idx, row in inventory_df.iterrows():
            stock = pd.to_numeric(row["Current Stock"], errors="coerce")
            max_stock = pd.to_numeric(row["Max Stock Level"], errors="coerce")
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
        and resolved_item_col in demand_df.columns
        and "Demand" in demand_df.columns
        and "Current Stock" in inventory_df.columns
    ):
        try:
            merged_demand = pd.merge(
                inventory_df[[resolved_item_col, "Current Stock"]],
                demand_df[[resolved_item_col, "Demand"]],
                on=resolved_item_col,
                how="inner",
            )
            for idx, row in merged_demand.iterrows():
                stock = pd.to_numeric(row["Current Stock"], errors="coerce")
                demand = pd.to_numeric(row["Demand"], errors="coerce")
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
            pass  # Silently skip any incompatible shape

    # 4. Predicted Demand Coverage Risk
    if (
        prediction_df is not None
        and not prediction_df.empty
        and resolved_item_col in prediction_df.columns
        and "Predicted Demand" in prediction_df.columns
        and "Current Stock" in inventory_df.columns
    ):
        try:
            merged_pred = pd.merge(
                inventory_df[[resolved_item_col, "Current Stock"]],
                prediction_df[[resolved_item_col, "Predicted Demand"]],
                on=resolved_item_col,
                how="inner",
            )
            for idx, row in merged_pred.iterrows():
                stock = pd.to_numeric(row["Current Stock"], errors="coerce")
                pred_demand = pd.to_numeric(row["Predicted Demand"], errors="coerce")
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
            pass  # Silently skip any incompatible shape

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


# Placeholder import hooks for Sujal's and Manthan's modules
def _try_import_demand_df() -> pd.DataFrame | None:
    # TODO: confirm real name
    try:
        from modules.demand import get_demand_dataframe  # type: ignore

        return get_demand_dataframe()
    except (ImportError, AttributeError):
        return None


def _try_import_prediction_df() -> pd.DataFrame | None:
    # TODO: confirm real name
    try:
        from modules.prediction import get_prediction_dataframe  # type: ignore

        return get_prediction_dataframe()
    except (ImportError, AttributeError):
        return None


def _try_import_supplier_df() -> pd.DataFrame | None:
    # TODO: confirm real name
    try:
        from modules.supplier import get_supplier_dataframe  # type: ignore

        return get_supplier_dataframe()
    except (ImportError, AttributeError):
        return None


def run_optimization(
    raw_df: pd.DataFrame | None, item_col: str = "Item"
) -> OptimizationResult:
    """Integration wrapper: queries teammate import hooks and finds optimization issues."""
    demand_df = _try_import_demand_df()
    prediction_df = _try_import_prediction_df()
    supplier_df = _try_import_supplier_df()

    return find_optimization_issues(
        inventory_df=raw_df,
        demand_df=demand_df,
        prediction_df=prediction_df,
        supplier_df=supplier_df,
        cost_df=None,
        item_col=item_col,
    )
