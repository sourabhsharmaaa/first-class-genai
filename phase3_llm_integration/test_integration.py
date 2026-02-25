import pytest
import pandas as pd
from llm_recommender import get_llm_recommendation

def test_groq_api_live_connection():
    """
    Live integration test that actually queries the Groq API.
    Requires GROQ_API_KEY to be set in the .env file.
    """
    # Create a tiny mock dataframe to send to the LLM
    mock_df = pd.DataFrame({
        'name': ['Integration Test Cafe'],
        'rate': [4.9],
        'location': ['Tech Park'],
        'cuisines': ['Coffee, Snacks'],
        'approx_cost(for two people)': [300.0]
    })
    
    prefs = {
        "location": "Tech Park",
        "cuisine": "Coffee",
        "max_price": 500
    }
    
    # Send request to Groq
    response = get_llm_recommendation(mock_df, prefs)
    
    # Assertions
    assert isinstance(response, str), "Response must be a string."
    assert len(response) > 50, "Response string is unnaturally short."
    
    # Check that we didn't hit our error fallback clauses
    assert "Groq client is not initialized" not in response, "API Key missing or client initialization failed."
    assert "Sorry, I encountered an error generating your recommendation" not in response, f"API Call failed. Response: {response}"
    
    # Check if the LLM mentioned the restaurant or details
    assert "Integration" in response or "Cafe" in response, "LLM formulation failed to mention the retrieved restaurant."
    
    print("\n--- Live Groq response ---\n", response)

if __name__ == "__main__":
    test_groq_api_live_connection()
