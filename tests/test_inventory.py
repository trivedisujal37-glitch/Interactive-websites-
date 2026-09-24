import pandas as pd
from modules.inventory import calculate_inventory

def test_inventory():
    df = pd.DataFrame({'demand measure': [10], 'delivery time': [2], 'current stock': [15]})
    res = calculate_inventory(df)
    assert 'reorder point' in res.columns
