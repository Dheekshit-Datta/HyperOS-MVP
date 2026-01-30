#!/bin/bash

echo "========================================"
echo "HyperOS - Quick Run"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please run setup.sh first or create .env with your Mistral API key"
    echo ""
    exit 1
fi

# Check if dependencies are installed
python3 -c "import mistralai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Dependencies not installed!"
    echo "Please run: pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "Starting HyperOS..."
echo ""
echo "TIP: A chat window will appear on top of your screen"
echo "     Type commands like: 'Open Notepad and type Hello'"
echo ""
echo "Emergency Stop: Move mouse to top-left corner"
echo ""

python3 main.py
