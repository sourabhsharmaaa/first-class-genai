import sys
import os

# Add previous phases to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'phase1_data_ingestion'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'phase2_knowledge_base'))

from data_ingestion import get_zomato_data
from retrieval import retrieve_restaurants

df = get_zomato_data()

print("\n=== YOUR COMBO ===")
print("Location: Bellandur, Cuisine: American, Max Price: 1000, Min Rating: 4.0")
df1 = retrieve_restaurants(df, location="Bellandur", cuisine="American", max_price=1000.0, min_rating=4.0, top_n=10)
if df1 is not None and not df1.empty:
    print(df1[['name', 'rate', 'cuisines', 'approx_cost(for two people)']])
else:
    print("No results found for this combo.")

print("\n=== FINDING A COMBO WITH 5+ RESTAURANTS ===")
# Let's try Indiranagar + Cafe
df2 = retrieve_restaurants(df, location="Indiranagar", cuisine="Cafe", max_price=2000.0, min_rating=4.0, top_n=10)
if df2 is not None and not df2.empty:
    print("\nCombo: Indiranagar, Cafe, Max Price: 2000, Min Rating: 4.0")
    print(df2[['name', 'rate', 'cuisines', 'approx_cost(for two people)']].head(10))
else:
    print("Indiranagar Cafe didn't yield enough.")

# Let's try Koramangala 5th Block + Continental
df3 = retrieve_restaurants(df, location="Koramangala 5th Block", cuisine="Continental", max_price=2000.0, min_rating=4.0, top_n=10)
if df3 is not None and not df3.empty:
    print("\nCombo: Koramangala 5th Block, Continental, Max Price: 2000, Min Rating: 4.0")
    print(df3[['name', 'rate', 'cuisines', 'approx_cost(for two people)']].head(10))

# Try Jayanagar + North Indian
df4 = retrieve_restaurants(df, location="Jayanagar", cuisine="North Indian", max_price=1000.0, min_rating=4.0, top_n=10)
if df4 is not None and not df4.empty:
    print("\nCombo: Jayanagar, North Indian, Max Price: 1000, Min Rating: 4.0")
    print(df4[['name', 'rate', 'cuisines', 'approx_cost(for two people)']].head(10))
