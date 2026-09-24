import pandas as pd
from utils.validation import ALIAS_MAP

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    df['original_row_index'] = df.index
    df.columns = df.columns.str.lower().str.strip()
    df.rename(columns=ALIAS_MAP, inplace=True)
    
    initial_rows = len(df)
    cols_to_check = df.columns.difference(['original_row_index'])
    df = df.dropna(how='all', subset=cols_to_check)
    df = df.drop_duplicates(subset=cols_to_check)
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(0)
            
    return df, {"initial": initial_rows, "final": len(df), "fixed": initial_rows - len(df)}
