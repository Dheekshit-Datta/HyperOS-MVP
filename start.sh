#!/bin/bash

# ============================================
#  HyperOS MVP - Linux/macOS Startup Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           HYPEROS DESKTOP AI AGENT            ║${NC}"
echo -e "${BLUE}║          Vision-Enabled Automation            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down HyperOS...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    echo "Goodbye!"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM EXIT

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed${NC}"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}[OK]${NC} Python $PYTHON_VERSION found"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi
NODE_VERSION=$(node --version 2>&1)
echo -e "${GREEN}[OK]${NC} Node.js $NODE_VERSION found"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}[ERROR] npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} npm found"

# Setup Python virtual environment
echo ""
echo -e "${BLUE}[1/5]${NC} Setting up Python environment..."
if [ ! -d "agent-core/venv" ]; then
    echo "      Creating virtual environment..."
    cd agent-core
    python3 -m venv venv
    
    echo "      Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install Python dependencies${NC}"
        exit 1
    fi
    cd ..
    echo -e "${GREEN}[OK]${NC} Python environment ready"
else
    echo -e "${GREEN}[OK]${NC} Python environment already exists"
fi

# Check for .env file
echo ""
echo -e "${BLUE}[2/5]${NC} Checking configuration..."
if [ ! -f "agent-core/.env" ]; then
    if [ -f "agent-core/.env.example" ]; then
        cp agent-core/.env.example agent-core/.env
        echo -e "${YELLOW}[WARN]${NC} Created .env from .env.example"
        echo "       Please edit agent-core/.env and add your GEMINI_API_KEY"
        echo ""
        echo "       Get your API key at: https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Press Enter to continue after adding your API key..."
    else
        echo -e "${RED}[ERROR]${NC} No .env file found in agent-core/"
        exit 1
    fi
else
    echo -e "${GREEN}[OK]${NC} Configuration file exists"
fi

# Install npm dependencies
echo ""
echo -e "${BLUE}[3/5]${NC} Setting up Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    echo "      Installing npm packages (this may take a minute)..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install npm dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Node.js dependencies installed"
else
    echo -e "${GREEN}[OK]${NC} Node.js dependencies already installed"
fi

# Start the backend server
echo ""
echo -e "${BLUE}[4/5]${NC} Starting Python backend..."
cd agent-core
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to initialize
echo "      Waiting for backend to start..."
sleep 3

# Verify backend is running
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Backend is running on port 8000"
else
    echo -e "${YELLOW}[WARN]${NC} Backend may still be starting..."
    sleep 2
fi

# Start the frontend
echo ""
echo -e "${BLUE}[5/5]${NC} Starting Electron frontend..."
echo ""
echo "  ┌─────────────────────────────────────────────────┐"
echo "  │  HyperOS is starting!                           │"
echo "  │                                                 │"
echo "  │  Global Hotkey: Ctrl+Space  (toggle overlay)   │"
echo "  │  Backend API:   http://127.0.0.1:8000          │"
echo "  │                                                 │"
echo "  │  Press Ctrl+C to stop all services             │"
echo "  └─────────────────────────────────────────────────┘"
echo ""

# Run the dev server (blocking)
npm run dev

# Cleanup handled by trap
