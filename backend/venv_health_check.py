#!/usr/bin/env python3
"""
Virtual Environment Health Check and Maintenance Tool
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout if capture_output else True
    except subprocess.CalledProcessError as e:
        if capture_output:
            return None
        else:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {e.stderr}")
            return False

def check_corrupted_packages(venv_path):
    """Check for corrupted packages with invalid names."""
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    if not os.path.exists(site_packages):
        return False, []
    
    corrupted = []
    for item in os.listdir(site_packages):
        if item.startswith("~") or item.endswith("~"):
            corrupted.append(item)
    
    return len(corrupted) > 0, corrupted

def check_missing_record_files(venv_path):
    """Check for packages missing RECORD files."""
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    if not os.path.exists(site_packages):
        return False, []
    
    missing_records = []
    for item in os.listdir(site_packages):
        item_path = os.path.join(site_packages, item)
        if os.path.isdir(item_path) and not item.startswith("~"):
            # Check if it's a package directory
            if os.path.exists(os.path.join(item_path, "__init__.py")):
                record_file = os.path.join(item_path, "*.dist-info", "RECORD")
                if not glob.glob(record_file):
                    missing_records.append(item)
    
    return len(missing_records) > 0, missing_records

def check_key_packages(venv_path):
    """Check if key packages can be imported."""
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        return False, "Python executable not found"
    
    test_cmd = f'"{python_exe}" -c "import fastapi, uvicorn, selenium; print(\'OK\')"'
    result = run_command(test_cmd, capture_output=True)
    return result is not None, result

def fix_corrupted_packages(venv_path):
    """Remove corrupted packages."""
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    corrupted, corrupted_list = check_corrupted_packages(venv_path)
    
    if not corrupted:
        return True
    
    print(f"🗑️ Removing {len(corrupted_list)} corrupted packages...")
    for package in corrupted_list:
        package_path = os.path.join(site_packages, package)
        try:
            if os.path.isdir(package_path):
                import shutil
                shutil.rmtree(package_path)
            else:
                os.remove(package_path)
            print(f"  ✅ Removed: {package}")
        except Exception as e:
            print(f"  ❌ Failed to remove {package}: {e}")
            return False
    
    return True

def reinstall_problem_packages(venv_path):
    """Reinstall packages with missing RECORD files."""
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    missing_records, missing_list = check_missing_record_files(venv_path)
    
    if not missing_records:
        return True
    
    print(f"🔄 Reinstalling {len(missing_list)} packages with missing RECORD files...")
    
    # Common packages that might have issues
    common_packages = ["selenium", "fastapi", "uvicorn", "pydantic", "requests"]
    
    for package in common_packages:
        if package in missing_list:
            print(f"  🔄 Reinstalling {package}...")
            cmd = f'"{python_exe}" -m pip install --force-reinstall --no-deps {package}'
            if not run_command(cmd, capture_output=False):
                print(f"  ❌ Failed to reinstall {package}")
                return False
            print(f"  ✅ Reinstalled {package}")
    
    return True

def main():
    print("🔍 Virtual Environment Health Check")
    print("=" * 40)
    
    # Get backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(backend_dir, "venv")
    
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("💡 Run the clean install script to create it.")
        return False
    
    print(f"📍 Checking: {venv_path}")
    
    # Check 1: Corrupted packages
    print("\n1️⃣ Checking for corrupted packages...")
    corrupted, corrupted_list = check_corrupted_packages(venv_path)
    if corrupted:
        print(f"❌ Found {len(corrupted_list)} corrupted packages: {corrupted_list}")
        print("🔧 Attempting to fix...")
        if not fix_corrupted_packages(venv_path):
            print("❌ Failed to fix corrupted packages")
            print("💡 Run clean_install.bat for complete reset")
            return False
        print("✅ Fixed corrupted packages")
    else:
        print("✅ No corrupted packages found")
    
    # Check 2: Missing RECORD files
    print("\n2️⃣ Checking for missing RECORD files...")
    missing_records, missing_list = check_missing_record_files(venv_path)
    if missing_records:
        print(f"⚠️ Found {len(missing_list)} packages with missing RECORD files: {missing_list}")
        print("🔧 Attempting to reinstall...")
        if not reinstall_problem_packages(venv_path):
            print("❌ Failed to reinstall packages")
            print("💡 Run clean_install.bat for complete reset")
            return False
        print("✅ Reinstalled problem packages")
    else:
        print("✅ No missing RECORD files found")
    
    # Check 3: Key package imports
    print("\n3️⃣ Testing key package imports...")
    imports_ok, result = check_key_packages(venv_path)
    if imports_ok:
        print("✅ All key packages import successfully")
    else:
        print(f"❌ Package import test failed: {result}")
        print("💡 Run clean_install.bat for complete reset")
        return False
    
    print("\n🎉 Virtual environment is healthy!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 