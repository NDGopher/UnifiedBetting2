#!/usr/bin/env python3
"""
Fix corrupted virtual environment by completely removing and recreating it.
"""

import os
import sys
import shutil
import subprocess
import time

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🔧 Fixing corrupted virtual environment...")
    
    # Get the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(backend_dir, "venv")
    
    print(f"📍 Backend directory: {backend_dir}")
    print(f"📍 Virtual environment: {venv_dir}")
    
    # Step 1: Remove the corrupted virtual environment
    print("\n🗑️ Removing corrupted virtual environment...")
    if os.path.exists(venv_dir):
        try:
            shutil.rmtree(venv_dir)
            print("✅ Removed corrupted virtual environment")
        except Exception as e:
            print(f"❌ Failed to remove virtual environment: {e}")
            return False
    else:
        print("ℹ️ Virtual environment doesn't exist")
    
    # Step 2: Create a new virtual environment
    print("\n🏗️ Creating new virtual environment...")
    result = run_command("python -m venv venv", cwd=backend_dir)
    if result is None:
        print("❌ Failed to create virtual environment")
        return False
    print("✅ Created new virtual environment")
    
    # Step 3: Activate and upgrade pip
    print("\n⬆️ Upgrading pip...")
    pip_upgrade_cmd = "venv\\Scripts\\python.exe -m pip install --upgrade pip"
    result = run_command(pip_upgrade_cmd, cwd=backend_dir)
    if result is None:
        print("❌ Failed to upgrade pip")
        return False
    print("✅ Upgraded pip")
    
    # Step 4: Install requirements
    print("\n📦 Installing requirements...")
    install_cmd = "venv\\Scripts\\python.exe -m pip install -r requirements.txt"
    result = run_command(install_cmd, cwd=backend_dir)
    if result is None:
        print("❌ Failed to install requirements")
        return False
    print("✅ Installed requirements")
    
    # Step 5: Verify installation
    print("\n🔍 Verifying installation...")
    verify_cmd = "venv\\Scripts\\python.exe -c \"import fastapi, uvicorn, selenium; print('✅ All key packages imported successfully')\""
    result = run_command(verify_cmd, cwd=backend_dir)
    if result is None:
        print("❌ Verification failed")
        return False
    print("✅ Verification passed")
    
    print("\n🎉 Virtual environment fixed successfully!")
    print("💡 You can now run the application again.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to fix virtual environment")
        sys.exit(1) 