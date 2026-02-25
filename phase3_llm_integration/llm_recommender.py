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
    Constructs a prompt for stable and customized recommendations.
    """
    if df.empty:
        return '{"summary": "No exact matches found. Try broadening your criteria.", "restaurants": []}'
        
    prompt = f"Recommend these SPECIFIC restaurants from our Zomato dataset for preferences: {preferences}.\n\n"
    prompt += "RESTAURANTS TO CHOOSE FROM (USE ONLY THESE):\n"
    
    for _, row in df.iterrows():
        # Clean price string for the prompt
        price = str(row.get('approx_cost(for two people)', 'N/A')).replace('.0', '')
        prompt += f"- {row.get('name')}: {row.get('rate')} stars, Cost: ₹{price}, Location: {row.get('location')}, Cuisines: {row.get('cuisines')}, Address: {row.get('address')}\n"
        
    prompt += """
CRITICAL RULES:
1. You MUST ONLY use the restaurant names and data provided in the list above. 
2. NEVER use names like "Joe's Diner", "Sushi Palace", or "Taco Loco" unless they are in the list.
3. If no restaurants are in the list, state that no matches were found.
4. Output a detailed 'summary' paragraph (3-4 sentences) that mentions the specific restaurants you picked and why they fit the user's location, cuisine, and budget.
5. Provide a JSON object with: summary (string) and restaurants (array of objects with: id, name, rating, costForTwo, address, cuisines, aiReason).

Output strictly valid JSON.
"""
    return prompt

def get_llm_recommendation(df: pd.DataFrame, preferences: dict, model: str = "llama-3.1-8b-instant") -> str:
    """
    Calls the Groq API to generate JSON-formatted recommendations.
    Stability Fix: Returns early if no data to prevent hallucinations.
    """
    if not client:
        return '{"summary": "Service unavailable.", "restaurants": []}'
        
    if df is None or df.empty:
        return '{"summary": "No restaurants found matching your current filters. Please try broadening your search!", "restaurants": []}'
        
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
