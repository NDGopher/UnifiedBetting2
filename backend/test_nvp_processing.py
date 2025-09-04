#!/usr/bin/env python3

import requests
import json
from utils.pod_utils import process_event_odds_for_display, decimal_to_american

def test_nvp_processing():
    event_id = "1610163843"  # Tampa Bay vs Atlanta game
    
    print(f"Testing NVP processing for event {event_id}")
    
    # Fetch from Swordfish API
    url = f"https://swordfish-production.up.railway.app/events/{event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            raw_data = response.json()
            print(f"Raw Swordfish data for spreads:")
            
            # Show raw spreads data
            periods = raw_data.get('data', {}).get('periods', {})
            if 'num_0' in periods:
                spreads = periods['num_0'].get('spreads', {})
                print(f"Raw spreads:")
                for spread_key, spread_data in spreads.items():
                    if spread_key in ['2.0', '-2.0']:  # Focus on the spreads we care about
                        print(f"  {spread_key}: {spread_data}")
            
            # Process the data
            processed_data = process_event_odds_for_display(raw_data)
            
            print(f"\nProcessed data for spreads:")
            periods = processed_data.get('data', {}).get('periods', {})
            if 'num_0' in periods:
                spreads = periods['num_0'].get('spreads', {})
                print(f"Processed spreads:")
                for spread_key, spread_data in spreads.items():
                    if spread_key in ['2.0', '-2.0']:  # Focus on the spreads we care about
                        print(f"  {spread_key}: {spread_data}")
                        if 'nvp_home' in spread_data:
                            print(f"    NVP Home: {spread_data['nvp_home']} (American: {decimal_to_american(spread_data['nvp_home'])})")
                        if 'nvp_away' in spread_data:
                            print(f"    NVP Away: {spread_data['nvp_away']} (American: {decimal_to_american(spread_data['nvp_away'])})")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nvp_processing()

