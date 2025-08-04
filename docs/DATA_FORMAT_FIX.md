# POD Alerts Data Format Fix

## Issue Identified

The POD Alerts refresh system was not working because of **data format inconsistency** between initial alerts and background refreshes.

### Root Cause

In the `build_event_object` function in `backend/main.py`, there were two different data paths:

1. **Initial Alert Path**: Used `betbck_data.potential_bets_analyzed` (processed with BetBCK odds)
2. **Background Refresh Path**: Used `pinnacle_data_processed.markets` (raw Pinnacle data)

The background refresher was correctly re-analyzing markets with fresh Pinnacle odds, but the `build_event_object` function wasn't using the re-analyzed data consistently.

## The Fix

### 1. Updated Data Path Logic

**Before:**
```python
# For background refresher updates, use the markets directly from pinnacle_data_processed
if betbck_data_available:
    potential_bets = bet_data.get("potential_bets_analyzed", [])
else:
    # Use markets directly from pinnacle_data_processed for background refresher
    potential_bets = entry["pinnacle_data_processed"].get("markets", [])
```

**After:**
```python
# For background refresher updates, use the markets from pinnacle_data_processed
# (which have been re-analyzed with fresh Pinnacle odds)
if betbck_data_available:
    # For initial alerts, use the original potential_bets_analyzed
    potential_bets = bet_data.get("potential_bets_analyzed", [])
else:
    # For background refreshes, use the re-analyzed markets from pinnacle_data_processed
    # These have been updated with fresh Pinnacle odds and existing BetBCK data
    potential_bets = entry["pinnacle_data_processed"].get("markets", [])
```

### 2. Fixed BetBCK Status Field

**Before:**
```python
"betbck_status": f"Data Fetched: {home_team} vs {away_team}" if entry["betbck_data"].get("status") == "success" else entry["betbck_data"].get("message", "Odds check pending..."),
```

**After:**
```python
"betbck_status": f"Data Fetched: {home_team} vs {away_team}" if betbck_data_available and entry["betbck_data"].get("status") == "success" else (entry["betbck_data"].get("message", "Odds check pending...") if betbck_data_available else "Background refresh - no BetBCK data"),
```

## How It Works Now

### Initial Alert Processing
1. POD alert received
2. BetBCK odds fetched and stored
3. Pinnacle odds fetched
4. EV calculated using BetBCK + Pinnacle odds
5. Event created with `betbck_data_available = True`
6. `build_event_object` uses `potential_bets_analyzed`

### Background Refresh Processing
1. Background refresher runs every 3 seconds
2. Fresh Pinnacle odds fetched
3. **Re-analyzes markets** using fresh Pinnacle odds + existing BetBCK data
4. Updates `pinnacle_data_processed.markets` with re-analyzed data
5. Event updated with `betbck_data_available = False` (for background refresh)
6. `build_event_object` uses re-analyzed `pinnacle_data_processed.markets`

### Key Points
- ✅ **BetBCK odds are NOT re-fetched** during background refreshes
- ✅ **Pinnacle NVP is updated** with fresh data
- ✅ **EV is recalculated** with fresh Pinnacle odds + existing BetBCK odds
- ✅ **Data format is consistent** between initial and background updates
- ✅ **WebSocket broadcasts** use the same `build_event_object` function

## Testing

Run the data format consistency test:

```bash
cd backend
python test_data_format_consistency.py
```

This will:
1. Create a test event
2. Analyze the initial data structure
3. Wait for background refresh
4. Compare the updated data structure
5. Verify format consistency

## Expected Behavior

1. **Initial Alert**: Shows BetBCK odds, Pinnacle NVP, and calculated EV
2. **Background Refresh**: Updates Pinnacle NVP, recalculates EV, keeps BetBCK odds
3. **Real-time Updates**: Frontend receives consistent data format via WebSocket
4. **Event Expiration**: Events expire after 60s (negative EV) or 180s (positive EV)

## Verification

To verify the fix is working:

1. **Check backend logs** for:
   ```
   [BackgroundRefresher] Re-analyzing markets for EV with fresh Pinnacle odds
   [BackgroundRefresher] Broadcasting update for event X
   [SafeBroadcast] Successfully queued broadcast for event X
   ```

2. **Check frontend** for:
   - Initial alert appears with all data
   - Pinnacle NVP updates every 3 seconds
   - EV recalculates with fresh odds
   - BetBCK odds remain constant

3. **Check WebSocket messages** for:
   - `pod_alert` messages every 3 seconds
   - Consistent data structure
   - Updated NVP and EV values

The system should now work correctly with real-time updates while maintaining the event expiration and removal logic you want. 