import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data

df = get_zomato_data()

# Check for Belgian Waffle Factory
waffles = df[df['name'].str.contains('Belgian Waffle Factory', case=False, na=False)]
print(f"Total entries for Belgian Waffle Factory: {len(waffles)}")
for idx, row in waffles.iterrows():
    print(f"--- Entry {idx} ---")
    print(f"Name: {row['name']}")
    print(f"Location: {row['location']}")
    print(f"City (listed_in): {row['listed_in(city)']}")
    print(f"Cuisines: {row['cuisines']}")
    print(f"Rate: {row['rate']}")
    print(f"Address: {row['address']}")

# Also check for ALL Burger places in Indiranagar specifically
indira_burgers = df[
    (df['location'].astype(str).str.lower().str.contains('indiranagar', na=False)) &
    (df['cuisines'].astype(str).str.lower().str.contains('burger', na=False))
]
print(f"\nTotal Burgers in Indiranagar: {len(indira_burgers)}")
print(indira_burgers[['name', 'rate', 'location']].head(10))
