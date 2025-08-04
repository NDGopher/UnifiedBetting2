# POD Alerts Refresh System Analysis

## Issue Summary

The POD Alerts system is experiencing issues where:
- Initial alerts work perfectly
- Background refreshes (every 3 seconds) are not being pushed to the frontend
- Pinnacle NVP and EV updates are not appearing in real-time

## System Architecture

### Current Flow
1. **Initial Alert**: Chrome Extension → Backend → WebSocket → Frontend ✅
2. **Background Refresh**: Backend (3s loop) → Pinnacle API → WebSocket → Frontend ❌

### Key Components
- **Backend**: FastAPI server with background refresher thread
- **WebSocket**: Real-time communication between backend and frontend
- **Background Refresher**: 3-second loop that fetches fresh Pinnacle odds
- **Event Manager**: Manages active events and their data

## Potential Issues Identified

### 1. Background Refresher Thread Issues

**Problem**: The background refresher may not be running or may be encountering errors.

**Symptoms**:
- No `[BackgroundRefresher]` messages in console logs
- Refresher status shows as "not_running"
- Events don't get updated timestamps

**Diagnostic Steps**:
```bash
# Check refresher status
curl http://localhost:5001/refresher-status

# Check if refresher thread is alive
# Look for these messages in backend console:
# [BackgroundRefresher] Background event refresher started
# [BackgroundRefresher] Loop #X - Processing Y active events
```

**Potential Fixes**:
- Restart the backend server
- Manually start the refresher: `POST /refresher/start`
- Check for exceptions in the refresher thread

### 2. WebSocket Broadcasting Issues

**Problem**: Updates may not be reaching the frontend due to WebSocket issues.

**Symptoms**:
- WebSocket connection appears stable
- No `pod_alert` messages received on frontend
- Backend shows successful broadcasts but frontend doesn't receive them

**Diagnostic Steps**:
```bash
# Test WebSocket connection
python backend/test_websocket_updates.py

# Check WebSocket manager logs for:
# [WebSocket] Broadcasting message type 'pod_alert'
# [SafeBroadcast] Queued broadcast for event X
```

**Potential Issues**:
- Event loop not available for broadcasting
- `build_event_object` returning None
- WebSocket connection dropping silently

### 3. Data Structure Mismatches

**Problem**: The data structure sent during background refreshes may differ from initial alerts.

**Symptoms**:
- Initial alerts display correctly
- Background updates fail to update the UI
- Console errors about missing fields

**Key Differences**:
- **Initial Alert**: Uses `betbck_data` for markets
- **Background Refresh**: Uses `pinnacle_data_processed` directly

**Diagnostic Steps**:
```bash
# Check event data structure
python backend/pod_alerts_diagnostic.py

# Look for missing fields in event objects
# Required: title, markets, alert_arrival_timestamp
# Market fields: market, selection, pinnacle_nvp, betbck_odds, ev
```

### 4. Event Data Corruption

**Problem**: Events may become corrupted during processing, preventing updates.

**Symptoms**:
- Events disappear unexpectedly
- `pinnacle_data_processed` is None
- Build event object fails

**Diagnostic Steps**:
```bash
# Clean up corrupted events
curl -X POST http://localhost:5001/test/cleanup-corrupted-events

# Check for corrupted events in logs:
# [BuildEventObject] pinnacle_data_processed is None for event X
```

### 5. Pinnacle API Issues

**Problem**: Background refresher may fail to fetch fresh odds from Pinnacle.

**Symptoms**:
- Pinnacle API calls failing
- No new odds data being fetched
- Events not updating with fresh data

**Diagnostic Steps**:
```bash
# Check Pinnacle API responses in logs:
# [BackgroundRefresher] [SUCCESS] Pinnacle API call successful for X
# [BackgroundRefresher] [FAILED] Pinnacle API call failed for X
```

## Troubleshooting Steps

### Step 1: Run Diagnostic Script
```bash
cd backend
python pod_alerts_diagnostic.py
```

This will check:
- Backend connectivity
- Refresher status
- WebSocket connection
- Active events
- Event data structure
- Memory usage
- BetBCK status

### Step 2: Test WebSocket Updates
```bash
cd backend
python test_websocket_updates.py
```

This will:
- Connect to WebSocket
- Monitor for 60 seconds
- Analyze message types and timing
- Check for multiple updates from same event

### Step 3: Manual Refresh Test
```bash
cd backend
python manual_refresh_test.py
```

This will:
- Check current status
- Clean up corrupted events
- Start refresher if needed
- Monitor for updates

### Step 4: Check Backend Logs
Look for these key messages:

**Good Signs**:
```
[BackgroundRefresher] Background event refresher started
[BackgroundRefresher] Loop #20 - Processing 2 active events
[BackgroundRefresher] Broadcasting update for event X
[SafeBroadcast] Queued broadcast for event X
[WebSocket] Broadcasting message type 'pod_alert'
```

**Bad Signs**:
```
[BackgroundRefresher] No broadcast function provided
[SafeBroadcast] Cannot broadcast event X - event loop not available
[BuildEventObject] pinnacle_data_processed is None for event X
[BackgroundRefresher] ERROR building event object for X
```

## Potential Fixes

### Fix 1: Ensure Background Refresher is Running
```python
# In main.py startup event, add more logging:
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    
    # Add verification that thread started
    time.sleep(2)
    if refresher_thread and refresher_thread.is_alive():
        logger.info("✓ Background refresher thread confirmed running")
    else:
        logger.error("✗ Background refresher thread failed to start")
```

### Fix 2: Improve WebSocket Broadcasting
```python
# In broadcast_pod_alert_safe, add more validation:
def broadcast_pod_alert_safe(event_id, event_data):
    # Add more detailed logging
    logger.info(f"[SafeBroadcast] Attempting to broadcast event {event_id}")
    logger.info(f"[SafeBroadcast] Event data keys: {list(event_data.keys()) if event_data else 'None'}")
    
    # ... existing validation ...
    
    if main_event_loop and main_event_loop.is_running():
        try:
            asyncio.run_coroutine_threadsafe(
                async_broadcast_pod_alert(event_id, event_data),
                main_event_loop
            )
            logger.info(f"[SafeBroadcast] ✓ Successfully queued broadcast for event {event_id}")
        except Exception as e:
            logger.error(f"[SafeBroadcast] ✗ Error queuing broadcast: {e}")
    else:
        logger.error(f"[SafeBroadcast] ✗ Event loop not available for event {event_id}")
```

### Fix 3: Fix Data Structure Issues
```python
# In build_event_object, ensure consistent data structure:
def build_event_object(event_id, entry):
    # ... existing validation ...
    
    # Ensure markets are always in the same format
    if betbck_data_available:
        potential_bets = bet_data.get("potential_bets_analyzed", [])
    else:
        # Use markets directly from pinnacle_data_processed for background refresher
        potential_bets = entry["pinnacle_data_processed"].get("markets", [])
    
    # Ensure all markets have required fields
    markets = []
    for bet in potential_bets:
        market = {
            "market": bet.get("market", "N/A"),
            "selection": bet.get("selection", "N/A"),
            "line": bet.get("line", ""),
            "pinnacle_nvp": str(bet.get("pinnacle_nvp", "N/A")),
            "betbck_odds": str(bet.get("betbck_odds", "N/A")),
            "ev": bet.get("ev", "N/A")
        }
        markets.append(market)
    
    # ... rest of function ...
```

## Monitoring and Prevention

### Add Health Checks
```python
# Add to main.py
@app.get("/health/pod-alerts")
async def pod_alerts_health():
    """Health check for POD alerts system"""
    try:
        refresher_status = await get_refresher_status()
        active_events = pod_event_manager.get_active_events()
        
        return {
            "status": "healthy" if refresher_status.get("status") == "running" else "unhealthy",
            "refresher_running": refresher_status.get("refresher_running", False),
            "active_events_count": len(active_events),
            "last_check": time.time()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### Add Automatic Recovery
```python
# Add to pod_event_manager.py
def auto_recovery_check(self):
    """Check if refresher needs to be restarted"""
    if not self._refresher_thread or not self._refresher_thread.is_alive():
        logger.warning("Background refresher thread died, attempting restart...")
        self.start_background_refresher()
```

## Conclusion

The most likely causes of the refresh issue are:

1. **Background refresher thread not running** - Check `/refresher-status`
2. **WebSocket broadcasting failures** - Check for event loop issues
3. **Data structure mismatches** - Ensure consistent event object format
4. **Event data corruption** - Clean up corrupted events

Run the diagnostic scripts to identify the specific issue, then apply the appropriate fix. The system should work correctly once the background refresher is properly running and broadcasting updates. 