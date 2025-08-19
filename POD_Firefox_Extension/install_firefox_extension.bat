@echo off
echo 🦊 POD Firefox Extension Installer
echo ====================================

echo.
echo This script will help you install the POD Firefox Extension.
echo.

echo 📋 Installation Methods:
echo.
echo 1. Temporary Installation (Development)
echo    - Open Firefox and go to: about:debugging
echo    - Click "This Firefox" 
echo    - Click "Load Temporary Add-on"
echo    - Select the manifest.json file from this folder
echo.
echo 2. Permanent Installation (Recommended)
echo    - Create a ZIP file of all extension files
echo    - Open Firefox and go to: about:addons
echo    - Click the gear icon (⚙️) 
echo    - Select "Install Add-on From File"
echo    - Choose your ZIP file
echo.

echo 🔧 Creating ZIP file for permanent installation...
powershell -Command "Compress-Archive -Path '.\*' -DestinationPath 'pod-firefox-extension.zip' -Force"

if %ERRORLEVEL% EQU 0 (
    echo ✅ ZIP file created: pod-firefox-extension.zip
    echo.
    echo 📦 You can now install the extension using Method 2 above.
) else (
    echo ❌ Failed to create ZIP file
    echo 💡 You can manually create a ZIP file of all the extension files.
)

echo.
echo 🌐 Opening Firefox add-ons page...
start firefox about:addons

echo.
echo 📖 For detailed instructions, see README.md
echo.
pause 