@echo off
REM =============================================
REM LIVE ODDS SCREEN - One Click Launch
REM =============================================

echo =============================================
echo LIVE ODDS SCREEN LAUNCHER
echo =============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python first
    pause
    exit /b 1
)

echo [1/3] Starting PTO Chrome with debugging...
python start_pto_chrome_clean.py

echo [2/3] Waiting for Chrome to stabilize...
timeout /t 3 /nobreak >nul

echo [3/3] Launching Sports Selector...
echo.
echo *** SPORTS SELECTION GUI WILL APPEAR ***
echo *** Select your sports and markets ***
echo.

REM Run the simple sports selector
python simple_launcher.py

echo.
echo Live Odds Screen session complete.
echo Press any key to close this window.
pause >nul
