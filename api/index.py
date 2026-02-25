from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Set HF_HOME environment variable to use /tmp because Vercel Serverless filesystem is read-only
os.environ["HF_HOME"] = "/tmp/huggingface"

# Ensure the root directory and child phase directories are in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase1_data_ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase2_knowledge_base"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase3_llm_integration"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase4_api_service"))

# Import the main FastAPI app
from phase4_api_service.main import app as main_app

# Create a wrapper app to handle the /api prefix from Vercel
app = FastAPI()

# Mount the main logic under /api to match Vercel's routing
app.mount("/api", main_app)

# Fallback for /api itself
@app.get("/api")
def api_root():
    return {"message": "AI Recommender API is running"}
