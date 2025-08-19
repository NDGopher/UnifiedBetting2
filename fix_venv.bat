@echo off
echo 🔧 Fixing Unified Betting Virtual Environment
echo ================================================

cd /d "%~dp0"
cd backend

echo Running virtual environment fix script...
python fix_venv.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Virtual environment fixed successfully!
    echo 💡 You can now run the application again.
) else (
    echo.
    echo ❌ Failed to fix virtual environment
)

echo.
pause 