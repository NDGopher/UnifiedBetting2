#!/usr/bin/env python3
"""
Test script for PLive scraper with dynamic sport discovery
"""

import json
from pathlib import Path
from plive_dom_scraper_clean import scrape_plive_odds_with_driver, open_plive_driver, discover_plive_sports, get_plive_paths_for_selections

def test_plive_scraping():
    """Test PLive scraping directly."""
    print("=== TESTING PLIVE SCRAPER ===")
    
    # Test with our updated selectors
    selectors = {
        "event_row_selector": "div.event-list__item__details__container",
        "home_team_selector": "div.event-list__item__details__teams__team__container:first-child p[data-testid='top-team-details']",
        "away_team_selector": "div.event-list__item__details__teams__team__container:last-child p[data-testid='bottom-team-details']",
        "moneyline_selector": "div.offerings.market--two-row.market-3",
        "spread_selector": "div.offerings.market--two-row.market-6", 
        "total_selector": "div.offerings.market--two-row.market-5",
        "price_selector": "div.odds div.odd span.emphasis.pane"
    }
    
    print("Selectors:", json.dumps(selectors, indent=2))
    
    try:
        # Open a driver
        print("Opening PLive driver...")
        driver = open_plive_driver(
            user_data_dir=r"C:\Users\steph\AppData\Local\PTO_Chrome_Profile",
            profile_dir="Profile 1",
            headless=False  # Not headless so we can see what's happening
        )
        
        # Test dynamic sport discovery
        print("\n=== TESTING DYNAMIC SPORT DISCOVERY ===")
        discovered_sports = discover_plive_sports(driver)
        print(f"Discovered {len(discovered_sports)} sports:")
        for sport, url in discovered_sports.items():
            print(f"  {sport} -> {url}")
        
        # Test sport path mapping with discovered sports
        print("\n=== TESTING SPORT PATH MAPPING ===")
        test_selections = ["mlb:moneyline", "nfl:spread", "basketball:total"]
        paths = get_plive_paths_for_selections(test_selections, driver=driver)
        print(f"Paths for {test_selections}: {paths}")
        
        # Test scraping MLB only
        print("\n=== TESTING MLB SCRAPING ===")
        events = scrape_plive_odds_with_driver(
            driver, 
            sports_paths=["#!/sport/1"],  # MLB only
            selectors=selectors
        )
        
        print(f"Scraped {len(events)} events:")
        for i, event in enumerate(events):
            print(f"  Event {i+1}: {event.get('home')} vs {event.get('away')} ({event.get('sport')})")
            print(f"    Odds: {event.get('books', {}).get('plive', {})}")
        
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plive_scraping()
