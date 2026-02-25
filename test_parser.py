import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'phase3_llm_integration'))
from llm_recommender import parse_search_query

query = "burger in indiranagar under 500 rupees"
parsed = parse_search_query(query)
print(f"Query: {query}")
print(f"Parsed: {parsed}")
