import time
import threading
import logging
import copy
from typing import Dict, Set, Any
from pinnacle_fetcher import fetch_live_pinnacle_event_odds
from utils import process_event_odds_for_display
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class PodEventManager:
    def __init__(self):
        self._active_events_lock = threading.Lock()
        self._dismissed_events_lock = threading.Lock()
        self._active_events: Dict[str, Dict[str, Any]] = {}
        self._dismissed_event_ids: Set[str] = set()
        self.EVENT_DATA_EXPIRY_SECONDS = 300
        self.BACKGROUND_REFRESH_INTERVAL_SECONDS = 5  # Set to 5 seconds for faster updates
        self._event_locks = defaultdict(threading.Lock)
        # Add async lock for async operations
        self._async_lock = asyncio.Lock()

    def get_event_lock(self, event_id: str):
        return self._event_locks[event_id]

    def get_active_events(self) -> Dict[str, Dict[str, Any]]:
        with self._active_events_lock:
            # Use shallow copy for better performance - deep copy only when needed
            return dict(self._active_events)

    def add_active_event(self, event_id: str, event_data: Dict[str, Any]) -> None:
        with self._active_events_lock:
            self._active_events[event_id] = event_data
        broadcast_all_active_events()

    def remove_active_event(self, event_id: str, broadcast_function=None) -> None:
        with self._active_events_lock:
            if event_id in self._active_events:
                logger.info(f"[PodEventManager] Removing active event: {event_id}")
                self._active_events.pop(event_id, None)
                
                # Send removal notification to frontend if broadcast function is available
                if broadcast_function:
                    try:
                        # Send a removal message to the frontend
                        broadcast_function(event_id, {"removed": True})
                        print(f"[PodEventManager] Sent removal notification for event {event_id}")
                    except Exception as e:
                        print(f"[PodEventManager] Error sending removal notification for event {event_id}: {e}")
            else:
                logger.debug(f"[PodEventManager] Event {event_id} not found in active events")

    def is_event_dismissed(self, event_id: str) -> bool:
        with self._dismissed_events_lock:
            return event_id in self._dismissed_event_ids

    def add_dismissed_event(self, event_id: str) -> None:
        with self._dismissed_events_lock:
            self._dismissed_event_ids.add(event_id)

    def remove_dismissed_event(self, event_id: str) -> None:
        with self._dismissed_events_lock:
            self._dismissed_event_ids.discard(event_id)

    def update_event_data(self, event_id: str, update_data: Dict[str, Any]) -> None:
        with self._active_events_lock:
            if event_id in self._active_events:
                self._active_events[event_id].update(update_data)
        broadcast_all_active_events()

    async def background_event_refresher(self, broadcast_function=None):
        print("[BackgroundRefresher] Background event refresher started (ASYNC)")
        logger.info("[BackgroundRefresher] Background event refresher started (ASYNC)")
        
        if broadcast_function is None:
            print("[BackgroundRefresher] No broadcast function provided - updates will not be sent!")
            logger.error("[BackgroundRefresher] No broadcast function provided - updates will not be sent!")
        else:
            print("[BackgroundRefresher] Broadcast function available - updates will be sent when odds change")
            logger.info("[BackgroundRefresher] Broadcast function available - updates will be sent when odds change")
        
        print("[BackgroundRefresher] Starting main loop...")
        loop_count = 0
        while True:
            try:
                await asyncio.sleep(self.BACKGROUND_REFRESH_INTERVAL_SECONDS)
                loop_count += 1
                current_time = time.time()
                active_events = self.get_active_events()
                
                # Log every 20 loops (every minute) to confirm it's running
                if loop_count % 20 == 0:
                    logger.info(f"[BackgroundRefresher] Loop #{loop_count} - Processing {len(active_events)} active events")
                    print(f"[BackgroundRefresher] Loop #{loop_count} - Processing {len(active_events)} active events")
                    
                    # FORCED CLEANUP: Remove any expired events that might have been missed
                    events_to_remove = []
                    for event_id, event_data in active_events.items():
                        try:
                            alert_age = current_time - event_data.get("alert_arrival_timestamp", 0)
                            markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
                            
                            # Check if all markets have negative EV
                            all_negative_ev = True
                            if markets:
                                for market in markets:
                                    ev_str = market.get("ev", "0")
                                    try:
                                        ev_value = float(ev_str.replace('%', ''))
                                        if ev_value > 0:
                                            all_negative_ev = False
                                            break
                                    except:
                                        pass
                            
                            # Check if event should be expired
                            expiry_time = 60 if all_negative_ev else 180
                            if alert_age > expiry_time:
                                print(f"[BackgroundRefresher] FORCED CLEANUP: Event {event_id} is {alert_age:.1f}s old (limit: {expiry_time}s), removing...")
                                events_to_remove.append(event_id)
                        except Exception as e:
                            print(f"[BackgroundRefresher] Error checking event {event_id} for cleanup: {e}")
                    
                    # Remove expired events (thread-safe)
                    for event_id in events_to_remove:
                        self.remove_active_event(event_id, broadcast_function)
                    
                    # Only broadcast events that are still being updated (not expired or too old)
                    if broadcast_function and active_events:
                        active_count = 0
                        for event_id, event_data in active_events.items():
                            try:
                                # Check if event is still being updated
                                alert_age = current_time - event_data.get("alert_arrival_timestamp", 0)
                                markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
                                
                                # Check if all markets have negative EV
                                all_negative_ev = True
                                if markets:
                                    for market in markets:
                                        ev_str = market.get("ev", "0")
                                        try:
                                            ev_value = float(ev_str.replace('%', ''))
                                            if ev_value > 0:
                                                all_negative_ev = False
                                                break
                                        except:
                                            pass
                                
                                # Only broadcast if event is still being updated
                                if not (all_negative_ev and alert_age > 60):
                                    broadcast_function(event_id, event_data)
                                    active_count += 1
                            except Exception as e:
                                print(f"[BackgroundRefresher] Error broadcasting event {event_id}: {e}")
                        
                        if active_count > 0:
                            print(f"[BackgroundRefresher] Broadcasted {active_count} active events to frontend")
                        else:
                            print(f"[BackgroundRefresher] No active events to broadcast (all are expired or too old)")
                else:
                    print(f"[BackgroundRefresher] Loop #{loop_count} - sleeping for {self.BACKGROUND_REFRESH_INTERVAL_SECONDS} seconds...")
                
                for event_id, event_data in active_events.items():
                    try:
                        # Validate event data structure before processing
                        if not event_data or "pinnacle_data_processed" not in event_data or event_data["pinnacle_data_processed"] is None:
                            print(f"[BackgroundRefresher] Event {event_id} has corrupted data structure, removing...")
                            self.remove_active_event(event_id, broadcast_function)
                            continue
                        
                        # Check if event has expired - faster expiration for negative EV alerts
                        alert_age = current_time - event_data.get("alert_arrival_timestamp", 0)
                        
                        # Check if this is a negative EV alert (all markets have negative EV)
                        markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
                        all_negative_ev = True
                        if markets:
                            for market in markets:
                                ev_str = market.get("ev", "0")
                                try:
                                    ev_value = float(ev_str.replace('%', ''))
                                    if ev_value > 0:
                                        all_negative_ev = False
                                        break
                                except:
                                    pass
                        
                        # Expire negative EV alerts after 60 seconds, positive EV alerts after 3 minutes
                        expiry_time = 60 if all_negative_ev else 180  # 3 minutes for positive EV
                        
                        # Stop updating negative EV alerts after 60 seconds, but keep them visible for a bit longer
                        if all_negative_ev and alert_age > 60:
                            print(f"[BackgroundRefresher] Event {event_id} is negative EV and older than 60s, skipping updates (age: {alert_age:.1f}s)")
                            # Don't broadcast updates for old negative EV events
                            continue
                        
                        # Remove expired alerts (thread-safe)
                        if alert_age > expiry_time:
                            print(f"[BackgroundRefresher] Event {event_id} has expired (age: {alert_age:.1f}s, limit: {expiry_time}s, negative_ev: {all_negative_ev}), removing...")
                            self.remove_active_event(event_id, broadcast_function)
                            continue
                        
                        try:
                            # Fetch previous odds/EV for comparison
                            prev_markets = event_data.get("pinnacle_data_processed", {}).get("markets", [])
                            prev_nvp_map = { (m.get("market"), m.get("selection"), m.get("line")): m.get("pinnacle_nvp") for m in prev_markets }
                            prev_ev_map = { (m.get("market"), m.get("selection"), m.get("line")): m.get("ev") for m in prev_markets }

                            pinnacle_api_result = fetch_live_pinnacle_event_odds(event_id)
                            
                            if pinnacle_api_result and pinnacle_api_result.get("success"):
                                print(f"[BackgroundRefresher] [SUCCESS] Pinnacle API call successful for {event_id}")
                                # Process the new odds - use SAME pipeline as initial alert
                                processed_odds = process_event_odds_for_display(pinnacle_api_result.get("data"))
                                
                                # DEBUG: Log what Swordfish returned
                                raw_data = pinnacle_api_result.get("data", {})
                                print(f"[BackgroundRefresher] DEBUG: Swordfish returned {len(raw_data.get('markets', []))} markets")
                                if raw_data.get('markets'):
                                    print(f"[BackgroundRefresher] DEBUG: ALL MARKETS FROM SWORDFISH for {event_id}:")
                                    for i, market in enumerate(raw_data['markets']):
                                        print(f"  Market {i}: {market.get('market')} {market.get('selection')} Line: {market.get('line')} NVP: {market.get('pinnacle_nvp')}")
                                
                                # Log the actual odds being fetched
                                new_markets = processed_odds.get("markets", [])
                                if new_markets:
                                    sample_market = new_markets[0]
                                    print(f"[BackgroundRefresher] Fetched fresh odds for {event_id}:")
                                    print(f"  Market: {sample_market.get('market', 'N/A')}")
                                    print(f"  Selection: {sample_market.get('selection', 'N/A')}")
                                    print(f"  NVP: {sample_market.get('pinnacle_nvp', 'N/A')}")
                                    print(f"  EV: {sample_market.get('ev', 'N/A')}")
                                    print(f"  BetBCK: {sample_market.get('betbck_odds', 'N/A')}")
                                
                                # Update the event data with new odds - ALWAYS update timestamp
                                event_data["pinnacle_data_processed"] = processed_odds
                                event_data["last_update"] = int(current_time)
                                event_data["last_pinnacle_data_update_timestamp"] = int(current_time)
                                
                                # Re-analyze markets for EV with fresh Pinnacle odds and existing BetBCK data
                                try:
                                    from utils.pod_utils import analyze_markets_for_ev
                                    betbck_data = event_data.get("betbck_data", {}).get("data", {})
                                    
                                    if betbck_data and processed_odds:
                                        print(f"[BackgroundRefresher] Re-analyzing markets for EV with fresh Pinnacle odds")
                                        fresh_potential_bets = analyze_markets_for_ev(betbck_data, processed_odds)
                                        
                                        # Filter out unrealistic EVs (outside ±30% range)
                                        realistic_bets = []
                                        for bet in fresh_potential_bets:
                                            try:
                                                ev_str = bet.get("ev", "0")
                                                ev_value = float(ev_str.replace('%', ''))
                                                if -30 <= ev_value <= 30:
                                                    realistic_bets.append(bet)
                                                else:
                                                    print(f"[BackgroundRefresher] Filtering out unrealistic EV: {ev_str} for {bet.get('market', 'N/A')} {bet.get('selection', 'N/A')}")
                                            except:
                                                realistic_bets.append(bet)  # Keep if we can't parse EV
                                        
                                        # Update the processed odds with fresh EV calculations
                                        processed_odds["markets"] = realistic_bets
                                        event_data["pinnacle_data_processed"] = processed_odds
                                        
                                        # NEW: Sync the fresh markets back to betbck_data so build_event_object uses them
                                        if "betbck_data" in event_data and "data" in event_data["betbck_data"]:
                                            event_data["betbck_data"]["data"]["potential_bets_analyzed"] = realistic_bets
                                            print(f"[BackgroundRefresher] Synced fresh markets to betbck_data for {event_id}")
                                        
                                        print(f"[BackgroundRefresher] Updated EV analysis: {len(realistic_bets)} realistic bets found")
                                    else:
                                        print(f"[BackgroundRefresher] No BetBCK data available for EV re-analysis")
                                except Exception as ev_error:
                                    print(f"[BackgroundRefresher] Error re-analyzing EV: {ev_error}")
                                    logger.error(f"[BackgroundRefresher] Error re-analyzing EV: {ev_error}")
                                
                                # Compare new odds/EV with previous
                                new_markets = processed_odds.get("markets", [])
                                new_nvp_map = { (m.get("market"), m.get("selection"), m.get("line")): m.get("pinnacle_nvp") for m in new_markets }
                                new_ev_map = { (m.get("market"), m.get("selection"), m.get("line")): m.get("ev") for m in new_markets }
                                
                                odds_changed = False
                                ev_changed = False
                                changes_found = []
                                
                                # DEBUG: Log all market data to see what's happening
                                print(f"[BackgroundRefresher] DEBUG: Checking {len(new_markets)} markets for {event_id}")
                                for i, market in enumerate(new_markets[:3]):  # Log first 3 markets
                                    print(f"[BackgroundRefresher] Market {i}: {market.get('market')} {market.get('selection')} NVP: {market.get('pinnacle_nvp')} EV: {market.get('ev')}")
                                
                                print(f"[BackgroundRefresher] Comparing odds for {event_id}:")
                                for key in new_nvp_map:
                                    old_nvp = prev_nvp_map.get(key)
                                    new_nvp = new_nvp_map[key]
                                    if old_nvp != new_nvp:
                                        odds_changed = True
                                        changes_found.append(f"NVP {key}: {old_nvp} -> {new_nvp}")
                                        print(f"  [CHANGE] NVP CHANGE: {key} {old_nvp} -> {new_nvp}")
                                    else:
                                        print(f"  [SAME] NVP SAME: {key} = {new_nvp}")
                                
                                for key in new_ev_map:
                                    old_ev = prev_ev_map.get(key)
                                    new_ev = new_ev_map[key]
                                    if old_ev != new_ev:
                                        ev_changed = True
                                        changes_found.append(f"EV {key}: {old_ev} -> {new_ev}")
                                        print(f"  [CHANGE] EV CHANGE: {key} {old_ev} -> {new_ev}")
                                    else:
                                        print(f"  [SAME] EV SAME: {key} = {new_ev}")
                                
                                if changes_found:
                                    print(f"[CHANGES] [BackgroundRefresher] ODDS CHANGES DETECTED for {event_id}:")
                                    for change in changes_found:
                                        print(f"  [CHANGE] {change}")
                                    print(f"[BROADCAST] [BackgroundRefresher] Broadcasting changes to frontend...")
                                else:
                                    print(f"[STABLE] [BackgroundRefresher] No odds changes for {event_id} (all values stable)")
                                
                                # Always broadcast to show the system is working (even if no changes)
                                if broadcast_function:
                                    # Log some key odds for debugging
                                    sample_market = new_markets[0] if new_markets else {}
                                    print(f"[BackgroundRefresher] Broadcasting update for event {event_id}")
                                    print(f"[BackgroundRefresher] Sample odds: {sample_market.get('market', 'N/A')} {sample_market.get('selection', 'N/A')} NVP: {sample_market.get('pinnacle_nvp', 'N/A')} EV: {sample_market.get('ev', 'N/A')}")
                                    print(f"[BackgroundRefresher] Total markets to broadcast: {len(new_markets)}")
                                    
                                    # IMPORTANT: Pass the raw event_data to broadcast function
                                    # The broadcast function will call build_event_object internally
                                    try:
                                        print(f"[BackgroundRefresher] Broadcasting update for event {event_id}")
                                        broadcast_function(event_id, event_data)
                                        print(f"[BackgroundRefresher] SUCCESS: Successfully broadcasted update for event {event_id}")
                                    except Exception as broadcast_error:
                                        print(f"[BackgroundRefresher] ERROR broadcasting for {event_id}: {broadcast_error}")
                                else:
                                    print(f"[BackgroundRefresher] No broadcast function available for event {event_id}")
                                
                                # Update the manager with the synced data (thread-safe) - ALWAYS persist
                                self.update_event_data(event_id, {
                                    "pinnacle_data_processed": processed_odds,
                                    "betbck_data": event_data.get("betbck_data"),  # Include synced betbck_data if present
                                    "last_update": int(current_time),
                                    "last_pinnacle_data_update_timestamp": int(current_time)
                                })
                                print(f"[BackgroundRefresher] SUCCESS: Updated event data in manager for event {event_id}")
                            else:
                                print(f"[BackgroundRefresher] [FAILED] Pinnacle API call failed for {event_id}: {pinnacle_api_result}")
                                continue
                                
                        except Exception as e:
                            print(f"[BackgroundRefresher] Error processing event {event_id}: {e}")
                            logger.error(f"[BackgroundRefresher] Error processing event {event_id}: {e}")
                            
                    except Exception as e:
                        print(f"[BackgroundRefresher] Error in event loop for {event_id}: {e}")
                        logger.error(f"[BackgroundRefresher] Error in event loop for {event_id}: {e}")
                        
            except Exception as e:
                print(f"[BackgroundRefresher] Critical error in main loop: {e}")
                logger.error(f"[BackgroundRefresher] Critical error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

def broadcast_all_active_events():
    """Broadcast all active events to WebSocket clients"""
    try:
        # Use a callback approach instead of direct import to avoid circular dependencies
        logger.info("[PodEventManager] Need to broadcast all active events - will be handled by main.py")
    except Exception as e:
        logger.error(f"[PodEventManager] Error in broadcast_all_active_events: {e}")