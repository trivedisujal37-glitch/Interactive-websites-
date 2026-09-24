import os
import pandas as pd

REQUIRED_COLUMNS = ['item identifier', 'date', 'demand measure', 'current stock']

def validate_file(file_path):
    if not os.path.exists(file_path): return False, "File does not exist"
    if not file_path.endswith(('.csv', '.xlsx')): return False, "Invalid extension"
    return True, "Valid file"

def validate_dataframe(df):
    if df.empty: return False, "Empty dataset"
    df.columns = df.columns.str.lower().str.strip()
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing: return False, f"Missing required columns: {missing}"
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if (df[col] < 0).any():
            return False, f"Negative values found in {col}"
            
    return True, "Valid data"
