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

# Vercel handles requests to /api/index.py as the entry point for /api/*.
# We expose main_app directly as 'app' so Vercel can find it.
app = main_app

# Note: We no longer need to mount to /api because main_app defines routes
# like /locations, and Vercel passes the path after /api/ to the function.
# E.g. /api/locations -> main_app receives /locations
