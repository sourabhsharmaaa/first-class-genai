import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.getcwd(), 'phase1_data_ingestion'))
from data_ingestion import get_zomato_data
import warnings
warnings.filterwarnings('ignore')

df = get_zomato_data()
df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

# Filter for single cuisines
df = df[df['cuisines'].astype(str).str.contains(',') == False]
df = df.dropna(subset=['location', 'cuisines'])

# Filter out acronyms
df = df[~df['location'].str.contains('BTM', case=False, na=False)]
df = df[~df['location'].str.contains('HSR', case=False, na=False)]
df = df[~df['location'].str.contains('JP Nagar', case=False, na=False)]

counts = df.groupby(['location', 'cuisines']).size().reset_index(name='count')

ex3 = counts[counts['count'] == 3].head(5)
at6 = counts[counts['count'] >= 6].head(5)

print("--- Exact 3 ---")
print(ex3)
print("--- At least 6 ---")
print(at6)
