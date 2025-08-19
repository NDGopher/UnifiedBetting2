#!/usr/bin/env python3
"""
Clean system test without emoji issues
"""

import json
import sys
from pathlib import Path

# Import the sports mapping
try:
    from plive_dom_scraper import PLIVE_SPORT_PATHS, get_plive_paths_for_selections
except ImportError:
    print("ERROR: Cannot import PLive modules")
    PLIVE_SPORT_PATHS = {}
    def get_plive_paths_for_selections(selections):
        return ["#!/sport/1"]

def test_config_loading():
    """Test configuration file loading."""
    print("[Test] === CONFIG LOADING TEST ===")
    
    config_files = ["config.json", "selectors.json", "sports_selection.json"]
    
    for config_file in config_files:
        path = Path(config_file)
        print(f"[Test] Checking {config_file}:")
        print(f"[Test]   Exists: {path.exists()}")
        
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"[Test]   Valid JSON: SUCCESS")
                print(f"[Test]   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except Exception as e:
                print(f"[Test]   JSON Error: {e}")
        else:
            print(f"[Test]   Status: Missing")
    
    print("[Test] === END CONFIG LOADING TEST ===\n")

def test_chrome_profile():
    """Test Chrome profile accessibility."""
    print("[Test] === CHROME PROFILE TEST ===")
    
    profile_base = Path("C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile")
    profile_dir = profile_base / "Profile 1"
    
    print(f"[Test] Profile base: {profile_base}")
    print(f"[Test] Base exists: {profile_base.exists()}")
    print(f"[Test] Profile dir: {profile_dir}")
    print(f"[Test] Profile exists: {profile_dir.exists()}")
    
    if profile_dir.exists():
        key_files = ["Preferences", "History", "Cookies"]
        for key_file in key_files:
            file_path = profile_dir / key_file
            print(f"[Test]   {key_file}: {file_path.exists()}")
    
    print("[Test] === END CHROME PROFILE TEST ===\n")

def test_sports_mapping():
    """Test sports mapping functionality."""
    print("[Test] === SPORTS MAPPING TEST ===")
    
    test_cases = [
        ["mlb:moneyline", "mlb:spread"],
        ["wnba:moneyline", "wnba:total"],
        ["invalid:test"],
        []
    ]
    
    for selections in test_cases:
        print(f"[Test] Testing selections: {selections}")
        paths = get_plive_paths_for_selections(selections)
        print(f"[Test] Result paths: {paths}")
    
    print("[Test] === END SPORTS MAPPING TEST ===\n")

def create_test_selection_file():
    """Create test selection file."""
    print("[Test] === CREATING TEST SELECTION FILE ===")
    
    test_selections = {
        "selections": [
            "mlb:moneyline",
            "mlb:spread",
            "mlb:total", 
            "wnba:moneyline",
            "wnba:spread",
            "wnba:total"
        ],
        "opts": {
            "open_browser": "embedded",
            "pto_headless": False,
            "chrome_debug_port": 9223
        }
    }
    
    try:
        with open("sports_selection_test.json", 'w', encoding='utf-8') as f:
            json.dump(test_selections, f, indent=2)
        print("[Test] SUCCESS: Created sports_selection_test.json")
    except Exception as e:
        print(f"[Test] ERROR: Failed to create test file: {e}")
    
    print("[Test] === END CREATING TEST SELECTION FILE ===\n")

def main():
    print("LiveOddsScreen System Test")
    print("=" * 50)
    
    test_config_loading()
    test_chrome_profile()
    test_sports_mapping()
    create_test_selection_file()
    
    print("[Test] === SYSTEM TEST COMPLETE ===")
    print("[Test] If everything looks good, run: LIVE_ODDS_SCREEN.bat")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
