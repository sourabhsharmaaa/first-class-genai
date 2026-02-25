import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data

df = get_zomato_data()

# Check for Belgian Waffle Factory
waffles = df[df['name'].str.contains('Belgian Waffle Factory', case=False, na=False)]
print(f"Total entries for Belgian Waffle Factory: {len(waffles)}")
print(waffles[['name', 'location', 'cuisines', 'rate', 'approx_cost(for two people)']].head(10))

# Check for Indiranagar entries
indira_burgers = df[
    (df['location'].astype(str).str.lower().str.contains('indiranagar', na=False)) &
    (df['cuisines'].astype(str).str.lower().str.contains('burger', na=False))
]
print(f"\nBurgers in Indiranagar entries: {len(indira_burgers)}")
print(indira_burgers[['name', 'location', 'cuisines', 'rate']].head(10))
