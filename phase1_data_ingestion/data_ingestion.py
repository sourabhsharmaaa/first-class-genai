import pandas as pd
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_zomato_data(dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation") -> pd.DataFrame:
    """
    Downloads the Zomato dataset from huggingface and returns a cleaned pandas DataFrame.
    """
    logger.info(f"Loading dataset {dataset_name} from Hugging Face...")
    try:
        # Some datasets don't have 'train', they might have 'train' or only 'default'
        # To be safe, load dataset and take the first split.
        # Use /tmp for cache dir because Vercel is read-only elsewhere
        dataset = load_dataset(dataset_name, cache_dir="/tmp/huggingface")
        # Getting the first split available
        split_name = list(dataset.keys())[0]
        df = dataset[split_name].to_pandas()
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise
        
    logger.info(f"Dataset loaded with {len(df)} rows and {len(df.columns)} columns.")
    
    # Basic data cleaning
    
    # 1. Drop duplicates based on name and address to remove duplicate restaurants
    initial_len = len(df)
    if 'name' in df.columns and 'address' in df.columns:
        df = df.drop_duplicates(subset=['name', 'address'], keep='first')
        logger.info(f"Dropped {initial_len - len(df)} duplicate restaurants.")
    else:
        df = df.drop_duplicates()
        logger.info(f"Dropped {initial_len - len(df)} duplicate rows.")
    
    # 2. Clean 'approx_cost(for two people)' (e.g. "1,500" -> 1500)
    if 'approx_cost(for two people)' in df.columns:
        df['approx_cost(for two people)'] = df['approx_cost(for two people)'].astype(str).str.replace(',', '', regex=False)
        df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'], errors='coerce')
        
    # 3. Clean 'rate' (e.g. "4.1/5" -> 4.1, "NEW" -> NaN)
    if 'rate' in df.columns:
        df['rate'] = df['rate'].astype(str).str.split('/').str[0].str.strip()
        df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
        
    # 4. Clean 'cuisines' (e.g. normalize spaces around commas)
    if 'cuisines' in df.columns:
        df['cuisines'] = df['cuisines'].astype(str).apply(
            lambda x: ', '.join([c.strip() for c in x.split(',')]) if x.lower() != 'nan' else ''
        )
        
    # 5. Normalize other text columns
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            
    return df

if __name__ == "__main__":
    df = get_zomato_data()
    print("Columns:", df.columns.tolist())
    print(df.head())
