#!/usr/bin/env python3
"""
POD Alerts Diagnostic Script
This script helps diagnose issues with the POD Alerts refresh system.
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

class PODAlertsDiagnostic:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
    
    def run_diagnostics(self):
        """Run all diagnostic checks"""
        logger.info("=== POD Alerts Diagnostic Started ===")
        
        checks = [
            ("Backend Connectivity", self.check_backend_connectivity),
            ("Refresher Status", self.check_refresher_status),
            ("WebSocket Connection", self.check_websocket_connection),
            ("Active Events", self.check_active_events),
            ("Event Data Structure", self.check_event_data_structure),
            ("Background Refresher Logs", self.check_background_refresher_logs),
            ("Memory Usage", self.check_memory_usage),
            ("BetBCK Status", self.check_betbck_status),
        ]
        
        for check_name, check_func in checks:
            try:
                logger.info(f"Running check: {check_name}")
                result = check_func()
                self.results[check_name] = result
                logger.info(f"✓ {check_name}: {result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"✗ {check_name} failed: {e}")
                self.results[check_name] = {"status": "error", "error": str(e)}
        
        self.print_summary()
        return self.results
    
    def check_backend_connectivity(self):
        """Check if backend is responding"""
        try:
            response = requests.get(f"{self.base_url}/test", timeout=5)
            if response.status_code == 200:
                return {"status": "connected", "response": response.json()}
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_refresher_status(self):
        """Check if background refresher is running"""
        try:
            response = requests.get(f"{self.base_url}/refresher-status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": data.get("status"),
                    "refresher_running": data.get("refresher_running"),
                    "thread_alive": data.get("thread_alive"),
                    "active_events_count": data.get("active_events_count"),
                    "refresher_interval": data.get("refresher_interval_seconds")
                }
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            import websocket
            import threading
            
            result = {"status": "testing", "connected": False, "messages_received": 0}
            
            def on_message(ws, message):
                result["messages_received"] += 1
                logger.info(f"WebSocket message received: {message[:100]}...")
            
            def on_error(ws, error):
                result["error"] = str(error)
                logger.error(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logger.info("WebSocket connection closed")
            
            def on_open(ws):
                result["connected"] = True
                logger.info("WebSocket connection opened")
                # Send a test message
                ws.send(json.dumps({"type": "test", "timestamp": time.time()}))
            
            # Connect to WebSocket
            ws_url = f"ws://localhost:5001/ws"
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            time.sleep(3)
            
            ws.close()
            wst.join(timeout=2)
            
            if result["connected"]:
                result["status"] = "connected"
            else:
                result["status"] = "failed"
            
            return result
            
        except ImportError:
            return {"status": "error", "error": "websocket-client not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_active_events(self):
        """Check active events data"""
        try:
            response = requests.get(f"{self.base_url}/get_active_events_data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                events = data.get("data", {})
                
                return {
                    "status": "success",
                    "event_count": len(events),
                    "event_ids": list(events.keys()),
                    "sample_event": list(events.values())[0] if events else None
                }
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_event_data_structure(self):
        """Check if event data has the correct structure"""
        try:
            response = requests.get(f"{self.base_url}/get_active_events_data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                events = data.get("data", {})
                
                if not events:
                    return {"status": "no_events", "message": "No active events to check"}
                
                # Check first event structure
                first_event = list(events.values())[0]
                required_fields = ["title", "markets", "alert_arrival_timestamp"]
                missing_fields = [field for field in required_fields if field not in first_event]
                
                if missing_fields:
                    return {
                        "status": "error",
                        "missing_fields": missing_fields,
                        "available_fields": list(first_event.keys())
                    }
                
                # Check markets structure
                markets = first_event.get("markets", [])
                if markets:
                    first_market = markets[0]
                    market_fields = ["market", "selection", "pinnacle_nvp", "betbck_odds", "ev"]
                    missing_market_fields = [field for field in market_fields if field not in first_market]
                    
                    if missing_market_fields:
                        return {
                            "status": "error",
                            "missing_market_fields": missing_market_fields,
                            "available_market_fields": list(first_market.keys())
                        }
                
                return {
                    "status": "valid",
                    "event_count": len(events),
                    "markets_per_event": len(markets) if markets else 0
                }
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_background_refresher_logs(self):
        """Check for background refresher activity in logs"""
        # This would require access to log files
        # For now, we'll check if the refresher is running and has active events
        try:
            refresher_status = self.check_refresher_status()
            active_events = self.check_active_events()
            
            if (refresher_status.get("status") == "running" and 
                active_events.get("status") == "success" and 
                active_events.get("event_count", 0) > 0):
                
                return {
                    "status": "active",
                    "refresher_running": refresher_status.get("refresher_running"),
                    "active_events": active_events.get("event_count"),
                    "message": "Refresher is running and has events to process"
                }
            else:
                return {
                    "status": "inactive",
                    "refresher_running": refresher_status.get("refresher_running"),
                    "active_events": active_events.get("event_count", 0),
                    "message": "Refresher may not be processing events"
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_memory_usage(self):
        """Check memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "status": "success",
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {"status": "error", "error": "psutil not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_betbck_status(self):
        """Check BetBCK status"""
        try:
            response = requests.get(f"{self.base_url}/api/betbck/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def print_summary(self):
        """Print diagnostic summary"""
        logger.info("\n=== POD Alerts Diagnostic Summary ===")
        
        critical_issues = []
        warnings = []
        
        for check_name, result in self.results.items():
            status = result.get("status", "unknown")
            
            if status == "error":
                critical_issues.append(f"✗ {check_name}: {result.get('error', 'Unknown error')}")
            elif status in ["not_running", "failed", "inactive"]:
                warnings.append(f"⚠ {check_name}: {status}")
            else:
                logger.info(f"✓ {check_name}: {status}")
        
        if critical_issues:
            logger.error("\n=== CRITICAL ISSUES ===")
            for issue in critical_issues:
                logger.error(issue)
        
        if warnings:
            logger.warning("\n=== WARNINGS ===")
            for warning in warnings:
                logger.warning(warning)
        
        if not critical_issues and not warnings:
            logger.info("\n✓ All checks passed! System appears to be working correctly.")
        
        logger.info("\n=== DETAILED RESULTS ===")
        for check_name, result in self.results.items():
            logger.info(f"\n{check_name}:")
            for key, value in result.items():
                if key != "status":
                    logger.info(f"  {key}: {value}")

def main():
    """Main function to run diagnostics"""
    diagnostic = PODAlertsDiagnostic()
    results = diagnostic.run_diagnostics()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pod_alerts_diagnostic_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nDiagnostic results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    main() 