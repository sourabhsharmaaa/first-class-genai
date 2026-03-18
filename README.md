# Zomato Cravings Finder

An LLM-powered AI Restaurant Recommendation Service built for Bangalore food lovers. It understands your cravings in plain English and returns personalized dining suggestions — grounded in real Zomato data, not guesswork.

## 🧐 What is this project?

This project is an **AI-driven Restaurant Discovery Engine** that specializes in Bangalore's dining scene. Unlike generic search, this system understands natural language queries like *"find me a cozy Italian place in Indiranagar under ₹800"* and instantly returns curated restaurant recommendations with ratings, pricing, and cuisine details — all backed by real data from the [Zomato Restaurant Recommendation Dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) on Hugging Face.

## 🎯 Why we made this?

Searching for the right restaurant in a city as diverse as Bangalore is overwhelming. Existing tools force you to click through endless filters. We built this to:

1. **Make It Conversational**: Ask in plain English — the AI figures out the filters for you.
2. **Stay Grounded in Real Data**: Every recommendation comes from the actual Zomato dataset, not AI hallucinations.
3. **Combine Smart + Manual Control**: Mix natural language queries with dropdown filters for precision results.

## 🛠️ How it works & What we used

We use a **multi-phase pipeline** that connects a real dataset, a structured database, an LLM query parser, and a modern frontend.

### 1. The Data Pipeline (Ingestion & Storage)
- **Data Source**: The Zomato Restaurant Recommendation Dataset pulled directly from Hugging Face using the `datasets` library.
- **Cleaning**: Price normalization (handles `"1,200"` strings), rating parsing (handles `"4.1/5"`, `"NEW"`, `"-"`), and cuisine standardization.
- **Storage**: Cleaned data is uploaded to **Supabase (PostgreSQL)** for fast, structured querying at scale.

### 2. The Knowledge Base (Retrieval Layer)
- **SQL Filtering**: Location and cuisine filters run as native SQL `ILIKE` queries against the Supabase database.
- **Python-Side Filtering**: Price and rating filters are applied in-memory using Pandas for stability with messy string data.
- **Deduplication & Ranking**: Results are deduplicated by restaurant name and sorted by rating before being returned.

### 3. The Intelligence Layer (LLM & Groq)
- **Query Parsing**: Natural language queries are sent to **Groq** (`llama-3.1-8b-instant`) to extract structured filters — location, cuisine, max price, and min rating — as a JSON object.
- **Anti-Hallucination Guard**: Parsed locations are validated against all known Bangalore neighborhoods in the database. Unrecognized locations are silently discarded to prevent bad results.
- **Recommendation Engine**: The matched restaurant data is passed back to the LLM to synthesize a concise, human-readable recommendation response.

### 4. The API Service (FastAPI)
- Exposes a clean `/recommend` POST endpoint that accepts both free-text queries and dropdown filter values simultaneously.
- Filter merging logic: dropdown filters **take precedence** when both are provided (e.g., dropdown price cap wins over LLM-parsed price cap).
- Additional utility endpoints: `/locations`, `/cuisines`, and `/health`.

### 5. The UI (Next.js)
- Built with **Next.js 16**, **TypeScript**, and **Tailwind CSS**.
- Supports a free-text search bar + independent filter dropdowns for Location, Cuisine, Price, and Rating.
- Dropdowns clear the text input when changed to avoid conflicting filters and ensure clean, predictable results.

## ✨ Key Features

- **🗣️ Natural Language Search**: Type your craving in plain English — the AI parses location, cuisine, price, and rating automatically.
- **🛡️ Anti-Hallucination Guard**: Parsed locations are cross-validated against real Bangalore neighborhoods in the database. Made-up locations are rejected.
- **🎛️ Hybrid Filter Mode**: Combine free-text queries with manual dropdown filters — both signals are intelligently merged.
- **📊 Real Data, Real Restaurants**: Every result is sourced from the actual Zomato dataset — no fabricated restaurants.
- **⚡ Fast Inference**: Powered by Groq's `llama-3.1-8b-instant` for near-instant query parsing and recommendation generation.
- **🔄 Smart Deduplication**: Results are deduplicated and ranked by rating before being surfaced to the user.

## 🏗️ Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), Uvicorn
- **Database**: Supabase (PostgreSQL) via SQLAlchemy
- **Data Processing**: Pandas, NumPy
- **LLM Provider**: Groq (`llama-3.1-8b-instant`)
- **Data Source**: Hugging Face Datasets (`ManikaSaini/zomato-restaurant-recommendation`)

## 📁 Project Structure

- `/phase1_data_ingestion`: Downloads the Zomato dataset from Hugging Face, cleans it, and uploads it to Supabase.
- `/phase2_knowledge_base`: SQL + Python retrieval layer with rating/price filtering and deduplication.
- `/phase3_llm_integration`: Groq-powered NL query parser and LLM recommendation generator.
- `/phase4_api_service`: FastAPI service exposing `/recommend`, `/locations`, `/cuisines`, and `/health` endpoints.
- `/src`: Next.js frontend application with search UI and filter dropdowns.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js & npm
- Groq API Key
- Supabase project with a `restaurants` table

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root:
```bash
GROQ_API_KEY="your-groq-api-key"
DATABASE_URL="postgresql://user:password@host:port/dbname"
```

### 3. Seed the Database
```bash
python phase1_data_ingestion/upload_to_supabase.py
```

### 4. Run the Backend API
```bash
uvicorn phase4_api_service.main:app --reload
```
Runs on `http://localhost:8000`. Swagger docs available at `http://localhost:8000/docs`.

### 5. Run the Frontend UI
```bash
npm install
npm run dev
```
Access the UI at `http://localhost:3000`.

### 6. Run Tests
```bash
# Backend tests
python -m pytest phase1_data_ingestion/ phase2_knowledge_base/ phase3_llm_integration/ phase4_api_service/

# Frontend tests
npm run test
```
