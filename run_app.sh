#!/bin/bash

# Disable Streamlit telemetry and email prompt
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true

echo "Starting AI Restaurant Recommender Backend..."
source phase1_data_ingestion/venv/bin/activate
uvicorn phase4_api_service.main:app --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to initialize dataset (approx 15 seconds)..."
sleep 15

echo "Starting Next.js Frontend User Interface..."
npm run dev &
FRONTEND_PID=$!

echo "Both servers are running!"
echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C to kill both background processes
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

# Wait for process termination
wait $FRONTEND_PID $BACKEND_PID
