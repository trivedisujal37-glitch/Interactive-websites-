import pandas as pd
from modules.data_management import load_and_clean_data

def test_csv_upload_and_duplicates(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock,unknown col\n1,2023,10,20,A\n1,2023,10,20,A\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 1
    assert 'unknown col' in df.columns
    assert summary['fixed'] == 1

def test_missing_values(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n1,2023,,20\n")
    df, _ = load_and_clean_data(str(p))
    assert df['demand measure'].iloc[0] == 0.0

def test_zero_row_after_cleaning(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n,,,\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 0

def test_missing_optional_columns(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,date,sales,stock\n1,2023,10,20\n")
    df, _ = load_and_clean_data(str(p))
    assert 'item identifier' in df.columns
    assert 'delivery time' not in df.columns

def test_one_row_dataset(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n1,2023,10,20\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 1
    assert summary['initial'] == 1
