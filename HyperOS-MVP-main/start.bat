@echo off
setlocal
echo ==========================================
echo    HYPEROS NATIVE DESKTOP OVERLAY
echo ==========================================

:: Kill existing
taskkill /F /IM node.exe 2>nul
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM python.exe 2>nul

echo [1/3] Verifying Environment...
python download_electron.py
if %errorlevel% neq 0 (
    echo [ERROR] setup failed. Please follow instructions above.
    pause
    exit /b %errorlevel%
)

echo [2/3] Launching Agent Core...
start "HyperOS Agent" /min cmd /c "python agent-core\main.py"
timeout /t 3 >nul

echo [3/3] Starting Desktop Overlay Interface...
echo (Global Hotkey: Ctrl+Space)

set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
npm run dev

pause
