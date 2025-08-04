#!/usr/bin/env python3
"""
Manual Refresh Test Script
This script manually triggers the background refresher and tests the update system.
"""

import requests
import json
import time
import threading
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualRefreshTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def check_refresher_status(self):
        """Check if background refresher is running"""
        try:
            response = requests.get(f"{self.base_url}/refresher-status", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def start_refresher_manually(self):
        """Manually start the background refresher"""
        try:
            response = requests.post(f"{self.base_url}/refresher/start", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_active_events(self):
        """Get current active events"""
        try:
            response = requests.get(f"{self.base_url}/get_active_events_data", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def cleanup_corrupted_events(self):
        """Clean up corrupted events"""
        try:
            response = requests.post(f"{self.base_url}/test/cleanup-corrupted-events", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_background_refresher(self):
        """Test the background refresher functionality"""
        logger.info("=== Manual Background Refresher Test ===")
        
        # Step 1: Check current status
        logger.info("Step 1: Checking current refresher status...")
        status = self.check_refresher_status()
        logger.info(f"Current status: {status}")
        
        # Step 2: Clean up any corrupted events
        logger.info("Step 2: Cleaning up corrupted events...")
        cleanup_result = self.cleanup_corrupted_events()
        logger.info(f"Cleanup result: {cleanup_result}")
        
        # Step 3: Get active events
        logger.info("Step 3: Getting active events...")
        events_result = self.get_active_events()
        if events_result.get("status") == "success":
            events_data = events_result.get("data", {})
            logger.info(f"Active events: {len(events_data)}")
            for event_id, event_data in events_data.items():
                logger.info(f"  Event ID: {event_id}")
                logger.info(f"    Title: {event_data.get('title', 'N/A')}")
                logger.info(f"    Markets: {len(event_data.get('markets', []))}")
                logger.info(f"    Last Update: {event_data.get('last_update', 'N/A')}")
        else:
            logger.warning(f"Could not get active events: {events_result}")
        
        # Step 4: Start refresher if not running
        if status.get("status") != "running":
            logger.info("Step 4: Starting background refresher manually...")
            start_result = self.start_refresher_manually()
            logger.info(f"Start result: {start_result}")
            
            # Wait a moment and check status again
            time.sleep(3)
            status = self.check_refresher_status()
            logger.info(f"Status after manual start: {status}")
        
        # Step 5: Monitor for updates
        logger.info("Step 5: Monitoring for updates (30 seconds)...")
        start_time = time.time()
        initial_events = self.get_active_events()
        
        while time.time() - start_time < 30:
            time.sleep(5)
            current_events = self.get_active_events()
            
            if current_events.get("status") == "success":
                events_data = current_events.get("data", {})
                logger.info(f"Active events at {int(time.time() - start_time)}s: {len(events_data)}")
                
                # Check for updates in existing events
                if initial_events.get("status") == "success":
                    initial_data = initial_events.get("data", {})
                    for event_id in events_data:
                        if event_id in initial_data:
                            initial_event = initial_data[event_id]
                            current_event = events_data[event_id]
                            
                            initial_update = initial_event.get("last_update")
                            current_update = current_event.get("last_update")
                            
                            if initial_update != current_update:
                                logger.info(f"  ✓ Event {event_id} updated: {initial_update} -> {current_update}")
                            else:
                                logger.info(f"  ⚠ Event {event_id} not updated: {current_update}")
        
        logger.info("Test completed!")
    
    def simulate_alert(self):
        """Simulate a POD alert to test the system"""
        logger.info("=== Simulating POD Alert ===")
        
        # Create a test alert payload
        test_alert = {
            "eventId": "test_event_123",
            "homeTeam": "Test Home Team",
            "awayTeam": "Test Away Team",
            "sport": "Test Sport",
            "betDescription": "Test Bet",
            "oldOdds": "+150",
            "newOdds": "+140",
            "noVigPriceFromAlert": "+145",
            "ev": "2.5"
        }
        
        try:
            response = requests.post(f"{self.base_url}/pod_alert", json=test_alert, timeout=10)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Alert simulation result: {result}")
                return result
            else:
                logger.error(f"Alert simulation failed: {response.status_code}")
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Alert simulation error: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main function"""
    tester = ManualRefreshTester()
    
    # Run the background refresher test
    tester.test_background_refresher()
    
    # Optionally simulate an alert
    # tester.simulate_alert()

if __name__ == "__main__":
    main() 