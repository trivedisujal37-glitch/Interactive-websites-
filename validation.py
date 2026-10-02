# hi hio
import os
import pandas as pd

REQUIRED_COLUMNS = ['item identifier', 'date', 'demand measure', 'current stock']
ALIAS_MAP = {
    'id': 'item identifier', 'item id': 'item identifier', 'item_id': 'item identifier',
    'date': 'date',
    'demand': 'demand measure', 'sales': 'demand measure',
    'stock': 'current stock', 'inventory': 'current stock',
    'lead time': 'delivery time', 'delivery': 'delivery time'
}

def validate_file(file_path):
    if not os.path.exists(file_path): return False, "File does not exist"
    if not file_path.endswith(('.csv', '.xlsx')): return False, "Invalid extension"
    return True, "Valid file"

def validate_dataframe(df):
    if df.empty: return False, "Empty dataset"
    df.columns = df.columns.str.lower().str.strip()
    
    target_sources = {}
    for col in df.columns:
        target = ALIAS_MAP.get(col, col)
        if target in target_sources:
            return False, f"Conflicting aliases detected: both '{target_sources[target]}' and '{col}' map to '{target}'"
        target_sources[target] = col
        
    df.rename(columns=ALIAS_MAP, inplace=True)
    
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing: return False, f"Missing required columns: {missing}"
    
    if 'date' in df.columns:
        try:
            pd.to_datetime(df['date'])
        except Exception:
            return False, "Invalid dates found"
            
    numeric_expected = [c for c in ['demand measure', 'current stock', 'delivery time'] if c in df.columns]
    for c in numeric_expected:
        if not pd.api.types.is_numeric_dtype(df[c]):
            return False, f"Non-numeric values found in {c}"
            
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if (df[col] < 0).any():
            return False, f"Negative values found in {col}"
            
    return True, "Valid data"
