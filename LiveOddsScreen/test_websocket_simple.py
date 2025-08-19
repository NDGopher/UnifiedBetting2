#!/usr/bin/env python3
"""
Simple WebSocket test to analyze PTO's GraphQL connection
Uses basic socket and HTTP upgrade to test WebSocket connection
"""

import socket
import ssl
import base64
import hashlib
import json
import time
import threading
from urllib.parse import urlparse

class SimpleWebSocketClient:
    def __init__(self, url):
        self.url = url
        self.connected = False
        self.socket = None
        self.messages = []
        
    def generate_key(self):
        """Generate WebSocket key"""
        return base64.b64encode(b'test-key-1234567890').decode()
    
    def connect(self):
        """Connect using basic socket with WebSocket upgrade"""
        try:
            parsed = urlparse(self.url)
            host = parsed.hostname
            port = 443 if parsed.scheme == 'wss' else 80
            
            print(f"[WS] Connecting to {host}:{port}...")
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Wrap with SSL for wss://
            if parsed.scheme == 'wss':
                context = ssl.create_default_context()
                self.socket = context.wrap_socket(sock, server_hostname=host)
            else:
                self.socket = sock
            
            # Connect
            self.socket.connect((host, port))
            
            # Send WebSocket upgrade request
            key = self.generate_key()
            upgrade_request = (
                f"GET {parsed.path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Upgrade: websocket\r\n"
                f"Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                f"Sec-WebSocket-Version: 13\r\n"
                f"Sec-WebSocket-Protocol: graphql-transport-ws\r\n"
                f"Origin: https://picktheodds.app\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
                f"\r\n"
            ).encode()
            
            self.socket.send(upgrade_request)
            
            # Read response
            response = self.socket.recv(4096).decode()
            print(f"[WS] Server response:")
            print(response[:500])
            
            if "101 Switching Protocols" in response:
                print(f"[WS] ✅ WebSocket handshake successful!")
                self.connected = True
                return True
            else:
                print(f"[WS] ❌ WebSocket handshake failed")
                return False
                
        except Exception as e:
            print(f"[WS] Connection error: {e}")
            return False
    
    def send_frame(self, payload):
        """Send WebSocket frame"""
        if not self.connected:
            return False
        
        try:
            # Simple text frame (opcode 1)
            frame = bytearray()
            frame.append(0x81)  # FIN + text frame
            
            payload_bytes = payload.encode() if isinstance(payload, str) else payload
            payload_len = len(payload_bytes)
            
            if payload_len < 126:
                frame.append(0x80 | payload_len)  # Masked + length
            else:
                frame.append(0x80 | 126)  # Masked + extended length
                frame.extend(payload_len.to_bytes(2, 'big'))
            
            # Masking key (required for client->server)
            mask = b'\x00\x00\x00\x00'
            frame.extend(mask)
            
            # Masked payload
            frame.extend(payload_bytes)
            
            self.socket.send(frame)
            return True
            
        except Exception as e:
            print(f"[WS] Send error: {e}")
            return False
    
    def receive_frame(self, timeout=5):
        """Receive WebSocket frame"""
        if not self.connected:
            return None
        
        try:
            self.socket.settimeout(timeout)
            
            # Read frame header
            header = self.socket.recv(2)
            if len(header) < 2:
                return None
            
            fin = header[0] & 0x80
            opcode = header[0] & 0x0f
            masked = header[1] & 0x80
            payload_len = header[1] & 0x7f
            
            # Extended payload length
            if payload_len == 126:
                length_bytes = self.socket.recv(2)
                payload_len = int.from_bytes(length_bytes, 'big')
            elif payload_len == 127:
                length_bytes = self.socket.recv(8)
                payload_len = int.from_bytes(length_bytes, 'big')
            
            # Masking key (if present)
            if masked:
                mask = self.socket.recv(4)
            
            # Payload
            payload = self.socket.recv(payload_len)
            
            if opcode == 1:  # Text frame
                text = payload.decode()
                print(f"[WS] Received: {text[:200]}...")
                return text
            elif opcode == 8:  # Close frame
                print(f"[WS] Connection closed by server")
                self.connected = False
                return None
            
        except socket.timeout:
            return None
        except Exception as e:
            print(f"[WS] Receive error: {e}")
            return None
    
    def test_graphql_connection(self):
        """Test GraphQL WebSocket connection"""
        if not self.connect():
            return False
        
        # Send connection_init
        init_message = json.dumps({
            "type": "connection_init",
            "payload": {}
        })
        
        print(f"[WS] Sending connection_init...")
        if self.send_frame(init_message):
            # Wait for connection_ack
            response = self.receive_frame(10)
            if response:
                try:
                    data = json.loads(response)
                    if data.get("type") == "connection_ack":
                        print(f"[WS] ✅ GraphQL connection acknowledged!")
                        return True
                except:
                    pass
        
        print(f"[WS] ❌ GraphQL connection failed")
        return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False

def test_pto_websocket():
    """Test PTO WebSocket connection"""
    print("🌐 Testing PTO WebSocket Connection")
    print("=" * 40)
    
    url = "wss://api.picktheodds.app/graphql"
    client = SimpleWebSocketClient(url)
    
    if client.test_graphql_connection():
        print(f"[WS] ✅ SUCCESS! WebSocket is accessible")
        
        # Try to subscribe to something
        subscription = json.dumps({
            "id": "test_sub",
            "type": "start",
            "payload": {
                "query": "subscription { oddsUpdated { id } }"
            }
        })
        
        print(f"[WS] Testing subscription...")
        client.send_frame(subscription)
        
        # Listen for responses
        for i in range(5):
            response = client.receive_frame(3)
            if response:
                print(f"[WS] Response {i+1}: {response[:100]}...")
            else:
                print(f"[WS] No response {i+1}")
        
        client.close()
        return True
    else:
        print(f"[WS] ❌ FAILED! WebSocket not accessible")
        client.close()
        return False

def test_api_endpoints():
    """Test PTO API endpoints"""
    print("\n🔍 Testing PTO API Endpoints")
    print("=" * 30)
    
    import urllib.request
    import urllib.error
    
    endpoints = [
        "https://api.picktheodds.app/graphql",
        "https://picktheodds.app/api/graphql",
        "https://api.picktheodds.app/health",
        "https://api.picktheodds.app/",
        "https://picktheodds.app/api/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"[API] Testing: {endpoint}")
            
            req = urllib.request.Request(endpoint)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Origin', 'https://picktheodds.app')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                data = response.read()[:200]
                
                print(f"[API] ✅ Status: {status}")
                print(f"[API] Data: {data}")
                
                if status == 200:
                    return endpoint
                    
        except urllib.error.HTTPError as e:
            print(f"[API] HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            print(f"[API] Error: {e}")
    
    return None

def main():
    print("🚀 PTO Data Source Investigation")
    print("=" * 50)
    
    # Test 1: WebSocket
    ws_success = test_pto_websocket()
    
    # Test 2: API endpoints
    api_endpoint = test_api_endpoints()
    
    print(f"\n📊 INVESTIGATION RESULTS:")
    print("=" * 30)
    print(f"✅ WebSocket Working: {ws_success}")
    print(f"✅ API Endpoint Found: {api_endpoint or 'None'}")
    
    if ws_success:
        print(f"\n🎯 RECOMMENDATION: Use WebSocket for real-time data")
        print(f"   URL: wss://api.picktheodds.app/graphql")
        print(f"   Protocol: graphql-transport-ws")
    elif api_endpoint:
        print(f"\n🎯 RECOMMENDATION: Use API endpoint {api_endpoint}")
    else:
        print(f"\n🎯 RECOMMENDATION: Optimize current DOM scraping")

if __name__ == "__main__":
    main()
