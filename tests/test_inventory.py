import pandas as pd
from modules.inventory import calculate_inventory
import numpy as np

def test_inventory_formula_correctness():
    df = pd.DataFrame({'demand measure': [100], 'delivery time': [4], 'current stock': [400], 'item identifier': [1]})
    res = calculate_inventory(df)
    assert np.isclose(res['reorder point'].iloc[0], 433.0)

def test_zero_demand_item():
    df = pd.DataFrame({'demand measure': [0], 'delivery time': [2], 'current stock': [10]})
    res = calculate_inventory(df)
    assert res['reorder point'].iloc[0] == 0

def test_inventory_statuses():
    df = pd.DataFrame({
        'item identifier': [1, 2, 3, 4, 5],
        'demand measure': [10, 10, 10, 10, 10],
        'delivery time': [1, 1, 1, 1, 1],
        # ROP = ~11.65
        # Priority Review: gap < 0 AND stock == 0
        # Low Stock: gap < 0 (stock > 0)
        # Review Required: gap < ROP * 0.1 (gap < 1.16)
        # Sufficient: otherwise
        # Overstock: gap > ROP * 2 + 1 (gap > 24.3)
        'current stock': [0, 5, 12, 15, 100]
    })
    res = calculate_inventory(df)
    statuses = res['inventory status'].tolist()
    
    assert "Priority Review" in statuses
    assert "Low Stock" in statuses
    assert "Review Required" in statuses
    assert "Sufficient" in statuses
    assert "Overstock" in statuses
