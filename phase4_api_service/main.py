import sys
import os
import logging
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add previous phases to sys.path to easily import the logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase1_data_ingestion'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase2_knowledge_base'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase3_llm_integration'))

from data_ingestion import get_zomato_data
from retrieval import retrieve_restaurants
from llm_recommender import get_llm_recommendation, parse_search_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Restaurant Recommendation API", version="1.0")

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global DataFrame to hold our data in memory
df = None

def get_data():
    global df
    if df is not None:
        return df
    logger.info("Loading Zomato dataset into memory...")
    try:
        df = get_zomato_data()
        logger.info(f"Dataset loaded successfully with {len(df)} rows.")
        return df
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dataset.")

@app.on_event("startup")
def startup_event():
    get_data()

class RecommendationRequest(BaseModel):
    search_query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    top_n: Optional[int] = 5

class RecommendationResponse(BaseModel):
    query: RecommendationRequest
    restaurant_count: int
    recommendation_text: str
    parsed_filters: Optional[dict] = None

@app.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(request: RecommendationRequest):
    df = get_data()
        
    # 1. Parse natural language search query if provided
    parsed_filters = {}
    if request.search_query:
        logger.info(f"Parsing search query: {request.search_query}")
        parsed_filters = parse_search_query(request.search_query)
        logger.info(f"Parsed filters: {parsed_filters}")

    # 2. Merge filters (Dropdowns and Parsed values)
    # Strategy: Take the most restrictive value if both are present.
    location = request.location or parsed_filters.get("location")
    cuisine = request.cuisine or parsed_filters.get("cuisine")
    
    # For price: take the MINIMUM (more restrictive)
    prices = [v for v in [request.max_price, parsed_filters.get("max_price")] if v is not None]
    max_price = min(prices) if prices else None

    # For rating: 
    # min_rating: take the MAXIMUM (more restrictive)
    min_ratings = [v for v in [request.min_rating, parsed_filters.get("min_rating")] if v is not None]
    min_rating = max(min_ratings) if min_ratings else None
    
    # max_rating: take the MINIMUM (more restrictive)
    max_ratings = [v for v in [request.max_rating, parsed_filters.get("max_rating")] if v is not None]
    max_rating = min(max_ratings) if max_ratings else None

    preferences = {
        "location": location,
        "cuisine": cuisine,
        "max_price": max_price,
        "min_rating": min_rating,
        "max_rating": max_rating
    }
    
    # 3. Retrieve the data
    try:
        matched_df = retrieve_restaurants(
            df=df,
            location=location,
            cuisine=cuisine,
            max_price=max_price,
            min_rating=min_rating,
            max_rating=max_rating,
            top_n=request.top_n
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in data retrieval: {str(e)}")
        
    # 4. Extract LLM Recommendation
    try:
        llm_response = get_llm_recommendation(matched_df, preferences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in LLM generation: {str(e)}")
        
    return RecommendationResponse(
        query=request,
        restaurant_count=len(matched_df),
        recommendation_text=llm_response,
        parsed_filters=parsed_filters
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "dataset_loaded": df is not None}

@app.get("/locations")
def get_locations():
    df = get_data()
    # Extract unique locations, filter out acronyms (length <= 3) as requested
    locations = sorted([str(loc).strip() for loc in df['location'].dropna().unique() if len(str(loc).strip()) > 3])
    return {"locations": locations}

@app.get("/cuisines")
def get_cuisines():
    df = get_data()
    
    all_cuisines = set()
    for c_str in df['cuisines'].dropna():
        for c in str(c_str).split(','):
            c_clean = c.strip()
            if c_clean:
                all_cuisines.add(c_clean)
                
    return {"cuisines": sorted(list(all_cuisines))}
