#!/usr/bin/env python3
"""
Force cleanup of expired events
"""

import time
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def force_cleanup_expired_events():
    """Force cleanup of expired events"""
    print("=== Force Cleanup Expired Events ===")
    
    try:
        from main import pod_event_manager, broadcast_pod_alert_safe
        
        active_events = pod_event_manager.get_active_events()
        current_time = time.time()
        expired_count = 0
        
        print(f"Current time: {datetime.fromtimestamp(current_time)}")
        print(f"Total active events: {len(active_events)}")
        
        for event_id, event_data in active_events.items():
            try:
                alert_age = current_time - event_data.get("alert_arrival_timestamp", 0)
                markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
                
                print(f"\n--- Checking Event {event_id} ---")
                print(f"  Age: {alert_age:.1f} seconds")
                
                # Check if all markets have negative EV
                all_negative_ev = True
                if markets:
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
                
                # Check if event should be expired
                expiry_time = 60 if all_negative_ev else 180
                time_until_expiry = expiry_time - alert_age
                
                print(f"  Expiry time: {expiry_time} seconds")
                print(f"  Time until expiry: {time_until_expiry:.1f} seconds")
                
                if time_until_expiry <= 0:
                    print(f"  ❌ EVENT SHOULD BE EXPIRED - REMOVING!")
                    try:
                        pod_event_manager.remove_active_event(event_id, broadcast_pod_alert_safe)
                        expired_count += 1
                        print(f"  ✅ Successfully removed event {event_id}")
                    except Exception as e:
                        print(f"  ❌ Failed to remove event {event_id}: {e}")
                else:
                    print(f"  ✅ Event is still active")
                    
            except Exception as e:
                print(f"  ❌ Error checking event {event_id}: {e}")
        
        print(f"\n=== Cleanup Complete ===")
        print(f"Removed {expired_count} expired events")
        print(f"Remaining events: {len(pod_event_manager.get_active_events())}")
        
    except Exception as e:
        print(f"Error in force cleanup: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print(f"=== Force Cleanup - {datetime.now()} ===")
    force_cleanup_expired_events()
    print("\n=== Cleanup Complete ===")

if __name__ == "__main__":
    main() 