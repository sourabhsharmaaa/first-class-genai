import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL not found in environment variables!")

# Persistent engine to be reused across calls (SQLAlchemy handles pooling)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine

def retrieve_restaurants(
    location: str = None, 
    cuisine: str = None, 
    max_price: float = None, 
    min_rating: float = None,
    max_rating: float = None,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Filters the Zomato dataset using a Supabase PostgreSQL query.
    Stability Fix: Performs location/cuisine filtering in SQL and numeric filtering in Python.
    """
    if not DATABASE_URL:
        return pd.DataFrame()

    try:
        engine = get_engine()
        
        # Base query - simple SQL to avoid syntax errors
        query_str = "SELECT * FROM restaurants WHERE 1=1"
        params = {}

        if location:
            query_str += " AND location ILIKE :location"
            params["location"] = f"%{location}%"

        if cuisine:
            query_str += " AND cuisines ILIKE :cuisine"
            params["cuisine"] = f"%{cuisine}%"

        # Fetch a sufficient buffer for Python-side filtering (price/rating)
        query_str += " LIMIT 500"

        with engine.connect() as conn:
            df = pd.read_sql(text(query_str), conn, params=params)
        
        if df.empty:
            return df

        # --- Stable Python-side Filtering ---
        # 1. Clean Rating (handles "4.1/5", "NEW", "-")
        if 'rate' in df.columns:
            df['rate_numeric'] = df['rate'].astype(str).str.split('/').str[0].str.strip()
            df['rate_numeric'] = pd.to_numeric(df['rate_numeric'], errors='coerce')
            
            if min_rating is not None:
                df = df[df['rate_numeric'] >= min_rating]
            if max_rating is not None:
                df = df[df['rate_numeric'] < max_rating]

        # 2. Clean Cost (handles "1,200", strings)
        if 'approx_costfor_two_people' in df.columns:
            df['cost_numeric'] = df['approx_costfor_two_people'].astype(str).str.replace(',', '', regex=False)
            df['cost_numeric'] = pd.to_numeric(df['cost_numeric'], errors='coerce')
            
            if max_price is not None:
                df = df[df['cost_numeric'] <= max_price]

        # 3. Final Cleaning & Deduplication
        df = df.drop_duplicates(subset=['name'], keep='first')
        
        # Sorting by rating
        if 'rate_numeric' in df.columns:
            df = df.sort_values(by='rate_numeric', ascending=False)
        
        # Consistent column naming for expected output
        rename_map = {
            'approx_costfor_two_people': 'approx_cost(for two people)',
            'listed_intype': 'listed_in(type)',
            'listed_incity': 'listed_in(city)'
        }
        df = df.rename(columns=rename_map)
        
        return df.head(top_n)
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return pd.DataFrame()
