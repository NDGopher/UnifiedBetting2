#!/usr/bin/env python3

import requests
import json

def check_pinnacle_odds():
    event_id = "1610163843"  # Tampa Bay vs Atlanta game
    
    print(f"Checking Pinnacle odds for event {event_id}")
    
    # Try to fetch from Pinnacle API
    url = f"https://guest.api.arcadia.pinnacle.com/0.1/events/{event_id}"
    params = {"brandId": "0"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Raw Pinnacle data structure:")
            print(json.dumps(data, indent=2)[:1000] + "...")
            
            # Look for spreads data
            if 'data' in data and 'periods' in data['data']:
                periods = data['data']['periods']
                if 'num_0' in periods:  # Full game
                    full_game = periods['num_0']
                    if 'spreads' in full_game:
                        spreads = full_game['spreads']
                        print(f"\nSpreads data:")
                        for spread_id, spread_data in spreads.items():
                            print(f"  Spread {spread_id}: {spread_data}")
                    else:
                        print("No spreads data found")
                else:
                    print("No full game period found")
            else:
                print("Unexpected data structure")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error fetching Pinnacle odds: {e}")

if __name__ == "__main__":
    check_pinnacle_odds()

