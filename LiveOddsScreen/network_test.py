#!/usr/bin/env python3
"""
Simple network test to check PTO connectivity and data access
"""

import urllib.request
import urllib.error
import json
import socket
import time

def test_basic_connectivity():
    """Test basic connectivity to PTO"""
    print("🌐 Testing Basic PTO Connectivity")
    print("=" * 35)
    
    hosts = [
        ("picktheodds.app", 443),
        ("api.picktheodds.app", 443),
        ("picktheodds.app", 80)
    ]
    
    for host, port in hosts:
        try:
            print(f"[NET] Testing {host}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"[NET] ✅ {host}:{port} - OPEN")
            else:
                print(f"[NET] ❌ {host}:{port} - CLOSED")
                
        except Exception as e:
            print(f"[NET] ❌ {host}:{port} - ERROR: {e}")

def test_http_endpoints():
    """Test HTTP endpoints"""
    print("\n📡 Testing HTTP Endpoints")
    print("=" * 25)
    
    endpoints = [
        "https://picktheodds.app/",
        "https://api.picktheodds.app/",
        "https://picktheodds.app/api/",
        "https://api.picktheodds.app/graphql",
        "https://picktheodds.app/api/graphql"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"[HTTP] Testing: {endpoint}")
            
            req = urllib.request.Request(endpoint)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                data = response.read()[:100]
                
                print(f"[HTTP] ✅ Status: {status}")
                print(f"[HTTP] Type: {content_type}")
                print(f"[HTTP] Data: {data}")
                
        except urllib.error.HTTPError as e:
            print(f"[HTTP] ❌ HTTP {e.code}: {e.reason}")
            try:
                error_data = e.read()[:100]
                print(f"[HTTP] Error data: {error_data}")
            except:
                pass
        except Exception as e:
            print(f"[HTTP] ❌ Error: {e}")

def test_websocket_port():
    """Test if WebSocket port is accessible"""
    print("\n🔌 Testing WebSocket Port")
    print("=" * 25)
    
    try:
        # Test if we can connect to the WebSocket port
        host = "api.picktheodds.app"
        port = 443
        
        print(f"[WS] Testing WebSocket connectivity to {host}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"[WS] ✅ WebSocket port accessible")
            
            # Try to send basic HTTP request
            request = (
                f"GET /graphql HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode()
            
            sock.send(request)
            response = sock.recv(1024)
            print(f"[WS] Response: {response[:200]}")
            
        else:
            print(f"[WS] ❌ WebSocket port not accessible")
        
        sock.close()
        
    except Exception as e:
        print(f"[WS] ❌ WebSocket test error: {e}")

def check_current_speed():
    """Check current system speed"""
    print("\n⚡ Checking Current System Speed")
    print("=" * 30)
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        speed_mode = config.get("speed_mode", False)
        fast_refresh = config.get("fast_refresh", "not set")
        timeouts = config.get("timeouts", {})
        
        print(f"[SPEED] Speed mode: {speed_mode}")
        print(f"[SPEED] Fast refresh: {fast_refresh}")
        print(f"[SPEED] Page load timeout: {timeouts.get('page_load', 'default')}")
        
        if speed_mode:
            print(f"[SPEED] ✅ Speed optimizations ACTIVE")
        else:
            print(f"[SPEED] ⚠️ Speed optimizations NOT ACTIVE")
            
    except Exception as e:
        print(f"[SPEED] ❌ Error checking config: {e}")

def main():
    print("🔍 PTO Network & Speed Investigation")
    print("=" * 45)
    
    # Test 1: Basic connectivity
    test_basic_connectivity()
    
    # Test 2: HTTP endpoints  
    test_http_endpoints()
    
    # Test 3: WebSocket port
    test_websocket_port()
    
    # Test 4: Current speed settings
    check_current_speed()
    
    print(f"\n📊 INVESTIGATION COMPLETE")
    print("=" * 25)
    print(f"Check the results above to see:")
    print(f"1. Which endpoints are accessible")
    print(f"2. If WebSocket connection is possible")
    print(f"3. Current speed optimization status")

if __name__ == "__main__":
    main()
