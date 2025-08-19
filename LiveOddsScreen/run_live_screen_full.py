#!/usr/bin/env python3
"""
Complete Live Odds Screen with full scraping system integrated into clean framework
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import threading
from threading import Lock
import os

# Import all the scraping modules
try:
    from pto_live_dom_scraper import scrape_pto_live, PTOSelectors, open_pto_driver, scrape_pto_live_with_driver
    from schema import EventOdds
    from team_matching import match_events
    from dashboard import build_best_table, serve_dashboard, push_rows
    from profile_resolver import resolve_chrome_profile
    from plive_dom_scraper_clean import open_plive_driver, scrape_plive_odds_with_driver, get_plive_paths_for_selections
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[Import] WARNING: Some modules not available: {e}")
    MODULES_AVAILABLE = False

def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Config] File not found: {path}")
        return {}
    except Exception as e:
        print(f"[Config] Error loading {path}: {e}")
        return {}

def _read_selection_keys(sel_file: Path) -> List[str]:
    try:
        raw = json.loads(sel_file.read_text(encoding="utf-8"))
    except Exception:
        return []
    
    if isinstance(raw, dict):
        arr = raw.get("selections")
        if isinstance(arr, list):
            return [str(x) for x in arr]
    
    return []

def serve_dashboard_threaded(initial_data: List[Dict], port: int = 8765):
    """Start dashboard server in background thread"""
    def start_server():
        try:
            if MODULES_AVAILABLE:
                serve_dashboard(initial_data, port)
            else:
                # Fallback to simple dashboard
                from dashboard_simple import serve_dashboard_sync
                serve_dashboard_sync(initial_data, port)
        except Exception as e:
            print(f"[Dashboard] Error: {e}")
    
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    time.sleep(2)  # Give server time to start

def _to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

def main():
    print("[Init] Starting Live Odds Screen (Full System)...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--selectors", default="selectors.json") 
    parser.add_argument("--refresh", type=float, default=0.5)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    
    print(f"[Init] Command line args: {vars(args)}")
    
    # Load configuration
    print("[Config] Loading configuration files...")
    cfg = load_json(args.config)
    sels = load_json(args.selectors)
    
    print(f"[Config] Loaded config keys: {list(cfg.keys())}")
    print(f"[Config] Loaded selectors keys: {list(sels.keys())}")
    
    if not MODULES_AVAILABLE:
        print("[System] WARNING: Running in limited mode - some modules missing")
        print("[System] Starting simplified dashboard only...")
        serve_dashboard_threaded([], port=args.port)
        print(f"[Dashboard] Dashboard available at http://127.0.0.1:{args.port}/dashboard.html")
        
        try:
            print("[System] Press Ctrl+C to stop...")
            while True:
                print("[System] Running in limited mode...")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n[System] Stopping...")
            return 0
    
    # Start dashboard
    print(f"[Init] Starting dashboard on port {args.port}...")
    serve_dashboard_threaded([], port=args.port)
    print(f"[Dashboard] Dashboard available at http://127.0.0.1:{args.port}/dashboard.html")
    
    # Check for selections
    sel_file = Path("sports_selection.json")
    if not sel_file.exists():
        print("[Error] No sports_selection.json found!")
        print("[Error] Please run LIVE_ODDS_SCREEN.bat first to select sports.")
        return 1
    
    selections = _read_selection_keys(sel_file)
    print(f"[Config] Found selections: {selections}")
    
    if not selections:
        print("[Error] No selections found in sports_selection.json")
        return 1
    
    # Speed settings
    speed_mode = cfg.get("speed_mode", False)
    fast_refresh = cfg.get("fast_refresh", 0.1) if speed_mode else args.refresh
    actual_refresh = fast_refresh if speed_mode else args.refresh
    
    print(f"[Speed] Speed mode: {speed_mode}, Refresh rate: {actual_refresh}s")
    
    # Chrome profile setup
    print(f"\n[Browser] === CHROME PROFILE SETUP ===")
    user_data_dir = cfg.get("chrome_user_data_dir")
    profile_dir = cfg.get("chrome_profile_dir")
    print(f"[Browser] Config chrome_user_data_dir: {user_data_dir}")
    print(f"[Browser] Config chrome_profile_dir: {profile_dir}")
    
    if not user_data_dir or not Path(str(user_data_dir)).exists():
        print(f"[Browser] Profile path missing/invalid, resolving...")
        try:
            cud, cpd = resolve_chrome_profile()
            user_data_dir = user_data_dir or cud
            profile_dir = profile_dir or cpd
            print(f"[Browser] Resolved chrome_user_data_dir: {cud}")
            print(f"[Browser] Resolved chrome_profile_dir: {cpd}")
        except Exception as e:
            print(f"[Browser] Profile resolution error: {e}")
    
    print(f"[Browser] Final Chrome profile: user_data_dir={user_data_dir} profile_dir={profile_dir}")
    
    # Verify profile exists
    if user_data_dir:
        profile_path = Path(user_data_dir) / (profile_dir or "Profile 1")
        print(f"[Browser] Checking profile path: {profile_path}")
        print(f"[Browser] Profile exists: {profile_path.exists()}")
    print(f"[Browser] === END CHROME PROFILE SETUP ===\n")
    
    # Initialize scraping settings
    pto_headless = _to_bool(cfg.get("pto_headless", False))
    plive_headless = _to_bool(cfg.get("plive_headless", True))
    
    # Get PTO configurations
    raw_pto = sels.get("pto")
    raw_pto_multi = sels.get("pto_multi", [])
    allowed_books = sels.get("allowed_books", [])
    
    pto_cfgs = []
    if isinstance(raw_pto_multi, list):
        pto_cfgs = [c for c in raw_pto_multi if isinstance(c, dict)]
    elif isinstance(raw_pto, dict):
        pto_cfgs = [raw_pto]
    
    use_pto_dom = bool(cfg.get("use_pto_dom", True)) and bool(pto_cfgs)
    use_websocket = cfg.get("use_websocket", False)
    
    print(f"[System] WebSocket mode: {use_websocket}")
    print(f"[System] DOM scraping mode: {use_pto_dom}")
    
    # WebSocket client initialization
    websocket_client = None
    if use_websocket:
        try:
            from pto_websocket_integration import create_pto_websocket_client
            print(f"[WS] Attempting WebSocket initialization...")
            
            websocket_client = create_pto_websocket_client(selections)
            
            if websocket_client:
                print(f"[WS] SUCCESS: WebSocket client initialized!")
                print(f"[WS] WebSocket will provide real-time PTO data")
                # Keep DOM scraping available as fallback
                print(f"[WS] WebSocket primary, DOM scraping available as fallback")
            else:
                print(f"[WS] WARNING: WebSocket initialization failed")
                use_websocket = False
                
        except ImportError:
            print(f"[WS] WARNING: WebSocket module not available, using DOM scraping")
            use_websocket = False
        except Exception as e:
            print(f"[WS] ERROR: WebSocket setup error: {e}")
            use_websocket = False
    
    print(f"[System] use_pto_dom: {use_pto_dom}")
    print(f"[System] pto_headless: {pto_headless}")
    print(f"[System] plive_headless: {plive_headless}")
    print(f"[System] Available PTO configs: {len(pto_cfgs)}")
    print(f"[System] Allowed books: {allowed_books}")
    
    # Persistent drivers
    pto_driver = None
    plive_drivers: Dict[str, Any] = {}
    pto_tabs: List[Dict[str, Any]] = []
    
    # Initialize PTO driver if needed
    if use_pto_dom:
        try:
            debug_port = None
            try:
                dp = cfg.get("chrome_debug_port")
                if dp:
                    debug_port = int(dp)
                print(f"[PTO] Using debug_port: {debug_port}")
            except Exception as e:
                print(f"[PTO] Error parsing debug_port: {e}")
                debug_port = None
            
            # Filter PTO configs based on selections
            selected_cfgs = []
            if sel_file.exists():
                allowed = set(_read_selection_keys(sel_file))
                print(f"[PTO] Active selections: {sorted(list(allowed))}")
                
                def _ok(cfg: Dict[str, Any]) -> bool:
                    k = f"{cfg.get('sport','')}:{cfg.get('market','')}".lower()
                    url_match = cfg.get('url') in allowed
                    key_match = k in allowed
                    return url_match or key_match
                
                selected_cfgs = [c for c in pto_cfgs if _ok(c)]
                print(f"[PTO] Filtered PTO configs: {len(selected_cfgs)} out of {len(pto_cfgs)}")
                for i, cfg_item in enumerate(selected_cfgs):
                    print(f"[PTO]   Config {i+1}: {cfg_item.get('sport')}:{cfg_item.get('market')} -> {cfg_item.get('url', 'NO_URL')}")
            
            if selected_cfgs:
                print(f"[PTO] Opening PTO driver (headless={pto_headless}, debug_port={debug_port})...")
                print(f"[PTO] Attempting to connect to Chrome at port {debug_port}...")
                
                try:
                    pto_driver = open_pto_driver(
                        user_data_dir=user_data_dir,
                        profile_dir=profile_dir,
                        headless=pto_headless,
                        remote_debug_port=debug_port
                    )
                    print(f"[PTO] Driver initialization completed!")
                except Exception as driver_error:
                    print(f"[PTO] CRITICAL: Driver creation failed - {driver_error}")
                    pto_driver = None
                
                if pto_driver:
                    print("[PTO] SUCCESS: PTO driver opened")
                    print(f"[PTO] Session ID: {pto_driver.session_id}")
                    print(f"[PTO] Current handles: {len(pto_driver.window_handles)}")
                    
                    # Open tabs for each config
                    print(f"[PTO] Starting to open {len(selected_cfgs)} tabs...")
                    for i, cfg_item in enumerate(selected_cfgs):
                        try:
                            url = cfg_item.get("url", "")
                            if url:
                                sport_market = f"{cfg_item.get('sport')}:{cfg_item.get('market')}"
                                print(f"[PTO] Tab {i+1}/{len(selected_cfgs)}: Opening {sport_market}")
                                
                                # Set page load timeout
                                pto_driver.set_page_load_timeout(10)
                                
                                # Create new tab
                                pto_driver.execute_script("window.open();")
                                print(f"[PTO] Tab {i+1}: Created new window, total handles: {len(pto_driver.window_handles)}")
                                
                                # Switch to new tab
                                pto_driver.switch_to.window(pto_driver.window_handles[-1])
                                print(f"[PTO] Tab {i+1}: Switched to window handle: {pto_driver.current_window_handle}")
                                
                                # Navigate to URL
                                print(f"[PTO] Tab {i+1}: Navigating to {url[:60]}...")
                                pto_driver.get(url)
                                
                                pto_tabs.append({
                                    "handle": pto_driver.current_window_handle,
                                    "cfg": cfg_item
                                })
                                print(f"[PTO] Tab {i+1}: SUCCESS - {sport_market} loaded")
                                time.sleep(1)  # Brief pause between tabs
                        except Exception as e:
                            print(f"[PTO] Tab {i+1}: ERROR - Failed to open {cfg_item.get('sport')}:{cfg_item.get('market')}: {e}")
                    
                    print(f"[PTO] Tab opening completed: {len(pto_tabs)} tabs successfully opened")
                else:
                    print("[PTO] ERROR: Failed to open PTO driver")
            else:
                print("[PTO] No matching PTO configs found for selections")
        except Exception as e:
            print(f"[PTO] ERROR: PTO driver initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Main scraping loop
    print(f"\n[System] === STARTING MAIN LOOP ===")
    print(f"[System] Refresh rate: {actual_refresh}s")
    print(f"[System] Dashboard: http://127.0.0.1:{args.port}/dashboard.html")
    
    last_rows = []
    last_rows_ts = 0.0
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n[System] === CYCLE {cycle_count} ===")
            
            # PTO Data Collection (WebSocket or DOM)
            all_pto_events = []
            if use_websocket and websocket_client and websocket_client.is_ready():
                try:
                    print(f"[PTO] Using WebSocket data source...")
                    ws_events = websocket_client.get_events_for_main_system()
                    all_pto_events.extend(ws_events)
                    print(f"[PTO] SUCCESS: WebSocket provided {len(ws_events)} events")
                    
                    if ws_events:
                        print(f"[PTO] Sample WebSocket events:")
                        for i, event in enumerate(ws_events[:3]):
                            print(f"[PTO]   WS Event {i+1}: {event.get('sport')} {event.get('market')} - {event.get('home')} vs {event.get('away')} ({len(event.get('books', {}))} books)")
                    
                except Exception as e:
                    print(f"[PTO] ERROR: WebSocket data error: {e}")
                    all_pto_events = []
            elif use_pto_dom and pto_driver is not None and pto_tabs:
                print(f"[PTO] Scraping {len(pto_tabs)} PTO tabs...")
                for i, tab in enumerate(pto_tabs, 1):
                    try:
                        print(f"[PTO] Scraping tab {i}/{len(pto_tabs)}: {tab['cfg'].get('sport')}:{tab['cfg'].get('market')}")
                        pto_driver.switch_to.window(tab["handle"])
                        pto_cfg = tab["cfg"]
                        print(f"[PTO] Tab URL: {pto_cfg['url']}")
                        print(f"[PTO] Starting scrape with 12s timeout...")
                        
                        pto_events = scrape_pto_live_with_driver(
                            pto_driver,
                            pto_url=pto_cfg["url"],
                            selectors=PTOSelectors(
                                event_row_selector=pto_cfg["event_row_selector"],
                                home_team_selector=pto_cfg.get("home_team_selector", ""),
                                away_team_selector=pto_cfg.get("away_team_selector", ""),
                                market_container_selector=pto_cfg.get("market_container_selector"),
                                price_selector=pto_cfg.get("price_selector"),
                                team_title_selector=pto_cfg.get("team_title_selector"),
                                book_cell_selector=pto_cfg.get("book_cell_selector"),
                                book_icon_selector=pto_cfg.get("book_icon_selector"),
                                book_odds_value_selector=pto_cfg.get("book_odds_value_selector"),
                            ),
                            timeout=8,
                            allowed_books=allowed_books,
                            live_only=True,
                        )
                        
                        market_name = pto_cfg.get("market") or "moneyline"
                        sport_name = pto_cfg.get("sport") or "unknown"
                        for e in pto_events:
                            e.setdefault("market", market_name)
                            e.setdefault("sport", sport_name)
                            e.setdefault("ptoUrl", pto_cfg.get("url"))
                        
                        print(f"[PTO] COMPLETED: Tab {i} ({sport_name}:{market_name}) events: {len(pto_events)}")
                        if pto_events:
                            print(f"[PTO] Sample events from tab {i}:")
                            for j, event in enumerate(pto_events[:2]):
                                print(f"[PTO]   Event {j+1}: {event.get('home')} vs {event.get('away')} - books: {list(event.get('books', {}).keys())}")
                        else:
                            print(f"[PTO] WARNING: No events found on tab {i} - might be loading or no live games")
                        all_pto_events.extend(pto_events)
                        
                    except Exception as e:
                        print(f"[PTO] ERROR: Scrape error on tab {i}: {e}")
                        print(f"[PTO] Continuing to next tab...")
                        import traceback
                        traceback.print_exc()
                        continue
                
                print(f"[PTO] Total PTO events collected: {len(all_pto_events)}")
            else:
                print(f"[PTO] No PTO data source available - WebSocket:{use_websocket}, DOM:{use_pto_dom}")
                if use_websocket:
                    print(f"[PTO] WebSocket client ready: {websocket_client and websocket_client.is_ready() if websocket_client else False}")
                if use_pto_dom:
                    print(f"[PTO] DOM driver available: {pto_driver is not None}, tabs: {len(pto_tabs) if pto_tabs else 0}")
            
            # PLive Scraping
            print(f"\n[PLive] === PLIVE SCRAPING CYCLE ===")
            plive_events = []
            try:
                current_selections = _read_selection_keys(sel_file)
                # Use the first available driver for sport discovery, or create a temporary one
                discovery_driver = None
                if plive_drivers:
                    discovery_driver = list(plive_drivers.values())[0]
                else:
                    try:
                        discovery_driver = open_plive_driver(
                            user_data_dir=None, 
                            profile_dir=None, 
                            headless=plive_headless
                        )
                        # Store it for reuse
                        plive_drivers["discovery"] = discovery_driver
                    except Exception as e:
                        print(f"[PLive] Warning: Could not create discovery driver: {e}")
                
                plive_paths = get_plive_paths_for_selections(current_selections, driver=discovery_driver)
                print(f"[PLive] PLive paths to scrape: {plive_paths}")
                
                # Create or reuse drivers for each path
                for path in plive_paths:
                    print(f"[PLive] Processing path: {path}")
                    if path not in plive_drivers:
                        try:
                            print(f"[PLive] Creating new driver for {path}...")
                            plive_drivers[path] = open_plive_driver(
                                user_data_dir=None, 
                                profile_dir=None, 
                                headless=plive_headless
                            )
                            print(f"[PLive] SUCCESS: Created driver for {path}")
                        except Exception as e:
                            print(f"[PLive] ERROR: Failed to create driver for {path}: {e}")
                            continue
                    else:
                        print(f"[PLive] Reusing existing driver for {path}")
                    
                    driver = plive_drivers[path]
                    if driver is not None:
                        try:
                            # Test if driver session is still valid
                            try:
                                driver.current_url  # This will fail if session is invalid
                            except Exception:
                                print(f"[PLive] Driver session invalid for {path}, recreating...")
                                try:
                                    driver.quit()
                                except:
                                    pass
                                plive_drivers[path] = open_plive_driver(
                                    user_data_dir=None, 
                                    profile_dir=None, 
                                    headless=plive_headless
                                )
                                driver = plive_drivers[path]
                                print(f"[PLive] SUCCESS: Recreated driver for {path}")
                            
                            print(f"[PLive] Scraping {path}...")
                            plive_selectors = sels.get("plive", {})
                            cur = scrape_plive_odds_with_driver(driver, sports_paths=[path], selectors=plive_selectors)
                            sport_name = path.replace("#!/sport/", "Sport_")
                            print(f"[PLive] SUCCESS: {sport_name} events scraped: {len(cur)}")
                            if cur:
                                print(f"[PLive] Sample events from {sport_name}:")
                                for i, event in enumerate(cur[:2]):
                                    print(f"[PLive]   Event {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
                            plive_events.extend(cur)
                        except Exception as e:
                            print(f"[PLive] ERROR: Scraping failed for {path}: {e}")
                            # Try to recreate the driver on next cycle
                            try:
                                if path in plive_drivers:
                                    plive_drivers[path].quit()
                                    del plive_drivers[path]
                            except:
                                pass
                            import traceback
                            traceback.print_exc()
                
            except Exception as e:
                print(f"[PLive] Selection processing error: {e}")
            
            print(f"[PLive] Total PLive events collected: {len(plive_events)}")
            
            # Data Matching
            print(f"\n[Merge] === DATA MATCHING ===")
            print(f"[Merge] PLive events: {len(plive_events)}")
            print(f"[Merge] PTO events: {len(all_pto_events)}")
            
            if plive_events:
                print(f"[Merge] Sample PLive events:")
                for i, event in enumerate(plive_events[:3]):
                    print(f"[Merge]   PLive {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
            
            if all_pto_events:
                print(f"[Merge] Sample PTO events:")
                for i, event in enumerate(all_pto_events[:3]):
                    print(f"[Merge]   PTO {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
            
            matches = match_events(plive_events, all_pto_events)
            print(f"[Merge] Successful matches: {len(matches)}")
            
            # Build combined data
            combined = []
            if matches:
                for m in matches:
                    b = m["left"]
                    p = m["right"]
                    eo = EventOdds(
                        sport=b.get("sport", p.get("sport", "unknown")),
                        market=(b.get("market", p.get("market", "moneyline")).upper()),
                        home=b.get("home", ""),
                        away=b.get("away", ""),
                        books={},
                        line=b.get("line") or p.get("line"),
                        pto_url=p.get("ptoUrl") or b.get("ptoUrl"),
                    )
                    # Add betbck prices
                    b_books = b.get("books", {})
                    betbck_prices = b_books.get("betbck") or {"home": None, "away": None}
                    eo.books["betbck"] = {"home": betbck_prices.get("home"), "away": betbck_prices.get("away")}
                    # Add PTO books
                    for book_name, sides in (p.get("books", {}) or {}).items():
                        key = book_name.lower().strip().replace(" ", "_")
                        eo.books[key] = sides
                    combined.append(eo)
            else:
                # Use PLive data only if no matches
                for b in plive_events:
                    eo = EventOdds(
                        sport=b.get("sport", "unknown"),
                        market=(b.get("market", "moneyline").upper()),
                        home=b.get("home", ""),
                        away=b.get("away", ""),
                        books=b.get("books", {}),
                        line=b.get("line"),
                        pto_url=b.get("ptoUrl"),
                    )
                    combined.append(eo)
            
            # Filter for live rows with betbck data
            live_rows = [e for e in combined if (e.books.get("betbck", {}).get("home") or e.books.get("betbck", {}).get("away"))]
            
            # Use cached data if no fresh data
            if not live_rows and last_rows and ((time.time() - last_rows_ts) < 60):
                live_rows = last_rows
            else:
                if live_rows:
                    last_rows = live_rows
                    last_rows_ts = time.time()
            
            # Save debug data
            try:
                Path("debug_last.json").write_text(
                    json.dumps({
                        "counts": {"pto": len(all_pto_events), "plive": len(plive_events), "matches": len(matches), "live_rows": len(live_rows)},
                        "sample_plive": (plive_events[:3] if plive_events else []),
                    }, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass
            
            # Update dashboard
            rows = build_best_table(live_rows)
            print(f"[UI] Pushing {len(rows)} rows to dashboard")
            push_rows(rows)
            
            # Status update
            if cycle_count % 10 == 0:
                print(f"[Speed] Cycle #{cycle_count} - using {actual_refresh}s refresh")
            
            time.sleep(actual_refresh)
            
    except KeyboardInterrupt:
        print("\n[System] Stopping Live Odds Screen...")
    
    finally:
        # Cleanup
        try:
            if pto_driver:
                pto_driver.quit()
        except:
            pass
        
        for driver in plive_drivers.values():
            try:
                if driver:
                    driver.quit()
            except:
                pass
        
        try:
            if Path(".live_screen.lock").exists():
                Path(".live_screen.lock").unlink(missing_ok=True)
        except:
            pass
    
    return 0

if __name__ == "__main__":
    exit(main())
