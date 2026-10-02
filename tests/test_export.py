"""Tests for utils/export.py."""

import io
import pandas as pd
import pytest
from utils.export import (
    EXCEL_AVAILABLE,
    export_to_csv,
    export_to_excel,
    get_available_export_formats,
)


def test_export_empty_or_none():
    assert export_to_csv(None) is None
    assert export_to_csv(pd.DataFrame()) is None

    assert export_to_excel(None) is None
    assert export_to_excel(pd.DataFrame()) is None


def test_export_csv_contains_real_values():
    df = pd.DataFrame(
        {
            "Item": ["Widget Alpha", "Sensor Beta"],
            "Cost": [123.45, 678.90],
        }
    )
    csv_bytes = export_to_csv(df)
    assert csv_bytes is not None
    assert isinstance(csv_bytes, bytes)

    decoded = csv_bytes.decode("utf-8")
    assert "Widget Alpha" in decoded
    assert "Sensor Beta" in decoded
    assert "123.45" in decoded
    assert "678.9" in decoded


def test_get_available_export_formats():
    formats = get_available_export_formats()
    assert "csv" in formats
    if EXCEL_AVAILABLE:
        assert "xlsx" in formats
    else:
        assert "xlsx" not in formats


def test_excel_roundtrip_if_openpyxl_available():
    df = pd.DataFrame(
        {
            "Item": ["Alpha", "Beta"],
            "Quantity": [10, 20],
        }
    )
    excel_bytes = export_to_excel(df)
    if EXCEL_AVAILABLE:
        assert excel_bytes is not None
        assert isinstance(excel_bytes, bytes)
        # Read back into DataFrame
        df_read = pd.read_excel(io.BytesIO(excel_bytes))
        assert list(df_read["Item"]) == ["Alpha", "Beta"]
        assert list(df_read["Quantity"]) == [10, 20]
    else:
        assert excel_bytes is None
