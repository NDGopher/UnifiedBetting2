#!/usr/bin/env python3
"""
Unified Betting Application Launcher with Menu System
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Import the original launcher functions
from launch import (
    print_banner, print_status, Colors, 
    setup_backend, setup_frontend, 
    wait_for_backend, launch_application
)

def run_health_check():
    """Run the virtual environment health check."""
    print_status("🔍 Running virtual environment health check...", "INFO", Colors.BLUE)
    
    backend_dir = Path(__file__).parent / "backend"
    health_check_script = backend_dir / "venv_health_check.py"
    
    if not health_check_script.exists():
        print_status("❌ Health check script not found", "ERROR", Colors.RED)
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(health_check_script)],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_status("✅ Virtual environment is healthy!", "SUCCESS", Colors.GREEN)
            return True
        else:
            print_status("❌ Virtual environment has issues", "ERROR", Colors.RED)
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print_status(f"❌ Health check failed: {e}", "ERROR", Colors.RED)
        return False

def run_clean_install():
    """Run the clean install script."""
    print_status("🔧 Running clean install...", "INFO", Colors.BLUE)
    
    backend_dir = Path(__file__).parent / "backend"
    clean_install_script = backend_dir / "clean_install.bat"
    
    if not clean_install_script.exists():
        print_status("❌ Clean install script not found", "ERROR", Colors.RED)
        return False
    
    try:
        result = subprocess.run(
            [str(clean_install_script)],
            cwd=backend_dir,
            shell=True
        )
        
        if result.returncode == 0:
            print_status("✅ Clean install completed successfully!", "SUCCESS", Colors.GREEN)
            return True
        else:
            print_status("❌ Clean install failed", "ERROR", Colors.RED)
            return False
    except Exception as e:
        print_status(f"❌ Clean install failed: {e}", "ERROR", Colors.RED)
        return False

def show_menu():
    """Show the main menu."""
    while True:
        print_banner()
        print(f"{Colors.CYAN}Choose an option:{Colors.RESET}")
        print(f"{Colors.WHITE}1.{Colors.RESET} 🚀 Launch Application")
        print(f"{Colors.WHITE}2.{Colors.RESET} 🔍 Check Virtual Environment Health")
        print(f"{Colors.WHITE}3.{Colors.RESET} 🔧 Clean Install (Fix Issues)")
        print(f"{Colors.WHITE}4.{Colors.RESET} 📦 Setup Dependencies Only")
        print(f"{Colors.WHITE}5.{Colors.RESET} 🚪 Exit")
        print()
        
        choice = input(f"{Colors.YELLOW}Enter your choice (1-5): {Colors.RESET}").strip()
        
        if choice == "1":
            print_status("🚀 Launching application...", "INFO", Colors.BLUE)
            try:
                launch_application()
            except KeyboardInterrupt:
                print_status("Application stopped by user", "INFO", Colors.YELLOW)
            except Exception as e:
                print_status(f"Launch failed: {e}", "ERROR", Colors.RED)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
        elif choice == "2":
            print()
            if run_health_check():
                print_status("💡 Your virtual environment is ready to use!", "INFO", Colors.CYAN)
            else:
                print_status("💡 Consider running option 3 to fix issues", "INFO", Colors.CYAN)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
        elif choice == "3":
            print()
            print_status("⚠️ This will completely recreate your virtual environment", "WARNING", Colors.YELLOW)
            confirm = input(f"{Colors.YELLOW}Are you sure? (y/N): {Colors.RESET}").strip().lower()
            if confirm in ['y', 'yes']:
                if run_clean_install():
                    print_status("✅ Virtual environment has been fixed!", "SUCCESS", Colors.GREEN)
                else:
                    print_status("❌ Clean install failed", "ERROR", Colors.RED)
            else:
                print_status("Clean install cancelled", "INFO", Colors.CYAN)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
        elif choice == "4":
            print()
            print_status("📦 Setting up dependencies only...", "INFO", Colors.BLUE)
            try:
                project_dir = Path(__file__).parent
                backend_dir = project_dir / "backend"
                frontend_dir = project_dir / "frontend"
                
                # Setup backend
                print_status("Setting up backend...", "INFO", Colors.BLUE)
                setup_backend()
                
                # Setup frontend
                print_status("Setting up frontend...", "INFO", Colors.BLUE)
                setup_frontend()
                
                print_status("✅ Dependencies setup completed!", "SUCCESS", Colors.GREEN)
            except Exception as e:
                print_status(f"❌ Setup failed: {e}", "ERROR", Colors.RED)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            
        elif choice == "5":
            print_status("👋 Goodbye!", "INFO", Colors.CYAN)
            break
            
        else:
            print_status("❌ Invalid choice. Please enter 1-5.", "ERROR", Colors.RED)
            time.sleep(1)

if __name__ == "__main__":
    try:
        show_menu()
    except KeyboardInterrupt:
        print_status("\n👋 Goodbye!", "INFO", Colors.CYAN)
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR", Colors.RED) 