#!/usr/bin/env python3
"""
Comprehensive test script for LiveOddsScreen system.
This will test all components and provide detailed diagnostics.
"""

import json
import sys
import time
from pathlib import Path
from plive_dom_scraper import get_plive_paths_for_selections, PLIVE_SPORT_PATHS


def test_sports_mapping():
   """Test the sports mapping functionality."""
   print(" [Test] === SPORTS MAPPING TEST ===")
   
   test_cases = [
   ["mlb:moneyline", "mlb:spread"],
   ["wnba:moneyline", "wnba:total"],
   ["epl:moneyline", "la_liga:spread"],
   ["nfl:spread", "nhl:total"],
   ["mls:moneyline"],
   ["invalid:test"],
   []
   ]
   
       for selections in test_cases:
        print(f"\n [Test] Testing selections: {selections}")
        paths = get_plive_paths_for_selections(selections)
        print(f" [Test] Result paths: {paths}")
   
   print(" [Test] === END SPORTS MAPPING TEST ===\n")


def test_config_loading():
   """Test configuration file loading."""
   print(" [Test] === CONFIG LOADING TEST ===")
   
   config_files = ["config.json", "selectors.json", "sports_selection.json"]
   
   for config_file in config_files:
   path = Path(config_file)
   print(f" [Test] Checking {config_file}:")
   print(f" [Test]   Exists: {path.exists()}")
   
   if path.exists():
   try:
   with open(path, 'r', encoding='utf-8') as f:
   data = json.load(f)
   print(f" [Test]   Valid JSON: ")
   print(f" [Test]   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
   except Exception as e:
   print(f" [Test]   JSON Error:  {e}")
   else:
   print(f" [Test]   Status:  Missing")
   
   print(" [Test] === END CONFIG LOADING TEST ===\n")


def test_chrome_profile():
   """Test Chrome profile accessibility."""
   print(" [Test] === CHROME PROFILE TEST ===")
   
   profile_base = Path("C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile")
   profile_dir = profile_base / "Profile 1"
   
   print(f" [Test] Profile base: {profile_base}")
   print(f" [Test] Base exists: {profile_base.exists()}")
   print(f" [Test] Profile dir: {profile_dir}")
   print(f" [Test] Profile exists: {profile_dir.exists()}")
   
   if profile_dir.exists():
   # Check for key Chrome profile files
   key_files = ["Preferences", "History", "Cookies"]
   for key_file in key_files:
   file_path = profile_dir / key_file
   print(f" [Test]   {key_file}: {file_path.exists()}")
   
   print(" [Test] === END CHROME PROFILE TEST ===\n")


def test_plive_mapping_completeness():
   """Test PLive sports mapping completeness."""
   print(" [Test] === PLIVE MAPPING COMPLETENESS ===")
   
   print(f" [Test] Total sports mapped: {len(PLIVE_SPORT_PATHS)}")
   print(" [Test] Available sports:")
   
   by_path = {}
   for sport, path in PLIVE_SPORT_PATHS.items():
   if path not in by_path:
   by_path[path] = []
   by_path[path].append(sport)
   
   for path, sports in sorted(by_path.items()):
   print(f" [Test]   {path}: {', '.join(sports)}")
   
   print(" [Test] === END PLIVE MAPPING COMPLETENESS ===\n")


def create_test_selection_file():
   """Create a test selection file for debugging."""
   print(" [Test] === CREATING TEST SELECTION FILE ===")
   
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
   print(" [Test]  Created sports_selection_test.json")
   print(f" [Test] Content: {test_selections}")
   except Exception as e:
   print(f" [Test]  Failed to create test file: {e}")
   
   print(" [Test] === END CREATING TEST SELECTION FILE ===\n")


def show_debug_instructions():
   """Show debugging instructions."""
   print(" [Debug] === DEBUGGING INSTRUCTIONS ===")
   print("""
 To debug the system:

1. Run this test script first:
   python test_system.py

2. Start PTO Chrome with debugging:
   python start_pto_chrome.py

3. Launch the system with extensive logging:
   start_live_screen.bat

4. Look for these debug markers in the output:
   [Init] - Initialization
   [Config] - Configuration loading  
   [Browser] - Chrome profile setup
   [PTO] - PTO driver and scraping
   [PLive-Debug] - PLive selection analysis
   [PLive] - PLive scraping cycles
   [Merge] - Data matching

5. Key things to check:
   - Are your selections being read correctly?
   - Is the PTO driver connecting?
   - Are PLive paths being mapped correctly?
   - Are events being scraped from both sources?
   - Are matches being found?

6. If PTO fails:
   - Check Chrome is running with debug port 9223
   - Verify profile path exists
   - Check for Chrome process conflicts

7. If PLive fails:
   - Check sports mapping in debug output
   - Verify selections file exists
   - Look for driver creation errors

8. If no matches:
   - Check team names in debug output
   - Verify both sources have data
   - Check sport/market alignment
""")
   print(" [Debug] === END DEBUGGING INSTRUCTIONS ===\n")


def main():
   print("LiveOddsScreen System Test")
   print("=" * 50)
   
   test_config_loading()
   test_chrome_profile()
   test_plive_mapping_completeness()
   test_sports_mapping()
   create_test_selection_file()
   show_debug_instructions()
   
   print(" [Test] === SYSTEM TEST COMPLETE ===")
   print(" [Test] Review the output above for any issues.")
   print(" [Test] If everything looks good, run: start_live_screen.bat")
   
   return 0


if __name__ == "__main__":
   sys.exit(main())
