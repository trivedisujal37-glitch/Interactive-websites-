"""Export utilities for Supply Chain Optimization System.

Supports CSV and Excel (openpyxl) export formats.
"""

import io
import pandas as pd

try:
    import openpyxl  # noqa: F401

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


def export_to_csv(df: pd.DataFrame | None) -> bytes | None:
    """Export DataFrame to UTF-8 encoded CSV bytes. Returns None if df is None/empty."""
    if df is None or df.empty:
        return None
    return df.to_csv(index=False).encode("utf-8")


def export_to_excel(df: pd.DataFrame | None) -> bytes | None:
    """Export DataFrame to Excel (.xlsx) bytes. Returns None if openpyxl unavailable or df None/empty."""
    if not EXCEL_AVAILABLE or df is None or df.empty:
        return None

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()


def get_available_export_formats() -> list[str]:
    """Return available export formats based on installed libraries."""
    formats = ["csv"]
    if EXCEL_AVAILABLE:
        formats.append("xlsx")
    return formats
