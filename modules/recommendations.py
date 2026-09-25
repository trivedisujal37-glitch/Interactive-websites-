"""Recommendations module for Supply Chain Optimization System.

Transforms optimization findings into human-review-only recommendation records.
Never prescribes automated actions or direct commands.
"""

from dataclasses import dataclass, field
import pandas as pd

HUMAN_REVIEW_TEXT = "Human approval required. This is not an automated action."

REQUIRED_FIELDS = [
    "item",
    "recommendation_type",
    "trigger_condition",
    "actual_values",
    "comparison",
    "reason",
    "suggested_action",
    "limitation",
    "human_review",
]


@dataclass
class RecommendationResult:
    available: bool
    message: str | None = None
    recommendations: list[dict] = field(default_factory=list)
    recommendations_df: pd.DataFrame | None = None


def build_recommendations(
    findings: list[dict] | None,
) -> RecommendationResult:
    """Build structured human-review recommendations from optimization findings."""
    if not findings:
        return RecommendationResult(
            available=False,
            message="No recommendations: no optimization findings were generated.",
            recommendations=[],
            recommendations_df=pd.DataFrame(columns=REQUIRED_FIELDS),
        )

    recommendations: list[dict] = []

    for finding in findings:
        finding_type = finding.get("finding_type", "")
        item = str(finding.get("item", "Unknown"))
        trigger = finding.get("trigger_condition", "")
        stock = finding.get("current_stock", 0.0)

        if finding_type == "Reorder Review":
            reorder = finding.get("reorder_point", 0.0)
            diff = finding.get("difference", stock - reorder)
            actual_values = (
                f"Current Stock: {stock:g}, Reorder Point: {reorder:g}, "
                f"Difference: {diff:g}"
            )
            comparison = f"Current Stock ({stock:g}) < Reorder Point ({reorder:g})"
            reason = f"Stock level is below reorder threshold by {abs(diff):g} units."
            suggested_action = (
                f"Recommended for review: Assess replenishment schedule and reorder "
                f"requirements for {item} (deficit: {abs(diff):g} units)."
            )
            limitation = (
                "Based on snapshot inventory; does not account for supplier lead "
                "time or orders in transit."
            )

        elif finding_type == "Overstock Review":
            max_stock = finding.get("max_stock_level", 0.0)
            diff = finding.get("difference", stock - max_stock)
            actual_values = (
                f"Current Stock: {stock:g}, Max Stock Level: {max_stock:g}, "
                f"Difference: +{diff:g}"
            )
            comparison = f"Current Stock ({stock:g}) > Max Stock Level ({max_stock:g})"
            reason = f"Stock level exceeds maximum holding threshold by {diff:g} units."
            suggested_action = (
                f"Recommended for review: Evaluate inventory reduction strategies, "
                f"promotional discounts, or transfer options for {item} "
                f"(surplus: {diff:g} units)."
            )
            limitation = (
                "Storage capacity impact and holding cost rates may differ by warehouse."
            )

        elif finding_type == "Demand Coverage Risk":
            demand = finding.get("demand", 0.0)
            diff = finding.get("difference", stock - demand)
            actual_values = (
                f"Current Stock: {stock:g}, Recorded Demand: {demand:g}, "
                f"Difference: {diff:g}"
            )
            comparison = f"Current Stock ({stock:g}) < Recorded Demand ({demand:g})"
            reason = f"Recorded demand exceeds available stock by {abs(diff):g} units."
            suggested_action = (
                f"Recommended for review: Verify allocation priority and safety stock "
                f"for {item}."
            )
            limitation = (
                "Reflects static historical/current demand; does not reflect pending batch arrivals."
            )

        elif finding_type == "Predicted Demand Coverage Risk":
            pred = finding.get("predicted_demand", 0.0)
            diff = finding.get("difference", stock - pred)
            actual_values = (
                f"Current Stock: {stock:g}, Predicted Demand: {pred:g}, "
                f"Difference: {diff:g}"
            )
            comparison = (
                f"Current Stock ({stock:g}) < Predicted Demand ({pred:g})"
            )
            reason = (
                f"Predicted demand exceeds available on-hand stock by {abs(diff):g} units."
            )
            suggested_action = (
                f"Recommended for review: Evaluate forecasted demand trends and plan "
                f"stock alignment for {item}."
            )
            limitation = (
                "Model predictions have inherent variance and confidence intervals."
            )

        else:
            actual_values = finding.get("explanation", "")
            comparison = trigger
            reason = finding.get("explanation", "")
            suggested_action = f"Recommended for review: Inspect condition for {item}."
            limitation = "Observational finding; external validation required."

        rec = {
            "item": item,
            "recommendation_type": finding_type,
            "trigger_condition": trigger,
            "actual_values": actual_values,
            "comparison": comparison,
            "reason": reason,
            "suggested_action": suggested_action,
            "limitation": limitation,
            "human_review": HUMAN_REVIEW_TEXT,
        }
        recommendations.append(rec)

    recommendations_df = pd.DataFrame(recommendations)
    return RecommendationResult(
        available=True,
        message=None,
        recommendations=recommendations,
        recommendations_df=recommendations_df,
    )
