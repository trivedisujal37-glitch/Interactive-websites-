import numpy as np
import pandas as pd

def calculate_inventory(df):
    df['average demand'] = df['demand measure']
    
    # Lead time comes from 'delivery time', fallback is 1 day
    df['lead time'] = df.get('delivery time', 1)
    
    # Safety stock = Z * std_demand * sqrt(lead time). Z=1.65 (~95% service level)
    if 'item identifier' in df.columns and len(df) > 1:
        std_demand = df.groupby('item identifier')['demand measure'].transform('std').fillna(df['demand measure'] * 0.1)
    else:
        std_demand = df['demand measure'] * 0.1
        
    df['safety stock'] = 1.65 * std_demand * np.sqrt(df['lead time'])
    df['reorder point'] = (df['average demand'] * df['lead time']) + df['safety stock']
    df['stock gap'] = df['current stock'] - df['reorder point']
    
    def get_status(row):
        gap = row['stock gap']
        # Priority Review: Negative gap AND stock is 0
        if gap < 0 and row['current stock'] == 0: return "Priority Review"
        # Low Stock: Negative gap
        if gap < 0: return "Low Stock"
        # Overstock: Gap is huge compared to reorder point
        if gap > (row['reorder point'] * 2) + 1: return "Overstock"
        # Review Required: Gap is positive but very close to 0
        if gap < (row['reorder point'] * 0.1): return "Review Required"
        # Sufficient: otherwise
        return "Sufficient"
        
    df['inventory status'] = df.apply(get_status, axis=1)
    return df
