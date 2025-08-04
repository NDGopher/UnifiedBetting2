#!/usr/bin/env python3
"""
Manual refresh debug script
"""

import time
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_refresher_status():
    """Check the current refresher status"""
    print("=== Refresher Status Check ===")
    
    try:
        import requests
        
        response = requests.get("http://localhost:5001/refresher-status")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Refresher running: {data.get('refresher_running')}")
            print(f"Thread alive: {data.get('thread_alive')}")
            print(f"Active events count: {data.get('active_events_count')}")
            print(f"Active event IDs: {data.get('active_event_ids')}")
            print(f"Refresher interval: {data.get('refresher_interval_seconds')} seconds")
            return data
        else:
            print(f"Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error checking refresher status: {e}")
        return None

def check_event_details():
    """Check details of active events"""
    print("\n=== Event Details Check ===")
    
    try:
        import requests
        
        response = requests.get("http://localhost:5001/get_active_events_data")
        if response.status_code == 200:
            events = response.json()
            print(f"Total events from API: {len(events)}")
            
            for event_id, event_data in events.items():
                print(f"\n--- Event {event_id} ---")
                print(f"  Title: {event_data.get('title')}")
                print(f"  Last update: {event_data.get('last_update')}")
                print(f"  Alert arrival: {event_data.get('alert_arrival_timestamp')}")
                
                # Calculate age
                current_time = time.time()
                alert_age = current_time - event_data.get('alert_arrival_timestamp', 0)
                print(f"  Age: {alert_age:.1f} seconds")
                
                # Check markets
                markets = event_data.get('markets', [])
                print(f"  Markets count: {len(markets)}")
                
                if markets:
                    # Check EV values
                    ev_values = []
                    all_negative = True
                    for market in markets:
                        ev_str = market.get('ev', '0')
                        try:
                            ev_value = float(ev_str.replace('%', ''))
                            ev_values.append(ev_value)
                            if ev_value > 0:
                                all_negative = False
                        except:
                            ev_values.append(0)
                    
                    print(f"  EV values: {ev_values}")
                    print(f"  All negative EV: {all_negative}")
                    
                    # Check if should be expired
                    expiry_time = 60 if all_negative else 180
                    time_until_expiry = expiry_time - alert_age
                    print(f"  Time until expiry: {time_until_expiry:.1f} seconds")
                    
                    if time_until_expiry <= 0:
                        print(f"  ❌ EVENT SHOULD BE EXPIRED!")
                    elif all_negative and alert_age > 60:
                        print(f"  ⚠ Should skip updates (negative EV, >60s old)")
                    else:
                        print(f"  ✅ Event is active and should update")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error checking event details: {e}")

def test_manual_refresh():
    """Test manual refresh trigger"""
    print("\n=== Testing Manual Refresh ===")
    
    try:
        import requests
        
        # Trigger manual refresh
        response = requests.post("http://localhost:5001/refresher/start")
        if response.status_code == 200:
            print("Manual refresh triggered successfully")
        else:
            print(f"Error triggering manual refresh: {response.status_code}")
            
    except Exception as e:
        print(f"Error testing manual refresh: {e}")

def main():
    """Main function"""
    print(f"=== Manual Refresh Debug - {datetime.now()} ===")
    
    # Check refresher status
    status = check_refresher_status()
    
    # Check event details
    check_event_details()
    
    # Test manual refresh
    test_manual_refresh()
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main() 