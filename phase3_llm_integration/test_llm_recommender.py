import pytest
import pandas as pd
from llm_recommender import generate_recommendation_prompt

@pytest.fixture
def mock_df():
    return pd.DataFrame({
        'name': ['ECHOES Koramangala', 'Pin Me Down'],
        'rate': [4.7, 4.5],
        'location': ['Koramangala 5th Block', 'BTM'],
        'cuisines': ['Chinese, American, Continental, Italian, North Indian', 'Continental, Mexican, Chinese, North Indian'],
        'approx_cost(for two people)': [750.0, 800.0]
    })

def test_prompt_generation_with_data(mock_df):
    prefs = {"location": "BTM / Koramangala", "cuisine": "North Indian/Continental", "max_price": 800}
    prompt = generate_recommendation_prompt(mock_df, prefs)
    
    # Assert preferences are mentioned
    assert "BTM" in prompt
    assert "North Indian" in prompt
    
    # Assert restaurant details are mentioned
    assert "ECHOES Koramangala" in prompt
    assert "Pin Me Down" in prompt
    assert "4.7⭐" in prompt

def test_prompt_generation_empty_data():
    empty_df = pd.DataFrame()
    prefs = {"location": "Nowhere", "cuisine": "Alien Food"}
    
    prompt = generate_recommendation_prompt(empty_df, prefs)
    
    assert "Nowhere" in prompt
    assert "Alien Food" in prompt
    assert "Unfortunately, no restaurants exactly matched" in prompt
