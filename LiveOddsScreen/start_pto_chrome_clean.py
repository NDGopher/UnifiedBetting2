#!/usr/bin/env python3
"""
Clean version of PTO Chrome launcher without emoji issues
"""

import os
import sys
import time
import subprocess
import socket
from pathlib import Path
import psutil

def is_port_in_use(port: int) -> bool:
    """Check if a TCP port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True

def kill_chrome_processes():
    """Kill all existing Chrome processes."""
    print("Killing existing Chrome processes...")
    killed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                proc.kill()
                killed += 1
                print(f"   Killed {proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed > 0:
        print(f"SUCCESS: Killed {killed} Chrome processes")
        time.sleep(3)
    else:
        print("SUCCESS: No Chrome processes to kill")

def find_chrome_executable() -> str:
    """Find Chrome executable path."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", 
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    raise FileNotFoundError("Chrome executable not found")

def launch_chrome_with_debug(profile_dir: str, debug_port: int = 9223) -> subprocess.Popen:
    """Launch Chrome with debugging enabled."""
    chrome_exe = find_chrome_executable()
    
    cmd = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--profile-directory=Profile 1",
        f"--remote-debugging-port={debug_port}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-default-apps", 
        "--disable-popup-blocking",
        "--disable-notifications",
        "--start-maximized",
        "https://picktheodds.app/en/user-control-panel"
    ]
    
    print("Launching Chrome with debugging...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def wait_for_debug_port(port: int, timeout: int = 30) -> bool:
    """Wait for Chrome debug port to become available."""
    print(f"Waiting for Chrome debug port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            print(f"SUCCESS: Chrome debug port {port} is ready!")
            return True
        time.sleep(1)
    
    print(f"ERROR: Timeout waiting for Chrome debug port {port}")
    return False

def main():
    profile_dir = r"C:\Users\steph\AppData\Local\PTO_Chrome_Profile"
    debug_port = 9223
    
    print("Starting PTO Chrome with Debug")
    print("=" * 50)
    
    # Check profile exists
    if not Path(profile_dir).exists():
        print(f"ERROR: Profile directory not found: {profile_dir}")
        return 1
    
    # Kill existing Chrome
    kill_chrome_processes()
    
    # Launch Chrome
    try:
        proc = launch_chrome_with_debug(profile_dir, debug_port)
        
        # Wait for debug port
        if wait_for_debug_port(debug_port):
            print("\nSUCCESS: Chrome is ready for PTO integration!")
            print(f"Debug port: {debug_port}")
            print(f"Profile: {profile_dir}")
            print("PTO should be loaded at: https://picktheodds.app/en/user-control-panel")
            print("\nChrome will remain open. Close manually when done.")
            return 0
        else:
            print("ERROR: Failed to establish debug connection")
            proc.terminate()
            return 1
            
    except Exception as e:
        print(f"ERROR: Error launching Chrome: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
