import sys
import os
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Add previous phases to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'phase2_knowledge_base'))
sys.path.append(os.path.join(BASE_DIR, 'phase3_llm_integration'))

try:
    from retrieval import retrieve_restaurants
    from llm_recommender import get_llm_recommendation, parse_search_query
except ImportError as e:
    logging.error(f"Import Error: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Restaurant Recommendation API", version="1.0")

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
    error: Optional[str] = None

@app.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(request: RecommendationRequest):
    parsed_filters = {}
    error_msg = None
    matched_df = pd.DataFrame()
    llm_response = '{"restaurants": []}'
    
    try:
        # 1. Parse natural language search query
        if request.search_query:
            try:
                parsed_filters = parse_search_query(request.search_query)
            except Exception as e:
                logger.error(f"Query parsing error: {e}")

        # 2. Merge filters (Dropdowns and Parsed values)
        location = parsed_filters.get("location") or request.location
        cuisine = parsed_filters.get("cuisine") or request.cuisine
        
        pricesResource = [v for v in [request.max_price, parsed_filters.get("max_price")] if v is not None]
        max_price = min(pricesResource) if pricesResource else None

        min_ratingsResource = [v for v in [request.min_rating, parsed_filters.get("min_rating")] if v is not None]
        min_rating = max(min_ratingsResource) if min_ratingsResource else None

        # 3. Retrieve the data
        try:
            matched_df = retrieve_restaurants(
                location=location,
                cuisine=cuisine,
                max_price=max_price,
                min_rating=min_rating,
                top_n=request.top_n or 5
            )
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            error_msg = str(e)
            
        # 4. Get LLM Recommendation
        try:
            llm_response = get_llm_recommendation(matched_df, {
                "location": location, 
                "cuisine": cuisine,
                "max_price": max_price,
                "min_rating": min_rating
            })
        except Exception as e:
            logger.error(f"LLM error: {e}")
            
    except Exception as e:
        logger.error(f"General recommendation error: {e}")
        error_msg = str(e)

    return RecommendationResponse(
        query=request,
        restaurant_count=len(matched_df),
        recommendation_text=llm_response,
        parsed_filters=parsed_filters,
        error=error_msg
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "db": DATABASE_URL is not None}

@app.get("/locations")
def get_locations():
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT DISTINCT location FROM restaurants WHERE location IS NOT NULL ORDER BY location ASC LIMIT 100"))
            return {"locations": [row[0] for row in res]}
    except Exception as e:
        return {"locations": [], "error": str(e)}

@app.get("/cuisines")
def get_cuisines():
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT DISTINCT cuisines FROM restaurants WHERE cuisines IS NOT NULL LIMIT 100"))
            c = set()
            for row in res:
                for x in str(row[0]).split(','):
                    if x.strip(): c.add(x.strip())
            return {"cuisines": sorted(list(c))}
    except Exception as e:
        return {"cuisines": [], "error": str(e)}
