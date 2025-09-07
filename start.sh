#!/bin/bash

# -----------------------------------------
# Activate virtual environment
# -----------------------------------------
echo "🟢 Activating Python virtual environment..."
source venv/Scripts/activate

# -----------------------------------------
# Set PYTHONPATH
# -----------------------------------------
export PYTHONPATH=./src

# -----------------------------------------
# Start FastAPI backend
# -----------------------------------------
echo "🚀 Starting FastAPI backend at http://localhost:8000 ..."
uvicorn api.main:app --reload &
BACKEND_PID=$!

# -----------------------------------------
# Start React frontend
# -----------------------------------------
echo "🌐 Starting React frontend at http://localhost:3000 ..."
cd frontend
npm start &
FRONTEND_PID=$!

# -----------------------------------------
# Auto-open browser tabs (wait a moment)
# -----------------------------------------
sleep 3
start http://localhost:3000
start http://localhost:8000/docs

# -----------------------------------------
# Gracefully shut down on Ctrl+C
# -----------------------------------------
trap "echo 🔴 Stopping servers...; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID