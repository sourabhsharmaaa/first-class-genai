import pandas as pd
from sqlalchemy import create_engine
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# The user provided: postgresql://postgres:ilovesomeone@123@db.mqlpkebsecuxrjfdfmdf.supabase.co:5432/postgres
# The password "ilovesomeone@123" contains an @ which must be encoded.

DATABASE_URL = "postgresql://postgres:ilovesomeone%40123@db.mqlpkebsecuxrjfdfmdf.supabase.co:5432/postgres"

def upload_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'zomato_cleaned.csv')
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure column names are compatible with SQL (no spaces, special chars)
    df.columns = [c.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').lower() for c in df.columns]

    print(f"Connecting to Supabase...")
    engine = create_engine(DATABASE_URL)
    
    print(f"Uploading {len(df)} rows to table 'restaurants' (this may take a few minutes)...")
    try:
        df.to_sql('restaurants', engine, if_exists='replace', index=False, chunksize=500)
        print("Successfully uploaded all data to Supabase!")
    except Exception as e:
        print(f"Error during upload: {e}")

if __name__ == "__main__":
    upload_data()
