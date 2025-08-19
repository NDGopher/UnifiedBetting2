#!/usr/bin/env python3
"""
Quick script to check if Chrome is running with debugging on port 9223
"""

import socket
import requests
import json

def check_debug_port(port=9223):
    """Check if Chrome debug port is accessible."""
    print(f"Checking Chrome debug port {port}...")
    
    # Check if port is open
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex(('127.0.0.1', port))
            if result != 0:
                print(f"ERROR: Port {port} is not open")
                return False
        print(f"SUCCESS: Port {port} is open")
    except Exception as e:
        print(f"ERROR: Cannot check port {port}: {e}")
        return False
    
    # Check if Chrome DevTools API responds
    try:
        response = requests.get(f'http://127.0.0.1:{port}/json', timeout=5)
        if response.status_code == 200:
            tabs = response.json()
            print(f"SUCCESS: Chrome DevTools API responding with {len(tabs)} tabs")
            for i, tab in enumerate(tabs[:3]):
                print(f"  Tab {i+1}: {tab.get('title', 'No title')} - {tab.get('url', 'No URL')}")
            return True
        else:
            print(f"ERROR: Chrome DevTools API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to Chrome DevTools API: {e}")
        return False

def main():
    print("Chrome Debug Port Checker")
    print("=" * 30)
    
    if check_debug_port(9223):
        print("\n✅ Chrome is ready for PTO integration!")
        print("You can now run the LiveOddsScreen system.")
    else:
        print("\n❌ Chrome is not ready for PTO integration!")
        print("Please run: python start_pto_chrome.py")
    
    return 0

if __name__ == "__main__":
    main()
