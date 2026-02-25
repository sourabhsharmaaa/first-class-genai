import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase1_data_ingestion'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'phase2_knowledge_base'))

from data_ingestion import get_zomato_data
from retrieval import retrieve_restaurants
from llm_recommender import get_llm_recommendation

df = get_zomato_data()

print("="*50)
print("SCENARIO 1: Cheap Chinese Food in Indiranagar")
prefs1 = {"location": "Indiranagar", "cuisine": "Chinese", "max_price": 600}
res1 = retrieve_restaurants(df, **prefs1, top_n=3)
print(get_llm_recommendation(res1, prefs1))

print("\n" + "="*50)
print("SCENARIO 2: Highly Rated Italian anywhere in Bangalore (Testing missing location max price 1500)")
prefs2 = {"cuisine": "Italian", "max_price": 1500, "min_rating": 4.5}
res2 = retrieve_restaurants(df, **prefs2, top_n=3)
print(get_llm_recommendation(res2, prefs2))

print("\n" + "="*50)
print("SCENARIO 3: Strict Edge Case (Impossible constraints)")
prefs3 = {"location": "Mars", "cuisine": "Alien", "max_price": 50}
res3 = retrieve_restaurants(df, **prefs3, top_n=3)
print(get_llm_recommendation(res3, prefs3))
