#!/usr/bin/env python3
"""
Test Chrome debugging connection and capture WebSocket traffic
"""

import json
import time
import socket
import urllib.request
import urllib.error

def test_chrome_debug_port():
    """Test if Chrome debug port is accessible"""
    print("🌐 Testing Chrome Debug Port 9223")
    print("=" * 35)
    
    try:
        # Test if port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 9223))
        sock.close()
        
        if result != 0:
            print("[DEBUG] ❌ Chrome debug port 9223 not accessible")
            print("[DEBUG] Make sure Chrome is running with --remote-debugging-port=9223")
            return False
        
        print("[DEBUG] ✅ Chrome debug port 9223 is accessible")
        
        # Test DevTools API
        try:
            url = "http://127.0.0.1:9223/json"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read()
                tabs = json.loads(data)
                
                print(f"[DEBUG] ✅ Found {len(tabs)} Chrome tabs")
                
                # Look for PTO tabs
                pto_tabs = []
                for tab in tabs:
                    url = tab.get('url', '')
                    title = tab.get('title', '')
                    if 'picktheodds.app' in url:
                        pto_tabs.append(tab)
                        print(f"[DEBUG]   PTO Tab: {title[:50]} - {url[:80]}")
                
                if pto_tabs:
                    print(f"[DEBUG] ✅ Found {len(pto_tabs)} PTO tabs")
                    return pto_tabs
                else:
                    print(f"[DEBUG] ⚠️ No PTO tabs found")
                    return []
                    
        except Exception as e:
            print(f"[DEBUG] ❌ DevTools API error: {e}")
            return False
            
    except Exception as e:
        print(f"[DEBUG] ❌ Debug port test error: {e}")
        return False

def capture_websocket_data(tab_id, duration=10):
    """Capture WebSocket data from a specific tab"""
    print(f"\n📡 Capturing WebSocket Data (Tab: {tab_id})")
    print("=" * 40)
    
    try:
        # Enable Network domain
        enable_url = f"http://127.0.0.1:9223/json/runtime/evaluate"
        
        # This is a simplified approach - real implementation would use CDP
        print(f"[WS] Would capture WebSocket traffic for {duration} seconds...")
        print(f"[WS] Tab ID: {tab_id}")
        
        # For now, just indicate what we would do
        print(f"[WS] Real implementation would:")
        print(f"[WS]   1. Connect to Chrome DevTools Protocol")
        print(f"[WS]   2. Enable Network domain")
        print(f"[WS]   3. Listen for WebSocket frame events")
        print(f"[WS]   4. Capture GraphQL messages")
        
        return True
        
    except Exception as e:
        print(f"[WS] ❌ Capture error: {e}")
        return False

def test_direct_websocket():
    """Test direct WebSocket connection to PTO"""
    print(f"\n🔌 Testing Direct WebSocket Connection")
    print("=" * 40)
    
    # Test basic socket connection
    try:
        print(f"[WS] Testing socket connection to api.picktheodds.app:443...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('api.picktheodds.app', 443))
        sock.close()
        
        if result == 0:
            print(f"[WS] ✅ Socket connection successful")
        else:
            print(f"[WS] ❌ Socket connection failed")
            return False
        
        # Test HTTP to GraphQL endpoint
        print(f"[WS] Testing HTTP request to GraphQL endpoint...")
        
        url = "https://api.picktheodds.app/graphql"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        req.add_header('Origin', 'https://picktheodds.app')
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                data = response.read()[:200]
                print(f"[WS] ✅ HTTP Response: {status}")
                print(f"[WS] Data: {data}")
                
        except urllib.error.HTTPError as e:
            print(f"[WS] HTTP Error {e.code}: {e.reason}")
            if e.code == 400:
                print(f"[WS] ✅ 400 error is normal for GraphQL without proper query")
            try:
                error_data = e.read()[:200]
                print(f"[WS] Error data: {error_data}")
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"[WS] ❌ Direct WebSocket test error: {e}")
        return False

def check_system_status():
    """Check current system status"""
    print(f"\n⚡ Checking System Status")
    print("=" * 25)
    
    try:
        # Check if LiveOddsScreen is running
        import psutil
        
        # Look for python processes running our scripts
        live_screen_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe':
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'run_live_screen.py' in cmdline:
                        live_screen_running = True
                        print(f"[SYS] ✅ LiveOddsScreen running (PID: {proc.info['pid']})")
                        break
            except:
                continue
        
        if not live_screen_running:
            print(f"[SYS] ⚠️ LiveOddsScreen not running")
        
    except ImportError:
        print(f"[SYS] psutil not available, cannot check processes")
    except Exception as e:
        print(f"[SYS] ❌ System check error: {e}")

def main():
    print("🔍 Chrome Debug & WebSocket Investigation")
    print("=" * 50)
    
    # Test 1: Chrome debug port
    pto_tabs = test_chrome_debug_port()
    
    # Test 2: Direct WebSocket
    ws_success = test_direct_websocket()
    
    # Test 3: System status
    check_system_status()
    
    # Test 4: If we have PTO tabs, try to capture data
    if pto_tabs and len(pto_tabs) > 0:
        tab_id = pto_tabs[0].get('id')
        if tab_id:
            capture_websocket_data(tab_id)
    
    print(f"\n📊 INVESTIGATION RESULTS")
    print("=" * 25)
    print(f"✅ Chrome Debug: {bool(pto_tabs)}")
    print(f"✅ WebSocket Reachable: {ws_success}")
    print(f"✅ PTO Tabs Found: {len(pto_tabs) if pto_tabs else 0}")
    
    if pto_tabs:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Chrome debug connection is working")
        print(f"2. PTO tabs are accessible")
        print(f"3. Can implement WebSocket traffic capture")
        print(f"4. Can extract real-time data from network traffic")
    else:
        print(f"\n⚠️ ISSUES:")
        print(f"1. Make sure Chrome is running with debug port")
        print(f"2. Make sure PTO tabs are open")
        print(f"3. Run: python start_pto_chrome.py")

if __name__ == "__main__":
    main()
