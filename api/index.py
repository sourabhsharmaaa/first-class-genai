from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ensure the root directory and child phase directories are in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase1_data_ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase2_knowledge_base"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase3_llm_integration"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "phase4_api_service"))

# Import the main FastAPI app and its startup events
from phase4_api_service.main import app as main_app

app = FastAPI(title="Vercel API Gateway")

# Vercel relies on the app instance directly
# We mount the imported app into this root instance to maintain exact routes
# Alternatively, we can just expose the imported app directly as the serverless handler
app.mount("/api", main_app)

# Note: Vercel standard routing maps `api/index.py` to `/api/*` based on vercel.json rewrites.
# If `vercel.json` rewrites `/api/(.*)` to `api/index.py`, then Vercel passes the request as `/api/...` to the FastAPI app.
# By mounting `main_app` to `/api`, we handle the prefix properly.

# To handle both local and Vercel environments seamlessly without mounting prefix woes:
# We mount main_app to /api so that Vercel's path injection aligns perfectly.
