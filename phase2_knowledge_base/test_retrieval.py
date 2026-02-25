import pytest
import pandas as pd
from retrieval import retrieve_restaurants

@pytest.fixture
def sample_df():
    data = {
        'name': ['Restaurant A', 'Restaurant B', 'Restaurant C', 'Restaurant D'],
        'location': ['BTM', 'Koramangala 5th Block', 'BTM', 'Indiranagar'],
        'listed_in(city)': ['BTM', 'Koramangala', 'BTM', 'Indiranagar'],
        'cuisines': ['North Indian, Chinese', 'South Indian', 'North Indian', 'Cafe'],
        'approx_cost(for two people)': [500.0, 300.0, 1500.0, 800.0],
        'rate': [4.5, 3.8, 4.0, 4.2]
    }
    return pd.DataFrame(data)

def test_location_filter(sample_df):
    result = retrieve_restaurants(df=sample_df, location='BTM', top_n=5)
    assert len(result) == 2
    assert all('BTM' in loc for loc in result['location'])

def test_cuisine_filter(sample_df):
    result = retrieve_restaurants(df=sample_df, cuisine='North Indian', top_n=5)
    assert len(result) == 2
    assert all('North Indian'.lower() in cuisine.lower() for cuisine in result['cuisines'])

def test_price_filter(sample_df):
    result = retrieve_restaurants(df=sample_df, max_price=600.0, top_n=5)
    assert len(result) == 2
    assert all(price <= 600.0 for price in result['approx_cost(for two people)'])

def test_rating_filter(sample_df):
    result = retrieve_restaurants(df=sample_df, min_rating=4.0, top_n=5)
    assert len(result) == 3
    assert all(rate >= 4.0 for rate in result['rate'])

def test_combined_filters(sample_df):
    result = retrieve_restaurants(
        df=sample_df, 
        location='BTM', 
        cuisine='North Indian', 
        max_price=1000.0, 
        min_rating=4.0,
        top_n=5
    )
    assert len(result) == 1
    assert result.iloc[0]['name'] == 'Restaurant A'
    
def test_sorting_and_top_n(sample_df):
    result = retrieve_restaurants(df=sample_df, top_n=2)
    assert len(result) == 2
    # Should sort by rating descending, so 4.5 then 4.2
    assert result.iloc[0]['name'] == 'Restaurant A'
    assert result.iloc[1]['name'] == 'Restaurant D'
