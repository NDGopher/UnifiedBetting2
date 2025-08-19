#!/usr/bin/env python3
"""
Clean version of PLive DOM scraper with proper indentation
"""

import re
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# PLive sport path mappings
PLIVE_SPORT_PATHS = {
    "mlb": "#!/sport/1",
    "baseball": "#!/sport/1", 
    "nba": "#!/sport/3",
    "basketball": "#!/sport/3",
    "wnba": "#!/sport/3",  # WNBA uses same basketball path
    "nfl": "#!/sport/2", 
    "football": "#!/sport/2",
    "nhl": "#!/sport/4",
    "hockey": "#!/sport/4",
    "soccer": "#!/sport/220",
    "football_soccer": "#!/sport/220",
    "tennis": "#!/sport/5",
    "mma": "#!/sport/6",
    "ufc": "#!/sport/6",
    "boxing": "#!/sport/7",
    "golf": "#!/sport/8",
    "olympics": "#!/sport/9",
    "rugby": "#!/sport/10",
}

SPORT_LABEL = {
    "#!/sport/1": "MLB", 
    "#!/sport/2": "NFL",
    "#!/sport/3": "NBA/WNBA",
    "#!/sport/4": "NHL", 
    "#!/sport/5": "TENNIS",
    "#!/sport/6": "MMA/UFC",
    "#!/sport/7": "BOXING",
    "#!/sport/8": "GOLF",
    "#!/sport/9": "OLYMPICS",
    "#!/sport/10": "RUGBY",
    "#!/sport/220": "SOCCER",
}

WNBA_HINTS = ["wnba", "women", "mercury", "liberty", "sky", "sparks", "lynx", "fever", "dream", "sun", "wings", "aces"]

def _build_driver(user_data_dir: Optional[str], profile_dir: Optional[str], headless: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    if profile_dir:
        chrome_options.add_argument(f"--profile-directory={profile_dir}")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--disable-gpu")
    # Speed/quiet tweaks
    chrome_prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    if headless:
        chrome_options.add_argument("--headless=new")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def open_plive_driver(user_data_dir: Optional[str], profile_dir: Optional[str], headless: bool = True) -> webdriver.Chrome:
    return _build_driver(user_data_dir, profile_dir, headless=headless)

def discover_plive_sports(driver: webdriver.Chrome, base_url: str = "https://plive.becoms.co/live/") -> Dict[str, str]:
    """
    Dynamically discover available sports from the PLive sports menu.
    Returns a mapping of sport names to their URLs.
    """
    print("[PLive] Discovering available sports from menu...")
    
    try:
        # Navigate to main page to load sports menu
        driver.get(base_url)
        time.sleep(3)  # Let page load
        
        # Find the sports menu
        sports_menu = driver.find_element(By.CSS_SELECTOR, "ul.sports-menu")
        sport_items = sports_menu.find_elements(By.CSS_SELECTOR, "li.sports-menu__item")
        
        sport_mapping = {}
        for item in sport_items:
            try:
                # Get the sport link
                link = item.find_element(By.CSS_SELECTOR, "a.sports-menu__item-link")
                sport_url = link.get_attribute("href")
                sport_id = link.get_attribute("data-id")
                
                # Get the sport title
                title_elem = link.find_element(By.CSS_SELECTOR, "span.title")
                sport_title = title_elem.text.strip()
                
                # Get event count
                count_elem = link.find_element(By.CSS_SELECTOR, "span.count")
                event_count = count_elem.text.strip()
                
                if sport_url and sport_title:
                    # Convert URL to the format we need (e.g., #!sport/1 -> #!/sport/1)
                    formatted_url = sport_url.replace("#!", "#!/")
                    sport_mapping[sport_title.lower()] = formatted_url
                    
                    print(f"[PLive] Discovered: {sport_title} -> {formatted_url} ({event_count} events)")
                    
            except Exception as e:
                print(f"[PLive] Error processing sport item: {e}")
                continue
        
        print(f"[PLive] Total sports discovered: {len(sport_mapping)}")
        return sport_mapping
        
    except Exception as e:
        print(f"[PLive] Error discovering sports: {e}")
        # Fallback to known mappings
        return {
            "baseball": "#!/sport/1",
            "football": "#!/sport/3", 
            "basketball": "#!/sport/2",
            "soccer": "#!/sport/5",
            "tennis": "#!/sport/8",
            "golf": "#!/sport/7",
            "mma": "#!/sport/27"
        }

def get_plive_paths_for_selections(selections: List[str], driver: Optional[webdriver.Chrome] = None) -> List[str]:
    """Convert sports selections like ['mlb:moneyline', 'wnba:spread'] to PLive sport paths."""
    print(f"\n[PLive-Debug] === SELECTION ANALYSIS ===")
    print(f"[PLive-Debug] Raw selections received: {selections}")
    
    sports = set()
    for sel in selections:
        print(f"[PLive-Debug] Processing selection: '{sel}'")
        if ":" in sel:
            sport = sel.split(":")[0].lower().strip()
            market = sel.split(":")[1].lower().strip() if len(sel.split(":")) > 1 else "unknown"
            sports.add(sport)
            print(f"[PLive-Debug]   -> Extracted sport: '{sport}', market: '{market}'")
        else:
            print(f"[PLive-Debug]   -> No ':' found in selection, skipping")
    
    print(f"[PLive-Debug] Unique sports extracted: {list(sports)}")
    
    # Try to discover sports dynamically if driver is available
    if driver:
        try:
            sport_mapping = discover_plive_sports(driver)
        except Exception as e:
            print(f"[PLive-Debug] Dynamic discovery failed: {e}")
            sport_mapping = {}
    else:
        sport_mapping = {}
    
    # Fallback to static mappings if dynamic discovery failed
    if not sport_mapping:
        sport_mapping = {
            "mlb": "#!/sport/1",
            "baseball": "#!/sport/1", 
            "nba": "#!/sport/2",
            "basketball": "#!/sport/2",
            "wnba": "#!/sport/2",  # WNBA uses same basketball path
            "nfl": "#!/sport/3", 
            "football": "#!/sport/3",
            "nhl": "#!/sport/4",
            "hockey": "#!/sport/4",
            "soccer": "#!/sport/5",
            "tennis": "#!/sport/8",
            "golf": "#!/sport/7",
            "mma": "#!/sport/27",
            "ufc": "#!/sport/27"
        }
    
    # Add common abbreviations to the discovered sports mapping
    if sport_mapping:
        # Common sport abbreviations
        abbreviations = {
            "mlb": "baseball",
            "nba": "basketball", 
            "wnba": "basketball",
            "nfl": "football",
            "nhl": "hockey",
            "ufc": "mma"
        }
        
        for abbrev, full_name in abbreviations.items():
            if full_name in sport_mapping and abbrev not in sport_mapping:
                sport_mapping[abbrev] = sport_mapping[full_name]
                print(f"[PLive-Debug] Added abbreviation: {abbrev} -> {full_name} -> {sport_mapping[full_name]}")
    
    paths = []
    for sport in sports:
        print(f"[PLive-Debug] Looking up PLive path for sport: '{sport}'")
        
        # Try exact match first
        if sport in sport_mapping:
            path = sport_mapping[sport]
            if path not in paths:
                paths.append(path)
                print(f"[PLive-Debug]   SUCCESS: Mapped '{sport}' -> '{path}'")
            else:
                print(f"[PLive-Debug]   WARNING: Path '{path}' already added for '{sport}'")
        else:
            # Try partial matches (e.g., "mlb" matches "baseball")
            matched = False
            for known_sport, path in sport_mapping.items():
                if sport in known_sport or known_sport in sport:
                    if path not in paths:
                        paths.append(path)
                        print(f"[PLive-Debug]   SUCCESS: Partial match '{sport}' -> '{known_sport}' -> '{path}'")
                        matched = True
                        break
            
            if not matched:
                print(f"[PLive-Debug]   ERROR: No PLive mapping found for sport: '{sport}'")
                print(f"[PLive-Debug]   Available mappings: {list(sport_mapping.keys())}")
    
    # Fallback to MLB if no valid sports found
    if not paths:
        print(f"[PLive-Debug] WARNING: No valid paths found, using fallback: ['#!/sport/1']")
        paths = ["#!/sport/1"]
    
    print(f"[PLive-Debug] Final PLive paths to scrape: {paths}")
    for path in paths:
        # Extract sport name from path for display
        sport_name = path.replace("#!/sport/", "Sport_")
        print(f"[PLive-Debug]   {path} -> {sport_name}")
    print(f"[PLive-Debug] === END SELECTION ANALYSIS ===\n")
    
    return paths

def _looks_like_team(text: str) -> bool:
    """Check if text looks like a team name"""
    if not text or len(text.strip()) < 2:
        return False
    
    text = text.strip().upper()
    
    # Filter out obvious non-team text
    non_team_patterns = [
        r'\d+TH\s+QTR', r'\d+ST\s+QTR', r'\d+ND\s+QTR', r'\d+RD\s+QTR',
        r'QUARTER', r'HALF', r'OVERTIME', r'FINAL', r'LIVE', r'ENDED',
        r'^\d+$', r'^\d+:\d+$', r'^\+?\d+\.?\d*$', r'^[+-]?\d+\.?\d*$'
    ]
    
    for pattern in non_team_patterns:
        if re.search(pattern, text):
            return False
    
    # More lenient: allow single words that look like team names
    if len(text.split()) == 1 and len(text) >= 3:
        return True
    
    return len(text.split()) <= 4  # Most team names are 1-4 words

def _infer_league_from_text(text_content: str) -> str:
    """Infer the league/sport from page text content"""
    text_lower = text_content.lower()
    
    # Check for WNBA hints first (more specific)
    for hint in WNBA_HINTS:
        if hint in text_lower:
            return "WNBA"
    
    # Then check for other sports
    if any(word in text_lower for word in ["nba", "lakers", "warriors", "celtics", "bulls"]):
        return "NBA"
    elif any(word in text_lower for word in ["mlb", "yankees", "dodgers", "red sox", "giants"]):
        return "MLB"
    elif any(word in text_lower for word in ["nfl", "patriots", "cowboys", "steelers", "packers"]):
        return "NFL"
    elif any(word in text_lower for word in ["nhl", "rangers", "bruins", "kings", "hawks"]):
        return "NHL"
    
    return "UNKNOWN"

def _refresh_page_if_stale(driver: webdriver.Chrome, max_stale_events: int = 3) -> bool:
    """Check if page has too many stale/locked events and refresh if needed"""
    try:
        print("[PLive] Checking for stale events...")
        
        # Look for event rows
        event_rows = driver.find_elements(By.CSS_SELECTOR, "tr.oddsTableTr, .event-row, .game-row")
        if not event_rows:
            print("[PLive] No event rows found, trying alternative selectors...")
            event_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr, .match-row")
        
        if len(event_rows) == 0:
            print("[PLive] No events found on page")
            return False
        
        print(f"[PLive] Found {len(event_rows)} total events")
        
        stale_count = 0
        for row in event_rows:
            try:
                row_text = row.text.lower()
                if any(indicator in row_text for indicator in ["locked", "ended", "final", "suspended"]):
                    stale_count += 1
            except:
                continue
        
        stale_percentage = (stale_count / len(event_rows)) * 100 if event_rows else 0
        print(f"[PLive] Stale events: {stale_count}/{len(event_rows)} ({stale_percentage:.1f}%)")
        
        # Refresh if >40% stale or more than max_stale_events
        should_refresh = stale_count > max_stale_events or stale_percentage > 40
        
        if should_refresh:
            print(f"[PLive] Refreshing page due to {stale_count} stale events ({stale_percentage:.1f}%)")
            driver.refresh()
            time.sleep(3)  # Wait for page to reload
            return True
        else:
            print(f"[PLive] Page looks fresh, continuing...")
            return False
            
    except Exception as e:
        print(f"[PLive] Error checking stale events: {e}")
        return False

def scrape_plive_odds_with_driver(
    driver: webdriver.Chrome,
    base_url: str = "https://plive.becoms.co/live/",
    sports_paths: Optional[List[str]] = None,
    timeout: int = 25,
    selectors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Scrape PLive odds using an existing driver"""
    if sports_paths is None:
        sports_paths = ["#!/sport/1"]  # Default to MLB
    
    # Use default selectors if none provided
    if selectors is None:
        selectors = {
            "event_row_selector": "div.event-list__item__details__container",
            "home_team_selector": "div.event-list__item__details__teams__team__container:first-child p[data-testid='top-team-details']",
            "away_team_selector": "div.event-list__item__details__teams__team__container:last-child p[data-testid='bottom-team-details']",
            "moneyline_selector": "div.offerings.market--two-row.market-3",
            "spread_selector": "div.offerings.market--two-row.market-6", 
            "total_selector": "div.offerings.market--two-row.market-5",
            "price_selector": "div.odds div.odd span.emphasis.pane"
        }
    
    all_events = []
    
    for sport_path in sports_paths:
        print(f"\n[PLive] === SCRAPING SPORT PATH: {sport_path} ===")
        sport_name = SPORT_LABEL.get(sport_path, f"Sport({sport_path})")
        print(f"[PLive] Sport: {sport_name}")
        
        try:
            url = base_url + sport_path
            print(f"[PLive] Loading URL: {url}")
            
            driver.get(url)
            time.sleep(5)  # Let page load
            
            # Wait for content to load using the correct selector
            try:
                WebDriverWait(driver, timeout).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, selectors["event_row_selector"])
                )
                print("[PLive] Page content loaded")
            except TimeoutException:
                print("[PLive] Warning: Timeout waiting for content, proceeding anyway")
            
            # Find all event rows using the correct selector
            event_rows = driver.find_elements(By.CSS_SELECTOR, selectors["event_row_selector"])
            print(f"[PLive] Found {len(event_rows)} potential event rows")
            
            # Debug: analyze first few rows
            for i, row in enumerate(event_rows[:3]):
                try:
                    row_text = row.text
                    print(f"[PLive-Debug] Row {i+1} text: {repr(row_text[:100])}")
                except Exception as e:
                    print(f"[PLive-Debug] Error reading row {i+1}: {e}")
            
            # Extract events from this sport
            sport_events = []
            for row in event_rows:
                try:
                    # Extract team names
                    home_team_elem = row.find_element(By.CSS_SELECTOR, selectors["home_team_selector"])
                    away_team_elem = row.find_element(By.CSS_SELECTOR, selectors["away_team_selector"])
                    
                    home_team = home_team_elem.text.strip()
                    away_team = away_team_elem.text.strip()
                    
                    if not home_team or not away_team:
                        continue
                    
                    # Extract moneyline odds (market-3)
                    moneyline_odds = []
                    try:
                        ml_container = row.find_element(By.CSS_SELECTOR, selectors["moneyline_selector"])
                        ml_prices = ml_container.find_elements(By.CSS_SELECTOR, selectors["price_selector"])
                        for price_elem in ml_prices:
                            odds_text = price_elem.text.strip()
                            if odds_text and odds_text != "":
                                moneyline_odds.append(odds_text)
                    except Exception as e:
                        print(f"[PLive-Debug] Error extracting moneyline: {e}")
                    
                    # Create event
                    event = {
                        "sport": sport_name,
                        "home": home_team,
                        "away": away_team,
                        "market": "moneyline",
                        "books": {
                            "plive": {
                                "home": moneyline_odds[0] if len(moneyline_odds) > 0 else None,
                                "away": moneyline_odds[1] if len(moneyline_odds) > 1 else None
                            }
                        },
                        "source": "plive",
                        "path": sport_path
                    }
                    
                    sport_events.append(event)
                    
                except Exception as e:
                    print(f"[PLive-Debug] Error processing row: {e}")
                    continue
            
            print(f"[PLive] Extracted {len(sport_events)} events from {sport_name}")
            all_events.extend(sport_events)
            
        except Exception as e:
            print(f"[PLive] Error scraping {sport_path}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"[PLive] Total events scraped: {len(all_events)}")
    return all_events

if __name__ == "__main__":
    # Test the functions
    selections = ["mlb:moneyline", "wnba:spread"]
    paths = get_plive_paths_for_selections(selections)
    print(f"Test result: {paths}")
