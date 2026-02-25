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

def parse_search_query(query: str, model: str = "llama-3.1-8b-instant") -> dict:
    """
    Parses a natural language search query into structured filters using Groq.
    """
    if not client or not query:
        return {}

    prompt = f"""
    Parse the following user search query for restaurant recommendations into a structured JSON object.
    Query: "{query}"

    Extract:
    1. location (string, e.g., "Indiranagar")
    2. cuisine (string, e.g., "Burger")
    3. max_price (number, e.g., 2000)
    4. min_rating (number, e.g., 4.0) - Use this if user says "above 4 stars" or "4 stars and up"
    5. max_rating (number, e.g., 4.0) - Use this if user says "under 4 stars" or "less than 4 stars"

    Rules:
    - If a field is not mentioned, return null for that field.
    - Return ONLY valid JSON.
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized query parser. You only output JSON."},
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
    Constructs a prompt containing user preferences and the retrieved restaurants.
    """
    prompt = f"You are an expert food critic and local guide. User preferences: {preferences}.\n\n"
    
    if df.empty:
        prompt += 'No matches. Output strictly JSON with key "restaurants": {"restaurants": [{"id": 1, "name": "Broaden your search", "rating": 0, "costForTwo": "N/A", "aiReason": "No exact matches found. Try changing your filters."}]}'
        return prompt
        
    prompt += "Top restaurants retrieved from our database:\n\n"
    
    for idx, row in df.iterrows():
        name = row.get('name', 'Unknown')
        rating = row.get('rate', 'N/A')
        loc = row.get('location', 'Unknown Location')
        address = row.get('address', 'Unknown Address')
        cuisines = row.get('cuisines', 'Unknown Cuisine')
        price = row.get('approx_cost(for two people)', 'Unknown Price')
        
        prompt += f"- Name: {name}, Rating: {rating}, Cost: {price}, Loc: {loc}, Address: {address}, Cuisine: {cuisines}\n"
        
    prompt += """
Based on this data, provide customized, engaging recommendations for ALL the restaurants provided above.
You MUST output strictly valid JSON. Do NOT output just one restaurant. Output a JSON object containing a global 'summary' text, followed by an array of objects for EVERY restaurant in the retrieved data. 

The 'summary' field MUST be a highly detailed, conversational paragraph (2-3 sentences) that explicitly NAMES the top restaurants being recommended. It must specifically mention the user's requested location, cuisines, and pricing, summarizing why these specific places are great choices altogether. Do NOT provide a generic summary.

Use the following format:
{
  "summary": "You're in for a treat in Basavanagudi with Mysuru Coffee Thindi and 36th Cross Coffee Mane, two fantastic spots that serve up delicious coffee at budget-friendly prices...",
  "restaurants": [
    {
      "id": 1,
      "name": "Restaurant 1",
      "rating": 4.5,
      "costForTwo": "800",
      "address": "123 Food Street, Jayanagar",
      "cuisines": "South Indian, Cafe",
      "aiReason": "A detailed, engaging 3-4 sentence explanation of why this restaurant is a great match for the user's specific location, cuisine, price, and rating preferences. Be highly specific and persuasive."
    },
    {
      "id": 2,
      "name": "Restaurant 2",
      "rating": 4.2,
      "costForTwo": "1200",
      "address": "456 Main Road, Indiranagar",
      "cuisines": "Italian, Continental",
      "aiReason": "A detailed, engaging 3-4 sentence explanation of why this restaurant is a great match for the user's specific location, cuisine, price, and rating preferences. Be highly specific and persuasive."
    }
  ]
}
Keep the output strictly as JSON.
"""
    return prompt

def get_llm_recommendation(df: pd.DataFrame, preferences: dict, model: str = "llama-3.1-8b-instant") -> str:
    """
    Calls the Groq API to generate JSON-formatted recommendations.
    """
    if not client:
        return '{"restaurants": []}'
        
    prompt = generate_recommendation_prompt(df, preferences)
    logger.info("Sending prompt to Groq API...")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful local food guide. You only respond in JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
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
