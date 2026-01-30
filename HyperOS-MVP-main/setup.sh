#!/bin/bash

echo "========================================"
echo "HyperOS Setup Script"
echo "========================================"
echo ""

echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "[2/4] Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "Tesseract OCR found!"
else
    echo "WARNING: Tesseract OCR not found!"
    echo "Install with:"
    echo "  Mac: brew install tesseract"
    echo "  Linux: sudo apt-get install tesseract-ocr"
    echo ""
fi

echo ""
echo "[3/4] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please edit it with your Mistral API key"
else
    echo ".env file already exists"
fi

echo ""
echo "[4/4] Setup complete!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Get your Mistral API key from: https://console.mistral.ai/"
echo "2. Edit .env file and add your API key"
echo "3. Run: python main.py"
echo ""
echo "========================================"
