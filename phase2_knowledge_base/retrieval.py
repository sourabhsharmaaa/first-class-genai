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
    """
    if not DATABASE_URL:
        return pd.DataFrame()

    engine = create_engine(DATABASE_URL)
    
    # Base query
    query_str = "SELECT * FROM restaurants WHERE 1=1"
    params = {}

    if location:
        query_str += " AND location ILIKE :location"
        params["location"] = f"%{location}%"

    if cuisine:
        query_str += " AND cuisines ILIKE :cuisine"
        params["cuisine"] = f"%{cuisine}%"

    if max_price is not None:
        query_str += " AND approx_costfor_two_people <= :max_price"
        params["max_price"] = max_price

    if min_rating is not None:
        query_str += " AND rate >= :min_rating"
        params["min_rating"] = min_rating

    if max_rating is not None:
        query_str += " AND rate < :max_rating"
        params["max_rating"] = max_rating

    # Sorting and Limit
    query_str += " ORDER BY rate DESC NULLS LAST LIMIT :limit"
    params["limit"] = top_n * 2 # Get more to deduplicate

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query_str), conn, params=params)
        
        # Deduplicate results locally by name (SQL DISTINCT is hard on name vs other columns)
        df = df.drop_duplicates(subset=['name'], keep='first')
        
        # Consistent column naming for expected output
        # (The uploader script converted them to lower_snake_case)
        rename_map = {
            'approx_costfor_two_people': 'approx_cost(for two people)',
            'listed_intype': 'listed_in(type)',
            'listed_incity': 'listed_in(city)'
        }
        df = df.rename(columns=rename_map)
        
        return df.head(top_n)
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame()

if __name__ == "__main__":
    logger.info("Loading data to test retrieval...")
    data = get_zomato_data()
    
    # Test specific retrieval
    test_loc = "BTM"
    test_cuisine = "North Indian"
    test_price = 800
    test_rating = 4.0
    
    logger.info(f"Searching for: Location={test_loc}, Cuisine={test_cuisine}, Max Price={test_price}, Min Rating={test_rating}")
    results = retrieve_restaurants(
        df=data,
        location=test_loc,
        cuisine=test_cuisine,
        max_price=test_price,
        min_rating=test_rating,
        top_n=3
    )
    
    if not results.empty:
        print("\nTop Matches found:")
        for idx, row in results.iterrows():
            print(f"- {row['name']} ({row['rate']}⭐) | {row['location']} | {row['cuisines']} | ₹{row['approx_cost(for two people)']}")
    else:
        print("\nNo matching restaurants found.")
