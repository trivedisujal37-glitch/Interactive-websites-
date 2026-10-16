import io
import numpy as np
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
    # Corrected per requirement: blank stays blank (NaN), never fillna(0)
    assert pd.isna(df['demand measure'].iloc[0])

def test_zero_row_after_cleaning(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n,,,\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 0

def test_missing_optional_columns(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,date,sales,stock\n1,2023,10,20\n")
    df, _ = load_and_clean_data(str(p))
    # Corrected per requirement: preserve original column names without renaming
    assert 'id' in df.columns
    assert 'sales' in df.columns
    assert 'stock' in df.columns
    assert 'delivery time' not in df.columns

def test_one_row_dataset(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n1,2023,10,20\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 1
    assert summary['initial'] == 1


def test_excel_upload_and_blank_delivery_time(tmp_path):
    df_raw = pd.DataFrame({
        "Item": ["A", "B"],
        "Demand": [10, 20],
        "Delivery Time": [np.nan, 3.5]
    })
    p = tmp_path / "test.xlsx"
    df_raw.to_excel(p, index=False)
    cleaned, report = load_and_clean_data(str(p))
    assert len(cleaned) == 2
    # Blank delivery column stays NaN
    assert pd.isna(cleaned["Delivery Time"].iloc[0])
    assert cleaned["Delivery Time"].iloc[1] == 3.5
    assert "Demand Prediction" in report["module_readiness"]  # missing date
 

def test_category_whitespace_trimmed_without_casing_change(tmp_path):
    df_raw = pd.DataFrame({
        "Item": ["Item 1", "Item 2"],
        "Category": ["FMCG", " Dairy  Products "]
    })
    p = tmp_path / "test_cat.csv"
    df_raw.to_csv(p, index=False)
    cleaned, _ = load_and_clean_data(str(p))
    assert cleaned["Category"].iloc[0] == "FMCG"
    assert cleaned["Category"].iloc[1] == "Dairy Products"

