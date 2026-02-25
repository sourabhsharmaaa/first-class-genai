import pytest
import pandas as pd
from data_ingestion import get_zomato_data

def test_data_ingestion():
    # Attempt to load data
    df = get_zomato_data()
    
    # Base assertions
    assert df is not None
    assert not df.empty, "Dataframe should not be empty"
    
    # Check if necessary structure is present
    print("Dataset Columns:", df.columns.tolist())
    assert len(df.columns) > 0, "Dataframe should have columns"
    
    # Verification for cleaning steps
    if 'approx_cost(for two people)' in df.columns:
        assert pd.api.types.is_numeric_dtype(df['approx_cost(for two people)']), "Cost should be numeric"
        
    if 'rate' in df.columns:
        assert pd.api.types.is_numeric_dtype(df['rate']), "Rate should be numeric"
        
    if 'name' in df.columns and 'address' in df.columns:
        duplicates = df.duplicated(subset=['name', 'address']).sum()
        assert duplicates == 0, f"Found {duplicates} duplicate restaurants in the dataset"
