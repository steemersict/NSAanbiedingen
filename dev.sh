#!/bin/bash
# NSAanbiedingen Development Script
# Start both frontend and backend for browser-based development

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting NSAanbiedingen in dev mode...${NC}"

# Kill any existing processes
pkill -f "python.*server.py" 2>/dev/null || true
pkill -f "astro dev" 2>/dev/null || true

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd backend/src
python3 server.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start and capture port
sleep 2
PORT=$(ps aux | grep -o "SERVER_PORT=[0-9]*" | head -1 | cut -d= -f2)

if [ -z "$PORT" ]; then
    echo "Error: Backend failed to start"
    exit 1
fi

echo -e "${GREEN}Backend running on port ${PORT}${NC}"

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NSAanbiedingen is ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Frontend: ${BLUE}http://localhost:4321/?port=${PORT}${NC}"
echo -e "Backend:  ${BLUE}http://127.0.0.1:${PORT}${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"

# Handle shutdown
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
