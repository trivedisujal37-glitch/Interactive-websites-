import pandas as pd
from utils.validation import validate_file, validate_dataframe

def test_validate_file_invalid():
    assert validate_file("test.txt")[0] == False

def test_missing_required_column():
    df = pd.DataFrame({'item identifier': [1], 'date': ['2023'], 'demand measure': [10]})
    assert validate_dataframe(df)[0] == False

def test_alias_mapping():
    df = pd.DataFrame({'id': [1], 'date': ['2023'], 'sales': [10], 'inventory': [20]})
    assert validate_dataframe(df)[0] == True
    assert 'item identifier' in df.columns

def test_negative_numeric_values():
    df = pd.DataFrame({'item identifier': [1], 'date': ['2023'], 'demand measure': [-5], 'current stock': [10]})
    assert validate_dataframe(df)[0] == False

def test_empty_dataset():
    df = pd.DataFrame()
    assert validate_dataframe(df)[0] == False

def test_conflicting_aliases():
    df = pd.DataFrame({'stock': [10], 'inventory': [20], 'item identifier': [1], 'date': ['2023'], 'demand measure': [5]})
    res, msg = validate_dataframe(df)
    assert res == False
    assert "Conflicting aliases detected" in msg

def test_invalid_dates():
    df = pd.DataFrame({'item identifier': [1], 'date': ['not_a_date'], 'demand measure': [5], 'current stock': [10]})
    res, msg = validate_dataframe(df)
    assert res == False
    assert "Invalid dates" in msg

def test_non_numeric_values():
    df = pd.DataFrame({'item identifier': [1], 'date': ['2023'], 'demand measure': ['ten'], 'current stock': [10]})
    res, msg = validate_dataframe(df)
    assert res == False
    assert "Non-numeric values" in msg
