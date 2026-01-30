@echo off
setlocal enabledelayedexpansion

:: ============================================
::  HyperOS MVP - Windows Startup Script
:: ============================================

echo.
echo  ╔═══════════════════════════════════════════════╗
echo  ║           HYPEROS DESKTOP AI AGENT            ║
echo  ║          Vision-Enabled Automation            ║
echo  ╚═══════════════════════════════════════════════╝
echo.

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

:: Check for Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

:: Check Node version
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found

:: Check for npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)
echo [OK] npm found

:: Kill any existing processes
echo.
echo [1/5] Cleaning up existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq HyperOS*" >nul 2>&1
taskkill /F /IM electron.exe >nul 2>&1

:: Setup Python virtual environment
echo.
echo [2/5] Setting up Python environment...
if not exist "agent-core\venv" (
    echo      Creating virtual environment...
    cd agent-core
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    
    echo      Installing Python dependencies...
    call venv\Scripts\activate.bat
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install Python dependencies
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [OK] Python environment ready
) else (
    echo [OK] Python environment already exists
)

:: Check for .env file
echo.
echo [3/5] Checking configuration...
if not exist "agent-core\.env" (
    if exist "agent-core\.env.example" (
        copy "agent-core\.env.example" "agent-core\.env" >nul
        echo [WARN] Created .env from .env.example
        echo        Please edit agent-core\.env and add your GEMINI_API_KEY
        echo.
        echo        Get your API key at: https://makersuite.google.com/app/apikey
        echo.
        set /p CONTINUE="Press Enter to continue after adding your API key..."
    ) else (
        echo [ERROR] No .env file found in agent-core/
        pause
        exit /b 1
    )
) else (
    echo [OK] Configuration file exists
)

:: Install npm dependencies
echo.
echo [4/5] Setting up Node.js dependencies...
if not exist "node_modules" (
    echo      Installing npm packages (this may take a minute)...
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install npm dependencies
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed
) else (
    echo [OK] Node.js dependencies already installed
)

:: Start the backend server
echo.
echo [5/5] Starting HyperOS services...
echo.
echo      Starting Python backend on port 8000...
start "HyperOS Backend" /min cmd /c "cd agent-core && call venv\Scripts\activate.bat && python main.py"

:: Wait for backend to initialize
echo      Waiting for backend to start...
timeout /t 3 /nobreak >nul

:: Verify backend is running
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Backend may still be starting...
    timeout /t 2 /nobreak >nul
)

:: Start the frontend
echo      Starting Electron frontend...
echo.
echo  ┌─────────────────────────────────────────────────┐
echo  │  HyperOS is starting!                           │
echo  │                                                 │
echo  │  Global Hotkey: Ctrl+Space  (toggle overlay)   │
echo  │  Backend API:   http://127.0.0.1:8000          │
echo  │                                                 │
echo  │  Press Ctrl+C to stop the frontend             │
echo  │  Close the "HyperOS Backend" window to stop    │
echo  │  the Python server                             │
echo  └─────────────────────────────────────────────────┘
echo.

:: Run the dev server (blocking)
npm run dev

:: Cleanup when frontend exits
echo.
echo Shutting down HyperOS...
taskkill /F /FI "WINDOWTITLE eq HyperOS Backend" >nul 2>&1

echo Goodbye!
endlocal
