@echo off
echo 🔍 Unified Betting - Virtual Environment Health Check
echo =====================================================

cd /d "%~dp0"
cd backend

echo Running health check...
python venv_health_check.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Virtual environment is healthy!
    echo 💡 You can run the application normally.
) else (
    echo.
    echo ❌ Virtual environment has issues
    echo 💡 Try running fix_venv.bat or clean_install.bat
)

echo.
pause 