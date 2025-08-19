#!/usr/bin/env python3
"""
Clean version of run_live_screen.py without indentation issues
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import threading

def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def read_selection_keys(sel_file: Path) -> List[str]:
    try:
        raw = json.loads(sel_file.read_text(encoding="utf-8"))
    except Exception:
        return []
    
    if isinstance(raw, dict):
        arr = raw.get("selections")
        if isinstance(arr, list):
            return [str(x) for x in arr]
    
    return []

def serve_dashboard(initial_data: List[Dict], port: int = 8765):
    """Start dashboard server in background thread"""
    def start_server():
        try:
            from dashboard_simple import serve_dashboard_sync
            serve_dashboard_sync(initial_data, port)
        except Exception as e:
            print(f"[Dashboard] Error: {e}")
    
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    time.sleep(2)  # Give server time to start

def main():
    print("[Init] Starting Live Odds Screen...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--selectors", default="selectors.json") 
    parser.add_argument("--refresh", type=float, default=0.5)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    
    print(f"[Init] Command line args: {vars(args)}")
    
    # Load configuration
    print("[Config] Loading configuration files...")
    cfg = load_json(args.config)
    sels = load_json(args.selectors)
    
    print(f"[Config] Loaded config: {list(cfg.keys())}")
    print(f"[Config] Loaded selectors: {list(sels.keys())}")
    
    # Start dashboard
    print(f"[Init] Starting dashboard on port {args.port}...")
    serve_dashboard([], port=args.port)
    print(f"[Dashboard] Dashboard available at http://127.0.0.1:{args.port}/dashboard.html")
    
    # Check for selections
    sel_file = Path("sports_selection.json")
    if not sel_file.exists():
        print("[Error] No sports_selection.json found!")
        print("[Error] Please run LIVE_ODDS_SCREEN.bat first to select sports.")
        return 1
    
    selections = read_selection_keys(sel_file)
    print(f"[Config] Found selections: {selections}")
    
    if not selections:
        print("[Error] No selections found in sports_selection.json")
        return 1
    
    # Speed settings
    speed_mode = cfg.get("speed_mode", False)
    fast_refresh = cfg.get("fast_refresh", 0.1) if speed_mode else args.refresh
    actual_refresh = fast_refresh if speed_mode else args.refresh
    
    print(f"[Speed] Speed mode: {speed_mode}, Refresh rate: {actual_refresh}s")
    
    # Main loop placeholder
    print("[System] Live odds system would start here...")
    print("[System] This is a simplified version - main system needs indentation fixes")
    print(f"[System] Selected sports: {selections}")
    print(f"[System] Dashboard URL: http://127.0.0.1:{args.port}/dashboard.html")
    
    # Simple loop to keep dashboard running
    try:
        print("[System] Press Ctrl+C to stop...")
        cycle = 0
        while True:
            cycle += 1
            print(f"[System] Cycle {cycle} - Dashboard running (simplified mode)")
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n[System] Stopping Live Odds Screen...")
        return 0

if __name__ == "__main__":
    exit(main())
