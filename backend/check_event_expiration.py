#!/usr/bin/env python3
"""
Check event expiration status and current state
"""

import time
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_event_expiration():
    """Check the expiration status of all active events"""
    print("=== Event Expiration Analysis ===")
    
    try:
        from main import pod_event_manager
        
        active_events = pod_event_manager.get_active_events()
        current_time = time.time()
        
        print(f"Current time: {datetime.fromtimestamp(current_time)}")
        print(f"Total active events: {len(active_events)}")
        
        if not active_events:
            print("No active events found")
            return
        
        for event_id, event_data in active_events.items():
            print(f"\n--- Event {event_id} ---")
            
            if not isinstance(event_data, dict):
                print(f"  ❌ Event data is not a dictionary")
                continue
            
            # Check alert arrival time
            alert_timestamp = event_data.get("alert_arrival_timestamp", 0)
            alert_age = current_time - alert_timestamp
            
            print(f"  Alert arrival: {datetime.fromtimestamp(alert_timestamp)}")
            print(f"  Age: {alert_age:.1f} seconds")
            
            # Check markets and EV
            markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
            print(f"  Markets count: {len(markets)}")
            
            if markets:
                all_negative_ev = True
                ev_values = []
                
                for market in markets:
                    ev_str = market.get("ev", "0")
                    try:
                        ev_value = float(ev_str.replace('%', ''))
                        ev_values.append(ev_value)
                        if ev_value > 0:
                            all_negative_ev = False
                    except:
                        ev_values.append(0)
                
                print(f"  EV values: {ev_values}")
                print(f"  All negative EV: {all_negative_ev}")
                
                # Calculate expiration
                expiry_time = 60 if all_negative_ev else 180
                time_until_expiry = expiry_time - alert_age
                
                print(f"  Expiry time: {expiry_time} seconds")
                print(f"  Time until expiry: {time_until_expiry:.1f} seconds")
                
                if time_until_expiry <= 0:
                    print(f"  ❌ EVENT SHOULD BE EXPIRED!")
                elif all_negative_ev and alert_age > 60:
                    print(f"  ⚠ Negative EV event older than 60s - should skip updates")
                else:
                    print(f"  ✅ Event is still active")
            else:
                print(f"  ❌ No markets found")
            
            # Check if event is being updated
            last_update = event_data.get("last_update", 0)
            if last_update > 0:
                update_age = current_time - last_update
                print(f"  Last update: {datetime.fromtimestamp(last_update)}")
                print(f"  Update age: {update_age:.1f} seconds")
            else:
                print(f"  No last_update timestamp found")
    
    except Exception as e:
        print(f"Error checking event expiration: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print(f"=== Event Expiration Check - {datetime.now()} ===")
    check_event_expiration()
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    main() 