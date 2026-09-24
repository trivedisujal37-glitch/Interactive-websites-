import pandas as pd

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    df.columns = df.columns.str.lower().str.strip()
    initial_rows = len(df)
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    return df, {"initial": initial_rows, "final": len(df)}
