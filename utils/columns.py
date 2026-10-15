"""Shared column resolver for supply chain datasets.

Provides robust, unambiguous mapping from arbitrary dataframe column headers
to canonical supply chain data keys without substring guessing or overlaps.
"""

from typing import Any
import re
import pandas as pd

# Canonical keys and their allowed aliases.
# Each alias is listed in preference order.
# All alias sets are strictly disjoint after normalization.
ALIAS_TABLE: dict[str, list[str]] = {
    "item_id": [
        "item_id", "itemid", "item", "sku", "product", "productid", "item_identifier", "itemidentifier"
    ],
    "item_name": [
        "item_name", "itemname", "product_name", "productname"
    ],
    "date": [
        "date"
    ],
    "demand": [
        "demand", "quantity_demanded", "quantitydemanded", "quantity_sold", "quantitysold", "sales", "usage", "demand_measure", "demandmeasure"
    ],
    "current_stock": [
        "current_stock", "currentstock", "stock", "onhand", "inventory"
    ],
    "reorder_point": [
        "reorder_point", "reorderpoint", "reorder_point_calc", "reorderpointcalc"
    ],
    "max_stock": [
        "max_stock_level", "maxstocklevel", "max_stock", "maxstock"
    ],
    "unit_price": [
        "unit_price", "unitprice", "price"
    ],
    "supplier_id": [
        "supplier_id", "supplierid", "supplier"
    ],
    "delivery_time": [
        "delivery_time", "deliverytime", "lead_time", "leadtime", "lead_days", "leaddays", "delivery_time_days", "deliverytimedays"
    ],
    "quantity_supplied": [
        "quantity_supplied", "quantitysupplied", "qty_supplied", "qtysupplied", "received", "units_supplied", "unitssupplied"
    ],
    "supplier_unit_price": [
        "supplier_unit_price", "supplierunitprice", "purchase_price", "purchaseprice"
    ],
    "transportation_cost": [
        "transportation_cost", "transportationcost", "freight", "shipping_cost", "shippingcost"
    ],
    "holding_cost": [
        "holding_cost", "holdingcost", "annual_holding_cost_per_unit", "annualholdingcostperunit"
    ],
    "purchase_cost": [
        "purchase_cost", "purchasecost"
    ],
    "category": [
        "category", "item_category", "itemcategory", "product_category", "productcategory"
    ],
}


def normalize_column_name(name: Any) -> str:
    """Normalize a column name by lowercasing and removing spaces, underscores, and hyphens."""
    if name is None:
        return ""
    return re.sub(r"[\s_\-]+", "", str(name).lower())


# Build lookup mapping: normalized_alias -> (canonical_key, priority_index)
_NORM_LOOKUP: dict[str, tuple[str, int]] = {}
for _canon_key, _aliases in ALIAS_TABLE.items():
    for _idx, _alias in enumerate(_aliases):
        _norm = normalize_column_name(_alias)
        if _norm in _NORM_LOOKUP:
            _existing_key, _ = _NORM_LOOKUP[_norm]
            if _existing_key != _canon_key:
                raise ValueError(f"Conflicting alias detected in ALIAS_TABLE: '{_norm}' maps to '{_existing_key}' and '{_canon_key}'")
            continue
        _NORM_LOOKUP[_norm] = (_canon_key, _idx)


def find_col(df: pd.DataFrame | None, key: str) -> str | None:
    """Find the real column name in df matching the canonical key.

    Uses exact normalized alias matching (never substring matching).
    Returns None if no matching column exists.
    """
    if df is None or not hasattr(df, "columns") or len(df.columns) == 0:
        return None

    target_key = normalize_column_name(key)
    # If the user passed an alias instead of the key, resolve it to canonical key
    if target_key in _NORM_LOOKUP:
        target_key = _NORM_LOOKUP[target_key][0]

    best_match: str | None = None
    best_priority: int = 999999

    for col in df.columns:
        norm_col = normalize_column_name(col)
        if norm_col in _NORM_LOOKUP:
            canon_key, priority = _NORM_LOOKUP[norm_col]
            if canon_key == target_key:
                if priority < best_priority:
                    best_priority = priority
                    best_match = col

    return best_match


def find_cols(df: pd.DataFrame | None, keys: list[str]) -> dict[str, str | None]:
    """Find multiple real column names for a list of canonical keys."""
    return {k: find_col(df, k) for k in keys}
