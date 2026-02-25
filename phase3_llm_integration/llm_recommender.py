import os
import pandas as pd
import logging
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file (if present)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
# It will automatically pick up GROQ_API_KEY from the environment
try:
    client = Groq()
except Exception as e:
    logger.warning(f"Failed to initialize Groq client: {e}")
    client = None

from functools import lru_cache

@lru_cache(maxsize=100)
def parse_search_query(query: str, model: str = "llama-3.1-8b-instant") -> dict:
    """
    Parses a natural language search query into structured filters using Groq.
    Cached to speed up repeated queries.
    """
    if not client or not query:
        return {}

    prompt = f'Parse this query into JSON: "{query}". Extract: location, cuisine, max_price, min_rating. Return ONLY valid JSON.'

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0,
        )
        import json
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error parsing search query: {e}")
        return {}

def generate_recommendation_prompt(df: pd.DataFrame, preferences: dict) -> str:
    """
    Constructs a concise prompt for faster generation.
    """
    prompt = f"Recommend these restaurants for preferences: {preferences}.\n\n"
    
    if df.empty:
        return '{"summary": "No matches found.", "restaurants": []}'
        
    for _, row in df.iterrows():
        prompt += f"- {row.get('name')}: {row.get('rate')} stars, ₹{row.get('approx_cost(for two people)')}, Location: {row.get('location')}, Cuisines: {row.get('cuisines')}\n"
        
    prompt += """
Output strictly valid JSON with a detailed 'summary' paragraph and an array of 'restaurants' with: id, name, rating, costForTwo, address, cuisines, and 'aiReason' (2-3 sentences).
Example:
{
  "summary": "...",
  "restaurants": [{"id": 1, "name": "...", "aiReason": "..."}]
}
"""
    return prompt

def get_llm_recommendation(df: pd.DataFrame, preferences: dict, model: str = "llama-3.1-8b-instant") -> str:
    """
    Calls the Groq API to generate JSON-formatted recommendations.
    """
    if not client:
        return '{"restaurants": []}'
        
    prompt = generate_recommendation_prompt(df, preferences)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a local food guide. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=800, # Reduced to speed up response
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return '{"restaurants": []}'
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return '{"restaurants": []}'

if __name__ == "__main__":
    # A simple mock DB result for manual testing
    mock_data = pd.DataFrame({
        'name': ['ECHOES Koramangala', 'Pin Me Down'],
        'rate': [4.7, 4.5],
        'location': ['Koramangala 5th Block', 'BTM'],
        'cuisines': ['Chinese, American, Continental, Italian, North Indian', 'Continental, Mexican, Chinese, North Indian'],
        'approx_cost(for two people)': [750.0, 800.0]
    })
    
    fake_prefs = {
        "location": "BTM / Koramangala",
        "cuisine": "North Indian/Continental",
        "max_price": 800
    }
    
    print("Testing LLM generation with mock data...\n")
    print(get_llm_recommendation(mock_data, fake_prefs))
