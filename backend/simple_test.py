#!/usr/bin/env python3
"""
Simple test script to verify POD alerts system
"""

import requests
import json
import time

def test_system():
    base_url = "http://localhost:5001"
    
    print("=== POD Alerts System Test ===")
    
    # Test 1: Backend connectivity
    print("\n1. Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend is running: {data.get('message')}")
            print(f"  Active events: {data.get('active_events_count')}")
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Backend connection failed: {e}")
        return
    
    # Test 2: Refresher status
    print("\n2. Testing refresher status...")
    try:
        response = requests.get(f"{base_url}/refresher-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Refresher status: {data.get('status')}")
            print(f"  Thread alive: {data.get('thread_alive')}")
            print(f"  Active events: {data.get('active_events_count')}")
            print(f"  Interval: {data.get('refresher_interval_seconds')} seconds")
        else:
            print(f"✗ Refresher status failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Refresher status check failed: {e}")
    
    # Test 3: Active events
    print("\n3. Testing active events...")
    try:
        response = requests.get(f"{base_url}/get_active_events_data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get("data", {})
            print(f"✓ Active events endpoint working")
            print(f"  Events returned: {len(events)}")
            if events:
                for event_id, event_data in events.items():
                    print(f"    Event ID: {event_id}")
                    print(f"    Title: {event_data.get('title', 'N/A')}")
                    print(f"    Markets: {len(event_data.get('markets', []))}")
            else:
                print("  No active events (this is normal if no alerts have been processed)")
        else:
            print(f"✗ Active events failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Active events check failed: {e}")
    
    # Test 4: Simulate POD alert
    print("\n4. Testing POD alert simulation...")
    test_alert = {
        "eventId": "test_event_456",
        "homeTeam": "Test Home Team",
        "awayTeam": "Test Away Team",
        "sport": "Test Sport",
        "betDescription": "Test Bet Description",
        "oldOdds": "+150",
        "newOdds": "+140",
        "noVigPriceFromAlert": "+145",
        "ev": "2.5"
    }
    
    try:
        response = requests.post(f"{base_url}/pod_alert", json=test_alert, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ POD alert simulation response: {data.get('status')}")
            print(f"  Message: {data.get('message', 'N/A')}")
        else:
            print(f"✗ POD alert simulation failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ POD alert simulation failed: {e}")
    
    # Test 5: Check if event was created
    print("\n5. Checking if event was created...")
    time.sleep(2)  # Wait for processing
    try:
        response = requests.get(f"{base_url}/get_active_events_data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get("data", {})
            test_event = events.get("test_event_456")
            if test_event:
                print(f"✓ Test event was created successfully!")
                print(f"  Title: {test_event.get('title', 'N/A')}")
                print(f"  Markets: {len(test_event.get('markets', []))}")
                print(f"  Last Update: {test_event.get('last_update', 'N/A')}")
            else:
                print("⚠ Test event was not created (this might indicate processing issues)")
        else:
            print(f"✗ Failed to check events: {response.status_code}")
    except Exception as e:
        print(f"✗ Event check failed: {e}")
    
    print("\n=== Test Complete ===")
    print("\nNext steps:")
    print("1. If test event was created, monitor it for background refreshes")
    print("2. Check backend console logs for [BackgroundRefresher] messages")
    print("3. If no test event was created, check backend logs for processing errors")

if __name__ == "__main__":
    test_system() 