@echo off
REM Run the live odds system after sports selection

echo =============================================
echo LIVE ODDS COMPARISON - Starting System
echo =============================================

REM Check if selections exist
if not exist "sports_selection.json" (
    echo ERROR: No sports selections found!
    echo Please run LIVE_ODDS_SCREEN.bat first to select sports.
    pause
    exit /b 1
)

echo [1/2] Fixing any remaining Python issues...
python fix_all_indentation.py >nul 2>&1

echo [2/2] Starting live odds comparison system...
echo.
echo Opening dashboard at: http://127.0.0.1:8765/dashboard.html
echo The system will now pull live odds and compare them.
echo.

REM Start the main system (full version with all scraping)
python -u run_live_screen_full.py --port 8765

echo.
echo Live odds session complete.
pause
