#!/bin/bash

# aetherhub Startup Script
echo "🚀 Starting aetherhub - The AI Package Manager"
echo "=============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

echo "✅ Node.js and npm are available"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "[DISC] Installing dependencies..."
    npm install

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    mkdir uploads
    echo "✅ Created uploads directory"
fi

echo ""
echo "🌟 Starting aetherhub services..."
echo ""

# Start the backend server in the background
echo "[TOOL] Starting backend API server..."
npm start &
BACKEND_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend API server started (PID: $BACKEND_PID)"
    echo "📊 API available at: http://localhost:3001/api/v1"
else
    echo "❌ Failed to start backend server"
    exit 1
fi

# Start the frontend server
echo "🌐 Starting frontend server..."
npm run frontend &
FRONTEND_PID=$!

sleep 2

if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend server started (PID: $FRONTEND_PID)"
    echo "🌐 Frontend available at: http://localhost:8080"
else
    echo "❌ Failed to start frontend server"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 aetherhub is now running!"
echo "================================"
echo "Frontend:  http://localhost:8080"
echo "API:       http://localhost:3001/api/v1"
echo "Health:    http://localhost:3001/api/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down aetherhub services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
