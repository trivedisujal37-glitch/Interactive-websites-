import pandas as pd
from modules.data_management import load_and_clean_data

def test_clean_data(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item identifier,date,demand measure,current stock\n1,2023-01-01,10,20\n1,2023-01-01,10,20\n")
    df, summary = load_and_clean_data(str(p))
    assert len(df) == 1
