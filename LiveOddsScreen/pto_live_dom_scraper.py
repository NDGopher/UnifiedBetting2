import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterable

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager


@dataclass
class PTOSelectors:
    event_row_selector: str
    home_team_selector: str
    away_team_selector: str
    market_container_selector: Optional[str] = None
    price_selector: Optional[str] = None
    # Optional, when team names are inside two spans with class like MuiTypography-odds; if set, we will prefer title attribute
    team_title_selector: Optional[str] = None
    # Selector to capture all book cells in a row
    book_cell_selector: Optional[str] = None
    # Selector for the image/icon that carries the book name via alt
    book_icon_selector: Optional[str] = None
    # Selector for odds text spans within a book cell
    book_odds_value_selector: Optional[str] = None
    # Live indicator selector (if present in row -> consider live)
    live_indicator_selector: Optional[str] = '[data-testid="SensorsIcon"], .css-ctyr61'


def canonicalize_book_name(site_id: str) -> str:
    s = (site_id or '').lower().strip()
    mapping = {
        'fanduel': 'fanduel',
        'fan_duel': 'fanduel',
        'fd': 'fanduel',
        'mgm': 'betmgm',
        'betmgm': 'betmgm',
        'draftkings': 'draftkings',
        'dk': 'draftkings',
        'caesars': 'caesars',
        'espnbet': 'espnbet',
        'espn_bet': 'espnbet',
        'pinnacle': 'pinnacle',
        'betonline': 'betonline',
        'bet_online': 'betonline',
        'betrivers': 'betrivers',
        'bet_rivers': 'betrivers',
        'bet365': 'bet365',
        'bovada': 'bovada',
        'circa': 'circa',
        'hardrock': 'hardrock',
        'hard_rock': 'hardrock',
        'betbck': 'betbck',
    }
    for k, v in mapping.items():
        if k in s:
            return v
    return s.replace(' ', '_')


def _build_driver(user_data_dir: Optional[str], profile_dir: Optional[str], headless: bool = True, remote_debug_port: Optional[int] = None) -> webdriver.Chrome:
    chrome_options = Options()
    # If attaching to an existing real Chrome via remote debug, use debuggerAddress to avoid automation banner
    if remote_debug_port:
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{int(remote_debug_port)}")
        # When attaching, do not set prefs or experimental fingerprint options; keep it minimal
    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    if profile_dir:
        chrome_options.add_argument(f"--profile-directory={profile_dir}")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Speed/quiet tweaks
    chrome_prefs = {
        # Keep images on when not headless so visible PTO looks correct
        "profile.managed_default_content_settings.images": 0 if not headless else 2,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    # Only disable images in headless mode to reduce bandwidth; keep on when visible for proper layout
    if headless:
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    # Reduce selenium fingerprints only when we launch our own Chrome. When attaching to an
    # already-open Chrome via remote debugging, these options are rejected by newer drivers.
    if not remote_debug_port:
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
    # When attaching to remote debug chrome, do not set headless (we're controlling an already-open real Chrome)
    if headless and not remote_debug_port:
        chrome_options.add_argument("--headless=new")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        if not remote_debug_port:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
    except Exception:
        pass
    return driver


def open_pto_driver(user_data_dir: Optional[str], profile_dir: Optional[str], headless: bool = True, remote_debug_port: Optional[int] = None) -> webdriver.Chrome:
    """Open or attach to a PTO browser session (reused across cycles)."""
    return _build_driver(user_data_dir, profile_dir, headless=headless, remote_debug_port=remote_debug_port)


def _extract_line_from_text(row_text: str, market_label: str) -> Optional[str]:
    t = (row_text or "").lower()
    # Totals like 7.5, 8.0, 2.5 etc
    if "total" in market_label or "over" in t or "under" in t or "o/u" in t:
        import re
        nums = re.findall(r"\b\d{1,2}(?:\.\d)?\b", row_text)
        for n in nums:
            try:
                val = float(n)
                if 0.5 <= val <= 20.0:
                    return n
            except Exception:
                continue
    # Spreads like +1.5 / -1.5 → line 1.5
    if "spread" in market_label or "handicap" in t:
        import re
        m = re.search(r"[+\-]\d+(?:\.\d)?", row_text)
        if m:
            try:
                return str(abs(float(m.group(0))))
            except Exception:
                return m.group(0)
    return None


def scrape_pto_live_with_driver(
    driver: webdriver.Chrome,
    pto_url: str,
    selectors: PTOSelectors,
    timeout: int = 30,
    allowed_books: Optional[Iterable[str]] = None,
    live_only: bool = True,
) -> List[Dict[str, Any]]:
    wait = WebDriverWait(driver, timeout)
    try:
        try:
            cur = driver.current_url
        except Exception:
            cur = None
        if not cur or (pto_url and not cur.startswith(pto_url)):
            driver.get(pto_url)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selectors.event_row_selector)))
            rows = driver.find_elements(By.CSS_SELECTOR, selectors.event_row_selector)
        except Exception:
            rows = driver.find_elements(By.CSS_SELECTOR, '[virtualrowstart], .MuiBox-root')
        # One-shot zoom-out to minimize need for scroll/virtualization
        try:
            driver.execute_script("if(!window.__zoomed){document.body.style.zoom='0.8';window.__zoomed=true}")
        except Exception:
            pass
        # Do not deep scroll; rely on live rows being visible and WebSocket updates
        events: List[Dict[str, Any]] = []
        for row in rows:
            try:
                if live_only and selectors.live_indicator_selector:
                    _live = row.find_elements(By.CSS_SELECTOR, selectors.live_indicator_selector)
                    if not _live:
                        continue
            except Exception:
                pass
            try:
                if selectors.home_team_selector and selectors.away_team_selector:
                    home_text = row.find_element(By.CSS_SELECTOR, selectors.home_team_selector).text.strip()
                    away_text = row.find_element(By.CSS_SELECTOR, selectors.away_team_selector).text.strip()
                else:
                    titles = row.find_elements(By.CSS_SELECTOR, selectors.team_title_selector or 'span[title]')
                    if len(titles) >= 2:
                        h_title = titles[0].get_attribute('title') or titles[0].text
                        a_title = titles[1].get_attribute('title') or titles[1].text
                        home_text = (h_title or '').strip()
                        away_text = (a_title or '').strip()
                    else:
                        continue
            except Exception:
                continue

            markets: List[Dict[str, Any]] = []
            books: Dict[str, Dict[str, Optional[str]]] = {}
            if selectors.book_cell_selector and selectors.book_icon_selector and selectors.book_odds_value_selector:
                try:
                    book_cells = row.find_elements(By.CSS_SELECTOR, selectors.book_cell_selector)
                    for cell in book_cells:
                        try:
                            icon = cell.find_element(By.CSS_SELECTOR, selectors.book_icon_selector)
                            book_name = (icon.get_attribute('alt') or icon.get_attribute('aria-label') or '').strip()
                            if not book_name:
                                parent_label = cell.get_attribute('aria-label') or ''
                                book_name = parent_label.strip()
                            if not book_name:
                                continue
                            canonical = canonicalize_book_name(book_name)
                            if allowed_books is not None and canonical not in set(map(canonicalize_book_name, allowed_books)):
                                continue
                            vals = cell.find_elements(By.CSS_SELECTOR, selectors.book_odds_value_selector)
                            odds_vals = [v.text.strip() for v in vals if v.text.strip()]
                            home_val = odds_vals[0] if len(odds_vals) >= 1 else None
                            away_val = odds_vals[1] if len(odds_vals) >= 2 else None
                            if home_val or away_val:
                                books[canonical] = {"home": home_val, "away": away_val}
                        except Exception:
                            continue
                except Exception:
                    pass
            if not books:
                try:
                    shallow = row.find_elements(By.CSS_SELECTOR, '.MuiTypography-oddsRobotoMono')
                    vals = [v.text.strip() for v in shallow if v.text.strip()]
                    if len(vals) >= 2:
                        books['pto'] = {"home": vals[0], "away": vals[1]}
                except Exception:
                    pass

            market_label = "moneyline"
            try:
                row_text_full = row.text
                row_text = row_text_full.lower()
                if "spread" in row_text:
                    market_label = "spread"
                elif "total" in row_text or "o/u" in row_text:
                    market_label = "total"
            except Exception:
                row_text_full = ""

            events.append({
                "home": home_text,
                "away": away_text,
                "markets": markets,
                "market": market_label,
                "books": books,
                "line": _extract_line_from_text(row_text_full, market_label),
            })
        return events
    except Exception:
        return []



def scrape_pto_live(
    pto_url: str,
    selectors: PTOSelectors,
    user_data_dir: Optional[str] = None,
    profile_dir: Optional[str] = None,
    timeout: int = 30,
    headless: bool = True,
    allowed_books: Optional[Iterable[str]] = None,
    live_only: bool = True,
) -> List[Dict[str, Any]]:
    driver = open_pto_driver(user_data_dir, profile_dir, headless=headless)
    try:
        return scrape_pto_live_with_driver(driver, pto_url, selectors, timeout=timeout, allowed_books=allowed_books, live_only=live_only)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

