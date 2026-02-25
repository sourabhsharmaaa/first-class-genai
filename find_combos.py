import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.getcwd(), 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data
import warnings
warnings.filterwarnings('ignore')

df = get_zomato_data()

# Clean up
df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

# Filter out rows with no location or cuisines
df = df.dropna(subset=['location', 'cuisines'])

counts = df.groupby(['location', 'cuisines']).size().reset_index(name='count')

exactly_3 = counts[counts['count'] == 3].head(5)
print("Combos with exactly 3 restaurants:")
for _, row in exactly_3.iterrows():
    print(f"Location: {row['location']}, Cuisine: {row['cuisines']}")

at_least_6 = counts[counts['count'] >= 6].head(5)
print("\nCombos with at least 6 restaurants:")
for _, row in at_least_6.iterrows():
    print(f"Location: {row['location']}, Cuisine: {row['cuisines']}")
