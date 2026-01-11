@echo off
setlocal
echo ==========================================
echo    HYPEROS NATIVE DESKTOP OVERLAY
echo ==========================================

:: Kill existing
taskkill /F /IM node.exe 2>nul
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM python.exe 2>nul

echo [1/2] Launching Agent Core...
start "HyperOS Agent" /min cmd /c "agent-core\venv\Scripts\python agent-core\main.py"
timeout /t 3 >nul

echo [2/2] Starting Desktop Overlay Interface...
echo (Global Hotkey: Ctrl+Space)

set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
npm run dev

pause
