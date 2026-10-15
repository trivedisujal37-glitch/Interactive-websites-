"""Tests for shared column resolver (utils/columns.py)."""

import pandas as pd
import pytest
from utils.columns import find_col, find_cols, normalize_column_name, ALIAS_TABLE


def test_column_resolver_aliases():
    df = pd.DataFrame(columns=[
        "Demand", "Quantity_Demanded", "Quantity Demanded", "sales",
        "Current Stock", "Current_Stock", "Delivery Time", "Delivery_Time"
    ])
    
    # Resolves canonical demand without ambiguous guessing
    df_single_dem = pd.DataFrame(columns=["Quantity_Demanded"])
    assert find_col(df_single_dem, "demand") == "Quantity_Demanded"

    df_space_dem = pd.DataFrame(columns=["Quantity Demanded"])
    assert find_col(df_space_dem, "demand") == "Quantity Demanded"

    df_sales = pd.DataFrame(columns=["sales"])
    assert find_col(df_sales, "demand") == "sales"

    # Current stock resolution
    df_stock_space = pd.DataFrame(columns=["Current Stock"])
    assert find_col(df_stock_space, "current_stock") == "Current Stock"

    df_stock_under = pd.DataFrame(columns=["Current_Stock"])
    assert find_col(df_stock_under, "current_stock") == "Current_Stock"

    # Delivery time resolution
    df_deliv_space = pd.DataFrame(columns=["Delivery Time"])
    assert find_col(df_deliv_space, "delivery_time") == "Delivery Time"

    df_deliv_under = pd.DataFrame(columns=["Delivery_Time"])
    assert find_col(df_deliv_under, "delivery_time") == "Delivery_Time"


def test_no_substring_guessing():
    # 'Quantity Supplied' must NOT match 'demand' even though both have 'quantity'
    # and must NOT match 'current_stock' even though older code guessed on 'qty/quantity'
    df = pd.DataFrame(columns=["Quantity Supplied", "Supplier_ID"])
    assert find_col(df, "demand") is None
    assert find_col(df, "current_stock") is None
    assert find_col(df, "quantity_supplied") == "Quantity Supplied"


def test_no_double_matching_and_disjoint_aliases():
    # Check that every normalized alias across all keys in ALIAS_TABLE is unique
    seen = {}
    for key, aliases in ALIAS_TABLE.items():
        for alias in aliases:
            norm = normalize_column_name(alias)
            if norm in seen:
                assert seen[norm] == key, f"Alias '{norm}' matched multiple keys: '{seen[norm]}' and '{key}'"
            seen[norm] = key


def test_find_cols_batch():
    df = pd.DataFrame(columns=["Item_ID", "Current_Stock", "Demand"])
    res = find_cols(df, ["item_id", "current_stock", "demand", "delivery_time"])
    assert res == {
        "item_id": "Item_ID",
        "current_stock": "Current_Stock",
        "demand": "Demand",
        "delivery_time": None
    }
