#!/bin/bash
# start.sh - Entrypoint for Docker container

# Start the FastAPI backend in the background
echo "Starting FastAPI Backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8001 &

# Wait for backend to be ready
sleep 3

# Start the Streamlit frontend in the foreground (this keeps the container running)
echo "Starting Streamlit UI..."
API_URL=http://localhost:8001 streamlit run frontend/streamlit_app.py --server.port 8502 --server.address 0.0.0.0
