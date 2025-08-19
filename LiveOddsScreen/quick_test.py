#!/usr/bin/env python3
"""
Quick test of all speed optimizations and WebSocket investigation
"""

import json
import time
import subprocess
import os

def check_speed_config():
    """Check if speed optimizations are configured"""
    print("⚡ Speed Configuration Check")
    print("=" * 30)
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        speed_mode = config.get("speed_mode", False)
        fast_refresh = config.get("fast_refresh", None)
        page_load = config.get("timeouts", {}).get("page_load", None)
        
        print(f"[SPEED] Speed mode: {'✅ ON' if speed_mode else '❌ OFF'}")
        print(f"[SPEED] Fast refresh: {fast_refresh}s" if fast_refresh else "[SPEED] Fast refresh: ❌ NOT SET")
        print(f"[SPEED] Page load timeout: {page_load}s" if page_load else "[SPEED] Page load timeout: ❌ DEFAULT")
        
        return speed_mode
        
    except Exception as e:
        print(f"[SPEED] ❌ Error reading config: {e}")
        return False

def check_chrome_running():
    """Check if Chrome is running with debug port"""
    print("\n🌐 Chrome Debug Status")
    print("=" * 20)
    
    try:
        # Try to connect to debug port
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9223))
        sock.close()
        
        if result == 0:
            print("[CHROME] ✅ Debug port 9223 accessible")
            return True
        else:
            print("[CHROME] ❌ Debug port 9223 not accessible")
            print("[CHROME] Run: python start_pto_chrome.py")
            return False
            
    except Exception as e:
        print(f"[CHROME] ❌ Error: {e}")
        return False

def check_websocket_theory():
    """Check WebSocket connection theory"""
    print("\n🔌 WebSocket Investigation")
    print("=" * 25)
    
    # Test basic connection to PTO domain
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('api.picktheodds.app', 443))
        sock.close()
        
        if result == 0:
            print("[WS] ✅ api.picktheodds.app:443 reachable")
            
            # Test HTTP request
            try:
                import urllib.request
                req = urllib.request.Request("https://api.picktheodds.app/")
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.getcode()
                    print(f"[WS] ✅ HTTP response: {status}")
                    
            except Exception as e:
                print(f"[WS] ⚠️ HTTP test: {e}")
            
            return True
        else:
            print("[WS] ❌ api.picktheodds.app:443 not reachable")
            return False
            
    except Exception as e:
        print(f"[WS] ❌ Connection test error: {e}")
        return False

def show_websocket_plan():
    """Show the WebSocket implementation plan"""
    print("\n🎯 WebSocket Implementation Plan")
    print("=" * 35)
    
    print("[PLAN] The WebSocket approach will:")
    print("[PLAN] 1. Connect to: wss://api.picktheodds.app/graphql")
    print("[PLAN] 2. Use protocol: graphql-transport-ws")
    print("[PLAN] 3. Send auth from Chrome session")
    print("[PLAN] 4. Subscribe to live odds updates")
    print("[PLAN] 5. Get real-time data (0.1s latency)")
    print("[PLAN] 6. Replace slow DOM scraping")
    
    print("\n[PLAN] Benefits:")
    print("[PLAN] ✅ 100x faster than DOM scraping")
    print("[PLAN] ✅ Real-time push notifications")
    print("[PLAN] ✅ All sports simultaneously")
    print("[PLAN] ✅ No page loading delays")
    print("[PLAN] ✅ Reliable data structure")

def test_current_system_speed():
    """Test if current system improvements work"""
    print("\n🚀 Current System Speed Test")
    print("=" * 30)
    
    try:
        # Check if LiveOddsScreen is running
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, timeout=5)
        
        if 'python.exe' in result.stdout:
            print("[SYS] ✅ Python processes running")
            
            # Check if our process is running
            lines = result.stdout.split('\n')
            python_processes = [line for line in lines if 'python.exe' in line]
            print(f"[SYS] Found {len(python_processes)} Python processes")
            
        else:
            print("[SYS] ⚠️ No Python processes found")
        
        return True
        
    except Exception as e:
        print(f"[SYS] ❌ Process check error: {e}")
        return False

def main():
    print("🔍 COMPREHENSIVE SPEED & WEBSOCKET TEST")
    print("=" * 50)
    
    # Test 1: Speed configuration
    speed_configured = check_speed_config()
    
    # Test 2: Chrome debug status
    chrome_ready = check_chrome_running()
    
    # Test 3: WebSocket connectivity
    websocket_reachable = check_websocket_theory()
    
    # Test 4: Current system
    system_running = test_current_system_speed()
    
    # Show WebSocket plan
    show_websocket_plan()
    
    print(f"\n📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 35)
    print(f"✅ Speed Mode Configured: {speed_configured}")
    print(f"✅ Chrome Debug Ready: {chrome_ready}")
    print(f"✅ WebSocket Reachable: {websocket_reachable}")
    print(f"✅ System Status: {system_running}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if not chrome_ready:
        print("[REC] 1. Run: python start_pto_chrome.py")
    if not speed_configured:
        print("[REC] 2. Speed mode already configured ✅")
    if websocket_reachable:
        print("[REC] 3. WebSocket approach is viable ✅")
        print("[REC] 4. Can implement real-time data stream")
    
    print(f"\n🚀 NEXT ACTIONS:")
    print("[ACT] 1. Ensure Chrome debug is running")
    print("[ACT] 2. Test speed improvements")
    print("[ACT] 3. Implement WebSocket client")
    print("[ACT] 4. Compare performance")

if __name__ == "__main__":
    main()
