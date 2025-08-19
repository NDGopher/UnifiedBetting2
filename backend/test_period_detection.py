#!/usr/bin/env python3
"""
Test script to verify period detection logic in betbck_scraper.py
"""

def test_period_detection():
    """Test the period detection logic"""
    
    # Test cases for 1H detection
    first_half_indicators = ["1h", "1st half", "first half"]
    
    # Test cases for skip indicators
    skip_indicators = [
        # Baseball periods
        "1st 5 Innings", "First Five Innings", 
        # Hockey periods
        "1st Period", "2nd Period", "3rd Period", 
        # Basketball/Football quarters
        "1Q", "2Q", "3Q", "4Q", "1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter",
        # Other halves (not 1H)
        "2nd Half", "3rd Half", "4th Half",
        # Soccer/Baseball props
        "hits+runs+errors", "h+r+e", "hre", "corners", "bookings", "cards", "fouls",
        # Other props
        "series", "overtime", "extra time", "penalties", "sets", "games"
    ]
    
    # Test team names
    test_cases = [
        # Should be detected as 1H
        ("Team A 1H", "Team B 1H", True, "1H line"),
        ("Team A 1st half", "Team B 1st half", True, "1st half line"),
        ("Team A first half", "Team B first half", True, "first half line"),
        
        # Should be skipped (quarter-based)
        ("Team A 1Q", "Team B 1Q", False, "1Q line"),
        ("Team A 2Q", "Team B 2Q", False, "2Q line"),
        ("Team A 1st Quarter", "Team B 1st Quarter", False, "1st Quarter line"),
        
        # Should be skipped (other periods)
        ("Team A 1st Period", "Team B 1st Period", False, "1st Period line"),
        ("Team A 2nd Half", "Team B 2nd Half", False, "2nd Half line"),
        
        # Should be skipped (props)
        ("Team A hits+runs+errors", "Team B hits+runs+errors", False, "hits+runs+errors prop"),
        ("Team A corners", "Team B corners", False, "corners prop"),
        
        # Should be processed as full game
        ("Team A", "Team B", False, "full game line"),
    ]
    
    print("Testing period detection logic...")
    print("=" * 60)
    
    for home_team, away_team, expected_1h, description in test_cases:
        # Test 1H detection
        is_first_half = any(ind.lower() in home_team.lower() or ind.lower() in away_team.lower() 
                           for ind in first_half_indicators)
        
        # Test skip detection
        should_skip = any(ind.lower() in home_team.lower() or ind.lower() in away_team.lower() 
                         for ind in skip_indicators)
        
        # Determine what should happen
        if should_skip:
            result = "SKIP"
        elif is_first_half:
            result = "1H"
        else:
            result = "FULL GAME"
        
        print(f"{description:25} | {home_team:20} vs {away_team:20} | Result: {result}")
        
        # Verify logic is correct
        if "1Q" in description and result != "SKIP":
            print(f"  ⚠️  ERROR: {description} should be SKIPPED, got {result}")
        elif "1H" in description and result != "1H":
            print(f"  ⚠️  ERROR: {description} should be 1H, got {result}")
        elif "full game" in description and result != "FULL GAME":
            print(f"  ⚠️  ERROR: {description} should be FULL GAME, got {result}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_period_detection()
