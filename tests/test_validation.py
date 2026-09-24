import pandas as pd
from utils.validation import validate_file, validate_dataframe

def test_validate_file():
    assert validate_file("test.txt")[0] == False

def test_validate_dataframe():
    df = pd.DataFrame({'item identifier': [1], 'date': ['2023'], 'demand measure': [-1], 'current stock': [10]})
    assert validate_dataframe(df)[0] == False
