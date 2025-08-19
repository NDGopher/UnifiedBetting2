#!/usr/bin/env python3
"""
Simple script to enable WebSocket mode
"""

import json

def enable_websocket_mode():
    """Enable WebSocket mode in config"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        config["use_websocket"] = True
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ WebSocket mode ENABLED")
        print("Next run will use WebSocket for real-time PTO data")
        
    except Exception as e:
        print(f"❌ Error enabling WebSocket: {e}")

def disable_websocket_mode():
    """Disable WebSocket mode in config"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        config["use_websocket"] = False
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("❌ WebSocket mode DISABLED")
        print("Next run will use DOM scraping for PTO data")
        
    except Exception as e:
        print(f"❌ Error disabling WebSocket: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['off', 'disable', 'false']:
        disable_websocket_mode()
    else:
        enable_websocket_mode()
