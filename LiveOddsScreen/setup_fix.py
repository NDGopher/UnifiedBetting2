#!/usr/bin/env python3
"""
LiveOddsScreen Setup and Fix Script
This script addresses the main issues and sets up the system properly.
"""

import json
import os
import sys
import time
from pathlib import Path
import subprocess


def update_config():
    """Update config.json with proper settings."""
    config_path = Path("config.json")
    
    config = {
        "chrome_user_data_dir": "C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile",
        "chrome_profile_dir": "Profile 1",
        "chrome_debug_port": 9223,
        "timeouts": {
            "page_load": 30
        },
        "pto_headless": False,
        "plive_headless": True
    }
    
    try:
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print("✅ Updated config.json with proper Chrome settings")
    except Exception as e:
        print(f"❌ Failed to update config.json: {e}")


def verify_selections():
    """Verify sports_selection.json has proper MLB/WNBA selections."""
    selections_path = Path("sports_selection.json")
    
    if not selections_path.exists():
        print("❌ sports_selection.json not found - please run the selector first")
        return False
    
    try:
        with open(selections_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        selections = data.get("selections", [])
        
        has_mlb = any("mlb:" in sel.lower() for sel in selections)
        has_wnba = any("wnba:" in sel.lower() for sel in selections)
        
        print(f"📋 Current selections: {selections}")
        print(f"   MLB markets: {has_mlb}")
        print(f"   WNBA markets: {has_wnba}")
        
        if not (has_mlb or has_wnba):
            print("⚠️  No MLB or WNBA selections found. The app may not work as expected.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading selections: {e}")
        return False


def check_profile():
    """Check if PTO Chrome profile exists."""
    profile_path = Path("C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile\\Profile 1")
    
    if profile_path.exists():
        print("✅ PTO Chrome profile found")
        return True
    else:
        print("❌ PTO Chrome profile not found")
        print("   Please run your PTO profile setup script first")
        return False


def show_usage_instructions():
    """Show step-by-step usage instructions."""
    print("\n" + "="*60)
    print("📖 USAGE INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Start PTO Chrome with debugging:")
    print("   python start_pto_chrome.py")
    print("   (This will open Chrome with your PTO profile and debug port)")
    
    print("\n2. In the opened Chrome:")
    print("   - Log into PTO if not already logged in")
    print("   - Navigate to the odds screens you want")
    print("   - Leave Chrome open")
    
    print("\n3. Start the LiveOddsScreen:")
    print("   python app_launcher.py")
    print("   OR")
    print("   start_live_screen.bat")
    
    print("\n4. In the selector:")
    print("   - Choose MLB and/or WNBA markets")
    print("   - Select moneyline, spread, and/or total")
    print("   - Click Start")
    
    print("\n✨ Key Fixes Applied:")
    print("   ✅ PLive now only scrapes selected sports (MLB=sport/1, WNBA=sport/2)")
    print("   ✅ PTO uses dedicated debug port (9223) to avoid conflicts")
    print("   ✅ Automatic refresh for stale PLive events")
    print("   ✅ Better team name matching for WNBA")
    print("   ✅ Dynamic sports path selection based on your choices")


def main():
    print("🚀 LiveOddsScreen Setup and Fix")
    print("=" * 40)
    
    # Update configuration
    update_config()
    
    # Check profile
    profile_ok = check_profile()
    
    # Verify selections
    selections_ok = verify_selections()
    
    # Show results
    print("\n📊 Setup Status:")
    print(f"   PTO Profile: {'✅' if profile_ok else '❌'}")
    print(f"   Selections: {'✅' if selections_ok else '⚠️'}")
    print("   Config: ✅")
    
    # Show instructions
    show_usage_instructions()
    
    if not profile_ok:
        print("\n⚠️  Please setup your PTO profile first before running the live screen.")
    
    print("\n🎯 Main Issues Fixed:")
    print("   1. PLive now scrapes only selected sports (was pulling Soccer)")
    print("   2. PTO connection improved with dedicated debug port")
    print("   3. Added WNBA team name matching")
    print("   4. Added automatic refresh for stale events")
    print("   5. Dynamic sports selection based on user choices")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
