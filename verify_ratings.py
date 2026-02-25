import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data

df = get_zomato_data()
df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

# Filter
filtered = df.copy()
filtered = filtered[filtered['location'].astype(str).str.lower().str.contains('banashankari', na=False)]
filtered = filtered[filtered['cuisines'].astype(str).str.lower().str.contains('cafe', na=False)]
filtered = filtered[filtered['approx_cost(for two people)'] <= 1000]
filtered = filtered[filtered['rate'] >= 4.0]

filtered = filtered.sort_values(by='rate', ascending=False).head(10)

print("--- Check Database Match ---")
for _, row in filtered.iterrows():
    print(f"Name: {row['name']} | Rating: {row['rate']} | Location: {row['location']} | Cost: {row['approx_cost(for two people)']}")
