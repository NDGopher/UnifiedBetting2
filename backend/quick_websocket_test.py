#!/usr/bin/env python3
"""
Quick WebSocket test to check message format
"""

import websocket
import json
import time
import threading
from datetime import datetime

def on_message(ws, message):
    """Handle incoming WebSocket messages"""
    try:
        data = json.loads(message)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if data.get("type") == "pod_alert":
            print(f"[{timestamp}] POD ALERT MESSAGE:")
            print(f"  Raw message: {message[:200]}...")
            print(f"  Keys: {list(data.keys())}")
            print(f"  eventId: {data.get('eventId', 'NOT_FOUND')}")
            print(f"  eventid: {data.get('eventid', 'NOT_FOUND')}")
            print(f"  Event title: {data.get('event', {}).get('title', 'N/A')}")
            print("  ---")
        
    except Exception as e:
        print(f"Error parsing message: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connected!")

def main():
    print("=== Quick WebSocket Test ===")
    print("Connecting to WebSocket...")
    
    ws = websocket.WebSocketApp(
        "ws://localhost:5001/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run in a separate thread
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Monitor for 30 seconds
    print("Monitoring for 30 seconds...")
    time.sleep(30)
    
    ws.close()
    print("Test complete!")

if __name__ == "__main__":
    main() 