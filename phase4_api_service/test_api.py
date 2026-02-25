import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import pandas as pd

client = TestClient(app)

# Create a mock dataframe to substitute the real massive one
mock_df = pd.DataFrame({
    'name': ['Test Restaurant'],
    'rate': [4.5],
    'location': ['Tech Park'],
    'listed_in(city)': ['Tech Park City'],
    'cuisines': ['Cafe, Bakery'],
    'approx_cost(for two people)': [400.0]
})

from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_get_zomato_data():
    """Patches the initial data load across the entire module so startup events don't wipe it."""
    with patch('main.get_zomato_data') as mock_load:
        mock_load.return_value = mock_df
        yield mock_load

def test_health_check():
    # Wrap in `with client` to trigger startup events during tests
    with client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "dataset_loaded": True}

@patch('main.get_llm_recommendation')
def test_recommendation_endpoint(mock_get_llm_recommendation):
    # Setup our mock LLM return string
    mock_get_llm_recommendation.return_value = "Here is a mock recommendation from LLM!"
    
    # Payload for POST request
    payload = {
        "location": "Tech Park",
        "cuisine": "Cafe",
        "max_price": 500.0,
        "min_rating": 4.0
    }
    
    # Wrap in `with client` to trigger startup events during tests
    with client:
        response = client.post("/recommend", json=payload)
    
        assert response.status_code == 200
        data = response.json()
        
        # Validate the structure and logic
        assert data["query"]["location"] == "Tech Park"
        assert data["restaurant_count"] == 1
        assert data["recommendation_text"] == "Here is a mock recommendation from LLM!"
        
        # Ensure our LLM mock was called exactly once
        mock_get_llm_recommendation.assert_called_once()
