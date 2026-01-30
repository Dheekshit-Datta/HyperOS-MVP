@echo off
echo ========================================
echo HyperOS - Quick Run
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please run setup.bat first or create .env with your Mistral API key
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import mistralai" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Dependencies not installed!
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting HyperOS...
echo.
echo TIP: A chat window will appear on top of your screen
echo      Type commands like: "Open Notepad and type Hello"
echo.
echo Emergency Stop: Move mouse to top-left corner
echo.

python main.py

pause
