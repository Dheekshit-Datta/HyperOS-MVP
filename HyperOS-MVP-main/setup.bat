@echo off
echo ========================================
echo HyperOS Setup Script
echo ========================================
echo.

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Checking for Tesseract OCR...
where tesseract >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Tesseract OCR not found!
    echo Please download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
) else (
    echo Tesseract OCR found!
)

echo.
echo [3/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please edit it with your Mistral API key
) else (
    echo .env file already exists
)

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Get your Mistral API key from: https://console.mistral.ai/
echo 2. Edit .env file and add your API key
echo 3. Run: python main.py
echo.
echo ========================================
pause
