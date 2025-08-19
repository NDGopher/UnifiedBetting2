import argparse
import json
import time
from typing import Any, Dict, List
import time as _time
from pathlib import Path
from threading import Lock
import os
import psutil

from pto_live_dom_scraper import scrape_pto_live, PTOSelectors
from schema import EventOdds
from team_matching import match_events
from dashboard import build_best_table, serve_dashboard, push_rows
from profile_resolver import resolve_chrome_profile
from pto_ws_client import PTOWebSocketClient
from plive_ws_client import PLiveWebSocketClient
from pto_token import extract_pto_bearer_from_har
from plive_gsid import extract_gsid_from_har
from pto_ws_mapping import canonicalize_site

# Persistent drivers
from pto_live_dom_scraper import open_pto_driver, scrape_pto_live_with_driver
from plive_dom_scraper import open_plive_driver, scrape_plive_odds_with_driver, get_plive_paths_for_selections


def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def _read_selection_keys(sel_file: Path) -> List[str]:
    try:
       raw = json.loads(sel_file.read_text(encoding="utf-8"))
   except Exception:
       return []
   if isinstance(raw, dict):
       arr = raw.get("selections")
   if isinstance(arr, list):
       return [str(x).lower() for x in arr]
   return []
   if isinstance(raw, list):
       return [str(x).lower() for x in raw]
   return []


def main():
    parser = argparse.ArgumentParser(description="Standalone live odds screen aggregator")
   parser.add_argument("--config", default="config.json", help="Optional local config (profile override)")
   parser.add_argument("--selectors", default="selectors.json")
   parser.add_argument("--refresh", type=float, default=0.5, help="Refresh interval seconds")
   parser.add_argument("--port", type=int, default=8765)
   args = parser.parse_args()

   print(f"[Init] Starting dashboard on port {args.port}...")
   print(f"[Init] Command line args: {vars(args)}")
   serve_dashboard([], port=args.port)

   lock_path = Path(".live_screen.lock")
   if lock_path.exists():
       try:
       pid_txt = lock_path.read_text(encoding="utf-8").strip()
   pid = int(pid_txt) if pid_txt.isdigit() else None
   except Exception:
       pid = None
   is_running = False
   if pid is not None:
       try:
       is_running = psutil.pid_exists(pid)
   except Exception:
       is_running = False
   if is_running:
       print("[Guard] Another instance appears to be running (lock file present). If this is stale, delete .live_screen.lock and re-run.")
   return
   else:
       print("[Guard] Stale lock detected; removing .live_screen.lock")
   try:
       lock_path.unlink(missing_ok=True)
   except Exception:
       pass
   lock_path.write_text(str(os.getpid()))

   try:
       print(f"\n[Config] Loading configuration files...")
   cfg = load_json(args.config)
   sels = load_json(args.selectors)
   print(f"[Config] Loaded config from '{args.config}': {cfg}")
   print(f"[Config] Loaded selectors from '{args.selectors}': keys = {list(sels.keys())}")
   print(f"[Config] Config keys: {list(cfg.keys())}")

   raw_pto_multi = sels.get("pto_multi")
   raw_pto = sels.get("pto")
   pto_cfgs: List[Dict[str, Any]] = []
   if isinstance(raw_pto_multi, list) and raw_pto_multi:
       pto_cfgs = [c for c in raw_pto_multi if isinstance(c, dict)]
   elif isinstance(raw_pto, dict):
       pto_cfgs = [raw_pto]
   else:
       print("[PTO] No PTO config found in selectors.json; skipping PTO DOM scraping.")

   print(f"\n[Browser] === CHROME PROFILE SETUP ===")
   user_data_dir = cfg.get("chrome_user_data_dir")
   profile_dir = cfg.get("chrome_profile_dir")
   print(f"[Browser] Config chrome_user_data_dir: {user_data_dir}")
   print(f"[Browser] Config chrome_profile_dir: {profile_dir}")
   
   if not user_data_dir or not Path(str(user_data_dir)).exists():
       print(f"[Browser] Profile path missing/invalid, resolving...")
   cud, cpd = resolve_chrome_profile()
   user_data_dir = user_data_dir or cud
   profile_dir = profile_dir or cpd
   print(f"[Browser] Resolved chrome_user_data_dir: {cud}")
   print(f"[Browser] Resolved chrome_profile_dir: {cpd}")
   
   print(f"[Browser] Final Chrome profile: user_data_dir={user_data_dir} profile_dir={profile_dir}")
   
   # Verify profile exists
   if user_data_dir:
       profile_path = Path(user_data_dir) / (profile_dir or "Profile 1")
   print(f"[Browser] Checking profile path: {profile_path}")
   print(f"[Browser] Profile exists: {profile_path.exists()}")
   print(f"[Browser] === END CHROME PROFILE SETUP ===\n")

   # Ensure types are normalized (config may contain strings)
   def _to_bool(v):
       if isinstance(v, bool):
       return v
   if isinstance(v, (int, float)):
       return bool(v)
   return str(v).strip().lower() in {"1", "true", "yes", "on"}
   pto_headless = _to_bool(cfg.get("pto_headless", False))
   plive_headless = bool(cfg.get("plive_headless", True))
   use_pto_dom = bool(cfg.get("use_pto_dom", True)) and bool(pto_cfgs)

   state_lock = Lock()
   ws_dirty = {"flag": False}
   ws_rows: List[Dict[str, Any]] = []

   # Persistent drivers
   pto_driver = None
   plive_drivers: Dict[str, Any] = {}  # One driver per sport path
   pto_tabs: List[Dict[str, Any]] = []
   selection_mtime: float = 0.0
   print(f"\n[PTO] === PTO DRIVER INITIALIZATION ===")
   print(f"[PTO] use_pto_dom: {use_pto_dom}")
   print(f"[PTO] pto_headless: {pto_headless}")
   print(f"[PTO] Available PTO configs: {len(pto_cfgs)}")
   
   if use_pto_dom:
       try:
       debug_port = None
   try:
       dp = cfg.get("chrome_debug_port")
   print(f"[PTO] Raw debug_port from config: {dp}")
   if dp:
       debug_port = int(dp)
   print(f"[PTO] Parsed debug_port: {debug_port}")
   except Exception as e:
       print(f"[PTO] Error parsing debug_port: {e}")
   debug_port = None
   selected_cfgs: List[Dict[str, Any]] = []
   try:
       sel_file = Path("sports_selection.json")
   print(f"[PTO] Checking selection file: {sel_file}")
   print(f"[PTO] Selection file exists: {sel_file.exists()}")
   
   if sel_file.exists():
       selection_mtime = sel_file.stat().st_mtime
   allowed = set(_read_selection_keys(sel_file))
   print(f"[PTO] Raw allowed selections: {allowed}")
   print(f"[PTO] Active selections: {sorted(list(allowed))}")
   
   def _ok(cfg: Dict[str, Any]) -> bool:
       k = f"{cfg.get('sport','')}:{cfg.get('market','')}".lower()
   url_match = cfg.get('url') in allowed
   key_match = k in allowed
   print(f"[PTO] Checking config: sport={cfg.get('sport')}, market={cfg.get('market')}")
   print(f"[PTO]   Key: '{k}', URL match: {url_match}, Key match: {key_match}")
   return url_match or key_match
   
   selected_cfgs = [c for c in pto_cfgs if _ok(c)]
   print(f"[PTO] Filtered PTO configs: {len(selected_cfgs)} out of {len(pto_cfgs)}")
   for i, cfg in enumerate(selected_cfgs):
       print(f"[PTO]   Config {i+1}: {cfg.get('sport')}:{cfg.get('market')} -> {cfg.get('url', 'NO_URL')}")
   else:
       print(f"[PTO] No selection file found, using empty configs")
   selected_cfgs = []
   except Exception as e:
       print(f"[PTO] Selection filter error: {e}")
   selected_cfgs = []
   print(f"[PTO] Selected PTO tabs: {len(selected_cfgs)}")
   if selected_cfgs:
       print(f"[PTO] Opening PTO driver (headless={pto_headless}, debug_port={debug_port}) ...")
   print(f"[PTO] Driver params: user_data_dir={user_data_dir}, profile_dir={profile_dir}")
   print(f"[PTO] Effective headless: {False if debug_port else pto_headless}")
   
   try:
       pto_driver = open_pto_driver(
   user_data_dir, profile_dir,
   headless=(False if debug_port else pto_headless),
   remote_debug_port=debug_port
   )
   print(f"[PTO] SUCCESS: PTO driver created successfully!")
   print(f"[PTO] Driver session ID: {pto_driver.session_id}")
   except Exception as driver_error:
       print(f"[PTO] ERROR: Failed to create PTO driver: {driver_error}")
   print(f"[PTO] Error type: {type(driver_error).__name__}")
   import traceback
   print(f"[PTO] Full traceback:")
   traceback.print_exc()
   pto_driver = None
   if pto_driver:
       try:
       first = selected_cfgs[0]
   print(f"[PTO] Opening first tab: {first.get('sport')}:{first.get('market')}")
   print(f"[PTO] First tab URL: {first['url']}")
   pto_driver.get(first["url"])  # initial navigation once
   print(f"[PTO] SUCCESS: First tab opened successfully")
   print(f"[PTO] Current window handle: {pto_driver.current_window_handle}")
   pto_tabs = [{"handle": pto_driver.current_window_handle, "cfg": first}]
   except Exception as e:
       print(f"[PTO] ERROR: Initial tab open failed: {e}")
   pto_tabs = []
   
   for i, cfg in enumerate(selected_cfgs[1:], 2):
       try:
       print(f"[PTO] Opening tab {i}: {cfg.get('sport')}:{cfg.get('market')}")
   print(f"[PTO] Tab {i} URL: {cfg['url']}")
   pto_driver.execute_script(f"window.open('{cfg['url']}', '_blank');")
   time.sleep(0.1)
   handles = pto_driver.window_handles
   print(f"[PTO] Total window handles: {len(handles)}")
   pto_tabs.append({"handle": handles[-1], "cfg": cfg})
   print(f"[PTO] SUCCESS: Tab {i} opened successfully")
   except Exception as e:
       print(f"[PTO] ERROR: Additional tab {i} open failed: {e}")
   print(f"[PTO] Total open PTO tabs: {len(pto_tabs)}")
   else:
       print(f"[PTO] ERROR: No PTO driver available, skipping tab setup")
   pto_tabs = []
   else:
       use_pto_dom = False
   except Exception as e:
       print(f"[PTO] Driver attach/open error: {e}")
   pto_driver = None
   # Initialize PLive drivers based on selections
   try:
       print(f"[PLive] Opening drivers (headless={plive_headless}) ...")
   # We'll create drivers dynamically as needed in the main loop
   except Exception as e:
       print(f"[PLive] Failed to open drivers: {e}")

   def mark_dirty():
       ws_dirty["flag"] = True

   def pto_on_event(payload: Dict[str, Any]):
       try:
       data = payload.get("data") or {}
   bet_cache = data.get("betCache")
   if not bet_cache:
       return
   entries = bet_cache if isinstance(bet_cache, list) else [bet_cache]
   for market in entries:
       listings = market.get("listings") or []
   conditions = market.get("conditions") or []
   market_label = "moneyline"
   try:
       mt = (conditions[0].get("marketType") if conditions else None) or ""
   mt_low = str(mt).lower()
   if "spread" in mt_low:
       market_label = "spread"
   elif "total" in mt_low or "over" in mt_low or "under" in mt_low:
       market_label = "total"
   except Exception:
       pass
   books: Dict[str, Dict[str, Any]] = {}
   for lst in listings:
       site_id = canonicalize_site(str(lst.get("siteId", "")))
   american = lst.get("americanOdds")
   if not site_id:
       continue
   if site_id not in books:
       books[site_id] = {"home": None, "away": None}
   if books[site_id]["home"] is None and american is not None:
       books[site_id]["home"] = str(american)
   if books:
       with state_lock:
       ws_rows.append({
   "sport": "MLB",
   "market": market_label,
   "home": "PTO Live",
   "away": "Market",
   "books": books,
   })
   mark_dirty()
   except Exception:
       return

   token = extract_pto_bearer_from_har() or ""
   if token:
       print("[PTO-WS] Token loaded; starting subscription... (expect PTO rows if mapping succeeds)")
   else:
       print("[PTO-WS] No token found; skipping WS for now. (PTO DOM will populate only if PTO driver starts successfully)")
   pto_ws = PTOWebSocketClient(on_event=pto_on_event, token_provider=lambda: token)
   pto_ws_query = (
   "subscription ($request: InputBetCacheSubscriptionRequestType) {\n"
   "  betCache(request: $request) {\n"
   "   hashCode\n"
   "   listings { siteId americanOdds }\n"
   "   conditions { marketType overUnder betValue teamId isGameBet }\n"
   "  }\n"
   "}"
   )
   try:
       if token:
       pto_ws.start(query=pto_ws_query, variables={"request": {}})
   except Exception as e:
       print(f"[PTO-WS] Start error: {e}")

   def plive_on_message(msg: str):
       mark_dirty()
   gsid = extract_gsid_from_har() or None
   auth = {"gsid": gsid} if gsid else None
   plive_ws = PLiveWebSocketClient(on_message=plive_on_message, auth=auth)
   try:
       plive_ws.start()
   except Exception as e:
       print(f"[PLive-WS] Start error: {e}")

   last_rows: List[EventOdds] = []
   last_rows_ts: float = 0.0

   allowed_books = None
   try:
       allowed_books = sels.get("allowed_books") or (sels.get("pto", {}) if isinstance(sels.get("pto"), dict) else {}).get("allowed_books")
   except Exception:
       allowed_books = None

   # Get speed settings
   speed_mode = cfg.get("speed_mode", False)
   fast_refresh = cfg.get("fast_refresh", 0.1) if speed_mode else refresh
   actual_refresh = fast_refresh if speed_mode else refresh
   
   # WebSocket integration option
   use_websocket = cfg.get("use_websocket", False)
   websocket_client = None
   
   print(f"[Speed] Speed mode: {speed_mode}, Refresh rate: {actual_refresh}s")
   print(f"[WS] WebSocket mode: {use_websocket}")
   
   # Try to initialize WebSocket if enabled
   if use_websocket:
       try:
       from pto_websocket_integration import create_pto_websocket_client
   print(f"[WS] Attempting WebSocket initialization...")
   
   # Get selections for WebSocket
   try:
       selfile = Path("sports_selection.json")
   if selfile.exists():
       allowed = set(_read_selection_keys(selfile))
   websocket_selections = list(allowed)
   websocket_client = create_pto_websocket_client(websocket_selections)
   
   if websocket_client:
       print(f"[WS]  WebSocket client initialized successfully!")
   print(f"[WS] WebSocket will provide real-time PTO data")
   else:
       print(f"[WS]  WebSocket initialization failed, falling back to DOM")
   use_websocket = False
   else:
       print(f"[WS]  No selections file found, falling back to DOM")
   use_websocket = False
   except Exception as e:
       print(f"[WS]  WebSocket setup error: {e}")
   use_websocket = False
   
   except ImportError:
       print(f"[WS]  WebSocket module not available, using DOM scraping")
   use_websocket = False
   except Exception as e:
       print(f"[WS]  WebSocket import error: {e}")
   use_websocket = False
   
   cycle_count = 0
   while True:
       cycle_count += 1
   print(f"\n[PTO] === PTO SCRAPING CYCLE #{cycle_count} ===")
   all_pto_events: List[Dict[str, Any]] = []
   print(f"[PTO] use_pto_dom: {use_pto_dom}")
   print(f"[PTO] pto_driver available: {pto_driver is not None}")
   print(f"[PTO] pto_tabs count: {len(pto_tabs) if pto_tabs else 0}")
   
   # Use WebSocket data if available, otherwise fall back to DOM scraping
   if use_websocket and websocket_client and websocket_client.is_ready():
       try:
       print(f"[PTO] Using WebSocket data source...")
   ws_events = websocket_client.get_events_for_main_system()
   all_pto_events.extend(ws_events)
   print(f"[PTO]  WebSocket provided {len(ws_events)} events")
   
   if ws_events:
       print(f"[PTO] Sample WebSocket events:")
   for i, event in enumerate(ws_events[:2]):
       print(f"[PTO]   WS Event {i+1}: {event.get('sport')} {event.get('market')} - {event.get('home')} vs {event.get('away')} ({len(event.get('books', {}))} books)")
   
   except Exception as e:
       print(f"[PTO]  WebSocket data error: {e}")
   print(f"[PTO] Falling back to DOM scraping...")
   use_websocket = False
   
   elif use_pto_dom and pto_driver is not None and pto_tabs:
       try:
       selfile = Path("sports_selection.json")
   if selfile.exists():
       mtime = selfile.stat().st_mtime
   if (not selection_mtime) or (mtime > selection_mtime):
       print("[PTO] Selection change detected -> rebuilding tabs...")
   selection_mtime = mtime
   try:
       cur = pto_driver.current_window_handle
   except Exception:
       cur = None
   for h in list(pto_driver.window_handles):
       if not cur or h != cur:
       try:
       pto_driver.switch_to.window(h)
   pto_driver.close()
   except Exception:
       pass
   if cur:
       try:
       pto_driver.switch_to.window(cur)
   except Exception:
       pass
   allowed = set(_read_selection_keys(selfile))
   raw_multi = sels.get("pto_multi") or []
   new_cfgs = [c for c in raw_multi if isinstance(c, dict) and ((c.get("url") in allowed) or (f"{c.get('sport','')}:{c.get('market','')}".lower() in allowed))]
   pto_tabs = []
   if new_cfgs:
       try:
       first = new_cfgs[0]
   pto_driver.get(first["url"])  # navigate
   pto_tabs = [{"handle": pto_driver.current_window_handle, "cfg": first}]
   except Exception:
       pto_tabs = []
   for cfg in new_cfgs[1:]:
       try:
       pto_driver.execute_script(f"window.open('{cfg['url']}', '_blank');")
   time.sleep(0.1)
   handles = pto_driver.window_handles
   pto_tabs.append({"handle": handles[-1], "cfg": cfg})
   except Exception:
       continue
   print(f"[PTO] Open PTO tabs: {len(pto_tabs)}")
   except Exception as e:
       print(f"[PTO] Hot-reload error: {e}")

   # Round-robin scrape tabs
   print(f"[PTO] Scraping {len(pto_tabs)} PTO tabs...")
   for i, tab in enumerate(pto_tabs, 1):
       try:
       print(f"[PTO] Scraping tab {i}/{len(pto_tabs)}: {tab['cfg'].get('sport')}:{tab['cfg'].get('market')}")
   pto_driver.switch_to.window(tab["handle"])
   pto_cfg = tab["cfg"]
   print(f"[PTO] Tab URL: {pto_cfg['url']}")
   
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
   timeout=12,
   allowed_books=allowed_books,
   live_only=True,
   )
   market_name = pto_cfg.get("market") or "moneyline"
   sport_name = pto_cfg.get("sport") or "unknown"
   for e in pto_events:
       e.setdefault("market", market_name)
   e.setdefault("sport", sport_name)
   e.setdefault("ptoUrl", pto_cfg.get("url"))
   print(f"[PTO] SUCCESS: Tab {i} ({sport_name}:{market_name}) events: {len(pto_events)}")
   if pto_events:
       print(f"[PTO] Sample events from tab {i}:")
   for j, event in enumerate(pto_events[:2]):
       print(f"[PTO]   Event {j+1}: {event.get('home')} vs {event.get('away')} - books: {list(event.get('books', {}).keys())}")
   all_pto_events.extend(pto_events)
   except Exception as e:
       print(f"[PTO] ERROR: Scrape error on tab {i}: {e}")
   import traceback
   traceback.print_exc()
   continue
   print(f"[PTO] Total PTO events collected: {len(all_pto_events)}")
   else:
       print(f"[PTO] ERROR: PTO scraping skipped - use_pto_dom:{use_pto_dom}, driver:{pto_driver is not None}, tabs:{len(pto_tabs) if pto_tabs else 0}")
   print(f"[PTO] === END PTO SCRAPING CYCLE ===\n")

   print(f"\n[PLive] === PLIVE SCRAPING CYCLE ===")
   plive_events: List[Dict[str, Any]] = []
   # Get current selections and determine PLive paths
   try:
       selfile = Path("sports_selection.json")
   print(f"[PLive] Reading selections from: {selfile}")
   current_selections = []
   if selfile.exists():
       print(f"[PLive] Selection file exists, reading...")
   allowed = set(_read_selection_keys(selfile))
   current_selections = list(allowed)
   print(f"[PLive] Raw selections from file: {current_selections}")
   else:
       print(f"[PLive] ERROR: Selection file does not exist!")
   
   plive_paths = get_plive_paths_for_selections(current_selections)
   print(f"[PLive] Final PLive paths to scrape: {plive_paths}")
   
   # Create or reuse drivers for each unique path
   for path in plive_paths:
       print(f"[PLive] Processing path: {path}")
   if path not in plive_drivers:
       try:
       print(f"[PLive] Creating new driver for {path}...")
   plive_drivers[path] = open_plive_driver(user_data_dir=None, profile_dir=None, headless=plive_headless)
   print(f"[PLive] SUCCESS: Created driver for {path}")
   except Exception as e:
       print(f"[PLive] ERROR: Failed to create driver for {path}: {e}")
   import traceback
   traceback.print_exc()
   continue
   else:
       print(f"[PLive] Reusing existing driver for {path}")
   
   driver = plive_drivers[path]
   if driver is not None:
       try:
       print(f"[PLive] Scraping {path}...")
   cur = scrape_plive_odds_with_driver(driver, sports_paths=[path])
   sport_name = path.replace("#!/sport/", "Sport_")
   print(f"[PLive] SUCCESS: {sport_name} events scraped: {len(cur)}")
   if cur:
       print(f"[PLive] Sample events from {sport_name}:")
   for i, event in enumerate(cur[:2]):  # Show first 2 events
   print(f"[PLive]   Event {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
   plive_events += cur
   except Exception as e:
       print(f"[PLive] ERROR: {sport_name} scrape error: {e}")
   import traceback
   traceback.print_exc()
   else:
       print(f"[PLive] ERROR: No driver available for {path}")
   
   # Clean up unused drivers
   active_paths = set(plive_paths)
   for path in list(plive_drivers.keys()):
       if path not in active_paths:
       try:
       plive_drivers[path].quit()
   del plive_drivers[path]
   print(f"[PLive] Cleaned up unused driver for {path}")
   except Exception:
       pass
   
   except Exception as e:
       print(f"[PLive] Selection processing error: {e}")

   print(f"[PLive] Total PLive events collected: {len(plive_events)}")
   print(f"[PLive] === END PLIVE SCRAPING CYCLE ===\n")
   
   print(f"\n[Merge] === DATA MATCHING ===")
   merged_bck = (plive_events or [])
   print(f"[Merge] PLive events: {len(merged_bck)}")
   print(f"[Merge] PTO events: {len(all_pto_events)}")
   
   if merged_bck:
       print(f"[Merge] Sample PLive events:")
   for i, event in enumerate(merged_bck[:3]):
       print(f"[Merge]   PLive {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
   
   if all_pto_events:
       print(f"[Merge] Sample PTO events:")
   for i, event in enumerate(all_pto_events[:3]):
       print(f"[Merge]   PTO {i+1}: {event.get('sport')} - {event.get('home')} vs {event.get('away')} ({event.get('market')})")
   
   matches = match_events(merged_bck, all_pto_events)
   print(f"[Merge] Successful matches: {len(matches)}")
   print(f"[Merge] === END DATA MATCHING ===\n")

   combined: List[EventOdds] = []
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
   b_books = b.get("books", {})
   betbck_prices = b_books.get("betbck") or {"home": None, "away": None}
   eo.books["betbck"] = {"home": betbck_prices.get("home"), "away": betbck_prices.get("away")}
   for book_name, sides in (p.get("books", {}) or {}).items():
       key = book_name.lower().strip().replace(" ", "_")
   eo.books[key] = {"home": sides.get("home"), "away": sides.get("away")}
   combined.append(eo)
   else:
       for b in merged_bck:
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

   live_rows = [e for e in combined if (e.books.get("betbck", {}).get("home") or e.books.get("betbck", {}).get("away"))]
   if not live_rows and last_rows and ((_time.time() - last_rows_ts) < 60):
       live_rows = last_rows
   else:
       if live_rows:
       last_rows = live_rows
   last_rows_ts = _time.time()

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

   rows = build_best_table(live_rows)
   print(f"[UI] Pushing {len(rows)} rows to dashboard")
   push_rows(rows)
   # Use faster refresh in speed mode
   sleep_time = actual_refresh if 'actual_refresh' in locals() else max(0.25, float(args.refresh))
   if speed_mode and cycle_count % 10 == 0:
       print(f"[Speed] Cycle #{cycle_count} - using {sleep_time}s refresh")
   time.sleep(sleep_time)
   finally:
       try:
       if Path(".live_screen.lock").exists():
       Path(".live_screen.lock").unlink(missing_ok=True)
   except Exception:
       pass


if __name__ == "__main__":
    main()

