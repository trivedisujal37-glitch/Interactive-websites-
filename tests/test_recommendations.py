"""Tests for modules/recommendations.py."""

import pytest
from modules.recommendations import (
    HUMAN_REVIEW_TEXT,
    REQUIRED_FIELDS,
    build_recommendations,
)


def test_empty_or_none_findings_unavailable():
    res_none = build_recommendations(None)
    assert not res_none.available
    assert (
        res_none.message
        == "No recommendations: no optimization findings were generated."
    )
    assert res_none.recommendations == []

    res_empty = build_recommendations([])
    assert not res_empty.available
    assert (
        res_empty.message
        == "No recommendations: no optimization findings were generated."
    )


def test_required_fields_and_no_forbidden_wording():
    sample_findings = [
        {
            "item": "Widget A",
            "finding_type": "Reorder Review",
            "trigger_condition": "Current Stock < Reorder Point",
            "current_stock": 320.0,
            "reorder_point": 700.0,
            "difference": -380.0,
            "explanation": "Current Stock (320) is below the Reorder Point (700) by 380 units.",
        },
        {
            "item": "Gadget B",
            "finding_type": "Overstock Review",
            "trigger_condition": "Current Stock > Max Stock Level",
            "current_stock": 1200.0,
            "max_stock_level": 800.0,
            "difference": 400.0,
            "explanation": "Current Stock (1200) exceeds the Max Stock Level (800) by 400 units.",
        },
    ]

    res = build_recommendations(sample_findings)
    assert res.available
    assert len(res.recommendations) == 2

    for rec in res.recommendations:
        # Every required field present
        for field in REQUIRED_FIELDS:
            assert field in rec, f"Missing field {field} in recommendation"
            assert rec[field] is not None and rec[field] != ""

        # Forbidden wording check: "order more inventory" must NOT appear
        full_text = " ".join(str(v).lower() for v in rec.values())
        assert "order more inventory" not in full_text

        # "recommended for review" MUST appear
        assert "recommended for review" in rec["suggested_action"].lower()

        # Human review verification
        assert rec["human_review"] == HUMAN_REVIEW_TEXT


def test_overstock_wording():
    findings = [
        {
            "item": "Overstock Widget",
            "finding_type": "Overstock Review",
            "trigger_condition": "Current Stock > Max Stock Level",
            "current_stock": 1000.0,
            "max_stock_level": 600.0,
            "difference": 400.0,
        }
    ]
    res = build_recommendations(findings)
    assert res.available
    rec = res.recommendations[0]
    assert rec["recommendation_type"] == "Overstock Review"
    assert "surplus: 400 units" in rec["suggested_action"]
    assert "order more inventory" not in rec["suggested_action"].lower()
    assert "recommended for review" in rec["suggested_action"].lower()
