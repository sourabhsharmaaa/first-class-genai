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

    prompt = f"""
    Parse the user's Bangalore restaurant search query into a structured JSON object.
    Query: "{query}"

    Extract:
    1. location (Specific Bangalore neighborhood/area. E.g., "Indiranagar", "Koramangala", "BTM", "Electronic City", "Church Street", "HSR")
    2. cuisine (E.g., "Japanese", "Pizza", "North Indian")
    3. max_price (Integer number)
    4. min_rating (Float number)

    CRITICAL RULES:
    - ONLY extract specific Bangalore neighborhoods for 'location'. 
    - NEVER extract the country "Japan" as a location.
    - NEVER extract the city "Bangalore" as a location.
    - IMPORTANT: Some neighborhood names contain the word "City" (e.g., "Electronic City") or "Street" (e.g., "Church Street"). You MUST extract these as locations.
    - If a neighborhood is mentioned alongside a cuisine (e.g., "Japanese in Electronic City"), extract BOTH.
    - Return ONLY valid JSON.
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized query parser for Bangalore restaurants. You output JSON only."},
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
    Restores high-quality, detailed prompts for persuasive recommendations.
    """
    if df.empty:
        return '{"summary": "No exact matches found. Try broadening your criteria.", "restaurants": []}'
        
    prompt = f"You are an expert food guide. Recommend these SPECIFIC restaurants for preferences: {preferences}.\n\n"
    prompt += "RESTAURANTS FROM DATABASE:\n"
    
    for _, row in df.iterrows():
        # Clean price string for the prompt
        price = str(row.get('approx_cost(for two people)', 'N/A')).replace('.0', '')
        prompt += f"- Name: {row.get('name')}, Rating: {row.get('rate')}, Cost: ₹{price}, Location: {row.get('location')}, Cuisines: {row.get('cuisines')}, Address: {row.get('address')}\n"
        
    prompt += """
Based on the data above, provide customized, engaging recommendations. 
CRITICAL QUALITY RULES:
1. You MUST ONLY use the real names and data provided above. NEVER hallucinate names like "Joe's Diner".
2. The 'summary' field MUST be a detailed, conversational 3-4 sentence paragraph naming the top spots and why they fit the user's specific request.
3. For EVERY restaurant, the 'aiReason' MUST be a persuasive 3-4 sentence explanation. Do NOT just say "High rating". Explain why this specific place is a great match.
4. Preserve the 'cuisines' formatting exactly as shown (e.g. "Pizza, Italian, Cafe" with spaces and commas).

Output strictly valid JSON:
{
  "summary": "Full detailed paragraph...",
  "restaurants": [
    {
      "id": 1,
      "name": "Exact Name",
      "rating": 4.5,
      "costForTwo": "600",
      "address": "Full Address",
      "cuisines": "Cuisine 1, Cuisine 2 (KEEP SPACES)",
      "aiReason": "A detailed 3-4 sentence persuasive explanation..."
    }
  ]
}
"""
    return prompt

def get_llm_recommendation(df: pd.DataFrame, preferences: dict, model: str = "llama-3.1-8b-instant") -> str:
    """
    Calls the Groq API to generate JSON-formatted recommendations.
    Restored high token limit for quality.
    """
    if not client:
        return '{"summary": "Service unavailable.", "restaurants": []}'
        
    if df is None or df.empty:
        return '{"summary": "No restaurants found matching your filters. Try broadening your search!", "restaurants": []}'
        
    prompt = generate_recommendation_prompt(df, preferences)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful local food guide. You only respond in JSON."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1024, # Restored for detailed content
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
