#!/bin/bash

echo "🚀 Starting Indian Stock Predictor AI..."
echo "========================================"
echo ""

# Check if backend dependencies are installed
if [ ! -d "stock-ai/backend/venv" ]; then
    echo "📦 Setting up backend virtual environment..."
    cd stock-ai/backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
else
    echo "✅ Backend virtual environment exists"
fi

# Check if frontend dependencies are installed
if [ ! -d "stock-ai/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd stock-ai/frontend
    npm install
    cd ../..
else
    echo "✅ Frontend dependencies installed"
fi

echo ""
echo "🎯 Starting services..."
echo ""

# Start backend in background
echo "🔧 Starting Backend (FastAPI) on http://localhost:8000"
cd stock-ai/backend
source venv/bin/activate
python3 main.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend (React) on http://localhost:5173"
cd stock-ai/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "========================================"
echo "✨ Application started successfully!"
echo "========================================"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ All services stopped'; exit 0" INT

wait
