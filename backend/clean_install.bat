@echo off
echo 🔧 Clean Installing Virtual Environment
echo ========================================

echo.
echo Step 1: Removing old virtual environment...
if exist venv (
    rmdir /s /q venv
    echo ✅ Removed old virtual environment
) else (
    echo ℹ️ No old virtual environment found
)

echo.
echo Step 2: Creating new virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Created new virtual environment

echo.
echo Step 3: Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)
echo ✅ Upgraded pip

echo.
echo Step 4: Installing requirements...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Installed requirements

echo.
echo Step 5: Verifying installation...
venv\Scripts\python.exe -c "import fastapi, uvicorn, selenium; print('✅ All key packages imported successfully')"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Verification failed
    pause
    exit /b 1
)
echo ✅ Verification passed

echo.
echo 🎉 Virtual environment setup completed successfully!
echo 💡 You can now run the application.
echo.
pause 