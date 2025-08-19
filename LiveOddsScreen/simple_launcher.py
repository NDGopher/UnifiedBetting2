#!/usr/bin/env python3
"""
Simple launcher that just runs the sports selector
"""

import sys
import json
from pathlib import Path

def run_sports_selector():
    """Run just the sports selector"""
    try:
        print("Loading sports selector...")
        import sports_selector
        from sports_selector import main as selector_main
        
        # Clear any existing selection
        try:
            Path("sports_selection.json").unlink(missing_ok=True)
        except:
            pass
        
        print("Starting sports selector GUI...")
        selector_main()
        
        # Check if selection was made
        try:
            with open("sports_selection.json", "r") as f:
                data = json.load(f)
            
            selections = data.get("selections", [])
            if selections:
                print(f"\n✅ SUCCESS! You selected: {selections}")
                print("✅ Selection saved to sports_selection.json")
                return True
            else:
                print("\n❌ No selections made")
                return False
                
        except Exception as e:
            print(f"\n❌ Error reading selections: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error running sports selector: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎮 Live Odds Screen - Sports Selector")
    print("=" * 40)
    
    success = run_sports_selector()
    
    if success:
        print("\n🎉 SPORTS SELECTION COMPLETE!")
        print("Your selections have been saved.")
        print("The system is now ready for live odds comparison.")
        print("\nNext steps:")
        print("1. Check your selections in sports_selection.json")
        print("2. The main system can now read your preferences")
    else:
        print("\n⚠️ SPORTS SELECTION FAILED")
        print("Please try running the selector again.")
    
    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()
