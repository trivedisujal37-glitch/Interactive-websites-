import pandas as pd

def calculate_inventory(df):
    df['average demand'] = df['demand measure']
    df['lead time'] = df.get('delivery time', 1)
    df['safety stock'] = df['average demand'] * 0.2
    df['reorder point'] = (df['average demand'] * df['lead time']) + df['safety stock']
    df['stock gap'] = df['current stock'] - df['reorder point']
    
    def status(row):
        if row['stock gap'] < 0: return "Low Stock"
        if row['stock gap'] > row['reorder point']: return "Overstock"
        return "Sufficient"
        
    df['inventory status'] = df.apply(status, axis=1)
    return df
