@echo off
echo ========================================
echo    UnifiedBetting Auto Setup & Launch
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo ✅ All prerequisites found!
echo.

REM Check if repository already exists
if exist "UnifiedBetting" (
    echo 📁 Repository already exists, updating...
    cd UnifiedBetting
    git pull origin main
) else (
    echo 📥 Cloning repository...
    git clone https://github.com/NDGopher/UnifiedBetting.git
    cd UnifiedBetting
)

echo.
echo 🔧 Setting up dependencies...
python setup_dependencies.py

if errorlevel 1 (
    echo.
    echo ❌ Setup failed! Check the errors above.
    pause
    exit /b 1
)

echo.
echo 🚀 Launching UnifiedBetting...
python launch.py

pause 