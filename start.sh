#!/bin/bash
# start.sh - Entrypoint for Docker container

# Start the FastAPI backend in the foreground
echo "Starting FastAPI Backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8001
