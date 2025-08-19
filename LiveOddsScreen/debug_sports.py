#!/usr/bin/env python3
"""
Debug script to test sports selection loading
"""

import json
from pathlib import Path

def test_sports_loading():
    """Test what sports selections are being loaded."""
    print("=== SPORTS SELECTION DEBUG ===")
    
    # Check main sports selection file
    main_file = Path("sports_selection.json")
    if main_file.exists():
        print(f"✅ Main file exists: {main_file}")
        try:
            data = json.loads(main_file.read_text(encoding="utf-8"))
            selections = data.get("selections", [])
            print(f"   Selections: {selections}")
        except Exception as e:
            print(f"   Error reading: {e}")
    else:
        print(f"❌ Main file missing: {main_file}")
    
    # Check test file
    test_file = Path("sports_selection_test.json")
    if test_file.exists():
        print(f"⚠️  Test file exists: {test_file}")
        try:
            data = json.loads(test_file.read_text(encoding="utf-8"))
            selections = data.get("selections", [])
            print(f"   Selections: {selections}")
        except Exception as e:
            print(f"   Error reading: {e}")
    else:
        print(f"✅ Test file missing: {test_file}")
    
    # Check if there are other sports selection files
    all_files = list(Path(".").glob("*sports*selection*.json"))
    print(f"\nAll sports selection files: {[f.name for f in all_files]}")
    
    # Test the selection loading function
    try:
        from plive_dom_scraper import get_plive_paths_for_selections
        
        if main_file.exists():
            data = json.loads(main_file.read_text(encoding="utf-8"))
            selections = data.get("selections", [])
            print(f"\n=== TESTING PLIVE PATH MAPPING ===")
            print(f"Input selections: {selections}")
            paths = get_plive_paths_for_selections(selections)
            print(f"Output paths: {paths}")
        
    except Exception as e:
        print(f"Error testing PLive mapping: {e}")

if __name__ == "__main__":
    test_sports_loading()
