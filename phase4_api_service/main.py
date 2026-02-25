import sys
import os
import logging
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Add previous phases to sys.path to easily import the logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase2_knowledge_base'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase3_llm_integration'))

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

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

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
    # 1. Parse natural language search query if provided
    parsed_filters = {}
    if request.search_query:
        logger.info(f"Parsing search query: {request.search_query}")
        parsed_filters = parse_search_query(request.search_query)
        logger.info(f"Parsed filters: {parsed_filters}")

    # 2. Merge filters (Dropdowns and Parsed values)
    location = parsed_filters.get("location") or request.location
    cuisine = parsed_filters.get("cuisine") or request.cuisine
    
    prices = [v for v in [request.max_price, parsed_filters.get("max_price")] if v is not None]
    max_price = min(prices) if prices else None

    min_ratings = [v for v in [request.min_rating, parsed_filters.get("min_rating")] if v is not None]
    min_rating = max(min_ratings) if min_ratings else None
    
    max_ratings = [v for v in [request.max_rating, parsed_filters.get("max_rating")] if v is not None]
    max_rating = min(max_ratings) if max_ratings else None

    preferences = {
        "location": location,
        "cuisine": cuisine,
        "max_price": max_price,
        "min_rating": min_rating,
        "max_rating": max_rating
    }
    
    # 3. Retrieve the data from SQL
    try:
        matched_df = retrieve_restaurants(
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
    return {"status": "ok", "db_connected": engine is not None}

@app.get("/locations")
def get_locations():
    if not engine:
        return {"locations": []}
    try:
        with engine.connect() as conn:
            # Query distinct locations with length > 3
            res = conn.execute(text("SELECT DISTINCT location FROM restaurants WHERE length(location) > 3 ORDER BY location ASC"))
            locations = [row[0] for row in res if row[0]]
        return {"locations": locations}
    except Exception as e:
        logger.error(f"Failed to fetch locations: {e}")
        return {"locations": []}

@app.get("/cuisines")
def get_cuisines():
    if not engine:
        return {"cuisines": []}
    try:
        with engine.connect() as conn:
            # Postgres supports strings split and distinct
            # But the easiest way is to fetch the column and set-split in Python for now
            res = conn.execute(text("SELECT DISTINCT cuisines FROM restaurants WHERE cuisines IS NOT NULL"))
            all_cuisines = set()
            for row in res:
                for c in str(row[0]).split(','):
                    c_clean = c.strip()
                    if c_clean:
                        all_cuisines.add(c_clean)
        return {"cuisines": sorted(list(all_cuisines))}
    except Exception as e:
        logger.error(f"Failed to fetch cuisines: {e}")
        return {"cuisines": []}
