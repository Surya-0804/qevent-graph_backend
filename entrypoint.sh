#!/bin/bash

# Exit on error
set -e

echo "Starting Event-Graph Quantum Backend..."

# Use PORT environment variable if set (Railway/Render), otherwise default to 8000
PORT=${PORT:-8000}

# Start uvicorn server
# Bind to 0.0.0.0 to accept external connections
# Use environment variable for port (required by Railway/Render)
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info
