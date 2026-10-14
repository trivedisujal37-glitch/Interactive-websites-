"""Unit tests for format_compact helper."""

import math
import numpy as np
import pytest
from modules.ui_charts import format_compact, format_full_value


def test_format_compact_spec_cases():
    """Verify all explicit edge cases and examples from the task specification."""
    # Zero
    assert format_compact(0) == "0"
    assert format_compact(0.0) == "0"
    
    # Below 1,000 plain numbers
    assert format_compact(999) == "999"
    assert format_compact(12.5) == "12.5"
    assert format_compact(450.0) == "450"
    
    # 1,000 to 999,999 show K
    assert format_compact(1000) == "1K"
    assert format_compact(24000) == "24K"
    assert format_compact(34000) == "34K"
    assert format_compact(74876.4) == "74.9K"
    
    # Rollover near 1M
    assert format_compact(999999) == "1M"
    assert format_compact(1000000) == "1M"
    
    # Millions & Billions
    assert format_compact(1782430) == "1.78M"
    assert format_compact(2.5e9) == "2.5B"
    
    # Negatives
    assert format_compact(-3700) == "-3.7K"
    assert format_compact(-15) == "-15"
    assert format_compact(-1200000) == "-1.2M"
    
    # Missing, NaN, and None
    assert format_compact(None) == "-"
    assert format_compact(float("nan")) == "-"
    assert format_compact(np.nan) == "-"
    assert format_compact(float("inf")) == "-"
    
    # Numpy numeric types
    assert format_compact(np.float64(12500.0)) == "12.5K"
    assert format_compact(np.int64(450)) == "450"
    assert format_compact(np.int32(1000000)) == "1M"
    
    # String number inputs
    assert format_compact("12345") == "12.3K"
    assert format_compact("74876.4") == "74.9K"
    assert format_compact("1,782,430") == "1.78M"
    assert format_compact("invalid") == "-"
    assert format_compact("") == "-"


def test_format_compact_prefix_suffix():
    """Verify prefix and suffix handling without injecting unneeded symbols."""
    assert format_compact(24000, prefix="$") == "$24K"
    assert format_compact(1782430, prefix="$", suffix=" USD") == "$1.78M USD"
    assert format_compact(-3700, prefix="$") == "$-3.7K"
    assert format_compact(None, prefix="$") == "-"


def test_format_full_value():
    """Verify exact value preserved for tooltips."""
    assert format_full_value(1782430) == "1,782,430"
    assert format_full_value(74876.4) == "74,876.40"
    assert format_full_value(None) == "-"
    assert format_full_value(float("nan")) == "-"


def test_four_plus_digit_k_and_m_formatting():
    """Verify numbers with more than 3 or 4 digits format with K and M for Reporting."""
    # 4 digits (thousands)
    assert format_compact(1000) == "1K"
    assert format_compact(1500) == "1.5K"
    assert format_compact(9999) == "10K"
    assert format_compact(24000) == "24K"
    assert format_compact(74876.90) == "74.9K"
    
    # 6-7 digits (millions)
    assert format_compact(1000000) == "1M"
    assert format_compact(1782443.00) == "1.78M"
    assert format_compact(1904243.90) == "1.9M"
    assert format_compact(45000000) == "45M"
    
    # Tooltip exact values are preserved
    assert format_full_value(1782443.00) == "1,782,443"
    assert format_full_value(74876.90) == "74,876.90"

