#!/bin/bash
# run.sh - Launches both FastAPI backend and Streamlit frontend

# Ensure we're in the right directory
cd /Users/SHAHID/.gemini/antigravity/scratch/advanced-financial-rag

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes on these ports to prevent port conflicts
echo "Stopping any existing processes on ports 8001 and 8502..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:8502 | xargs kill -9 2>/dev/null

# Start FastAPI backend in the background
echo "Starting FastAPI Backend..."
uvicorn app.main:app --reload --port 8001 &
BACKEND_PID=$!

# Wait for backend to spin up
sleep 3

# Start Streamlit frontend
echo "Starting Streamlit UI..."
API_URL=http://localhost:8001 streamlit run frontend/streamlit_app.py --server.port 8502

# When Streamlit is stopped (Ctrl+C), also kill the backend
kill $BACKEND_PID
