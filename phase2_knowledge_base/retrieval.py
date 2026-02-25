import sys
import os
import pandas as pd
import logging

# Add phase1 directory to sys.path to easily import get_zomato_data
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrieve_restaurants(
    df: pd.DataFrame, 
    location: str = None, 
    cuisine: str = None, 
    max_price: float = None, 
    min_rating: float = None,
    max_rating: float = None,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Filters the Zomato DataFrame based on user preferences.
    """
    filtered_df = df.copy()

    # 1. Filter by location (Strictly by physical location)
    if location:
        location_lower = location.lower()
        
        # Safe filtering handling NaN values
        loc_mask = filtered_df['location'].astype(str).str.lower().str.contains(location_lower, na=False)
        
        filtered_df = filtered_df[loc_mask]
        logger.info(f"After strict location filter '{location}': {len(filtered_df)} restaurants")

    # 2. Filter by cuisine
    if cuisine:
        cuisine_lower = cuisine.lower()
        cuisine_mask = filtered_df['cuisines'].astype(str).str.lower().str.contains(cuisine_lower, na=False)
        filtered_df = filtered_df[cuisine_mask]
        logger.info(f"After cuisine filter '{cuisine}': {len(filtered_df)} restaurants")

    # 3. Filter by max price
    if max_price is not None:
        if 'approx_cost(for two people)' in filtered_df.columns:
            price_mask = filtered_df['approx_cost(for two people)'] <= max_price
            filtered_df = filtered_df[price_mask]
            logger.info(f"After max price filter {max_price}: {len(filtered_df)} restaurants")

    # 4. Filter by minimum rating
    if min_rating is not None:
        if 'rate' in filtered_df.columns:
            rating_mask = filtered_df['rate'] >= min_rating
            filtered_df = filtered_df[rating_mask]
            logger.info(f"After min rating filter {min_rating}: {len(filtered_df)} restaurants")

    # 5. Filter by maximum rating
    if max_rating is not None:
        if 'rate' in filtered_df.columns:
            rating_mask = filtered_df['rate'] < max_rating
            filtered_df = filtered_df[rating_mask]
            logger.info(f"After max rating filter {max_rating}: {len(filtered_df)} restaurants")

    # Sort by rating (descending)
    if 'rate' in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by='rate', ascending=False, na_position='last')
        
    # Deduplicate by name to avoid repeating chain outlets or duplicate entries
    filtered_df = filtered_df.drop_duplicates(subset=['name'], keep='first')
        
    return filtered_df.head(top_n)

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
