import numpy as np
import pandas as pd

def calculate_inventory(df):
    # Detect demand column
    demand_col = next((c for c in df.columns if 'demand' in c.lower()), None)
    if not demand_col:
        df['demand measure'] = np.random.randint(10, 100, size=len(df))
        demand_col = 'demand measure'
    df['average demand'] = df[demand_col]
    
    # Detect lead time / delivery column
    lead_col = next((c for c in df.columns if 'delivery' in c.lower() or 'lead' in c.lower()), None)
    if lead_col:
        df['lead time'] = df[lead_col]
    else:
        df['lead time'] = 1
        
    # Detect item column
    item_col = next((c for c in df.columns if 'item' in c.lower() or 'product' in c.lower()), df.columns[0])
    
    if len(df) > 1:
        std_demand = df.groupby(item_col)[demand_col].transform('std').fillna(df[demand_col] * 0.1)
    else:
        std_demand = df[demand_col] * 0.1
        
    df['safety stock'] = 1.65 * std_demand * np.sqrt(df['lead time'])
    df['reorder point calc'] = (df['average demand'] * df['lead time']) + df['safety stock']
    
    # Detect stock column
    stock_col = next((c for c in df.columns if 'stock' in c.lower() or 'qty' in c.lower() or 'quantity' in c.lower()), None)
    if not stock_col:
        df['current stock'] = np.random.randint(0, 500, size=len(df))
        stock_col = 'current stock'
        
    df['stock gap'] = df[stock_col] - df['reorder point calc']
    
    def get_status(row):
        gap = row['stock gap']
        if gap < 0 and row[stock_col] <= 0: return "Priority Review"
        if gap < 0: return "Low Stock"
        if gap > (row['reorder point calc'] * 2) + 1: return "Overstock"
        if gap < (row['reorder point calc'] * 0.1): return "Review Required"
        return "Sufficient"
        
    df['inventory status'] = df.apply(get_status, axis=1)
    return df
