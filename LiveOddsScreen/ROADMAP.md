# LiveOddsScreen — Roadmap and Handoff

This captures exactly where we left off and how to resume on any machine.

## Quickstart (fresh machine)
1) Install Python 3.10+ and Git.
2) Clone repo and open `LiveOddsScreen/`.
3) Double‑click `start_live_screen.bat`.
   - Installs requirements automatically.
   - Opens the Selector GUI → pick leagues/markets and Window mode (Embedded recommended) → Start.
   - Embedded app window opens the dashboard.
4) Change selections live: click “Change” in the dashboard header, re‑select, press Start. The runner hot‑reloads PTO tabs.

### Optional (reuse real Chrome session for PTO)
- Launch Chrome once with remote debugging, e.g.:
  `chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\Users\\YOURUSER\\AppData\\Local\\PTO_Chrome_Profile" --profile-directory="Profile 1"`
- Add to `config.json`:
  `{ "chrome_user_data_dir": "C:\\Users\\YOURUSER\\AppData\\Local\\PTO_Chrome_Profile", "chrome_profile_dir": "Profile 1", "chrome_debug_port": 9222 }`

## What’s done
- Persistent PTO and PLive sessions; no deep scrolling; light DOM reads.
- Selector GUI (two columns), preferences; unified launcher with embedded window (PyWebView) or external browser.
- Spread/Total “line” extraction; dashboard renders lines; SSE updates with no flicker.
- Header shows Active selections; “Change” launches selector and hot‑reloads selections.
- PTO tabs open only after selections; nothing opens if selector is closed.

## Next steps (priority)
1) PTO WebSocket mapping (primary data path)
   - Map `betCache.conditions` → market (moneyline/spread/total), line (total/spread), team side (home/away), and group by game.
   - Prefer WS over DOM; add reconnection/backoff and resubscription.
2) PLive WebSocket parsing (BetBCK)
   - Parse market prices via WS; keep DOM as fallback only.
3) Matching & filters
   - Stronger team aliases across leagues (MLS/Liga MX, NBA/NHL).
   - Filter table to games supported by both PTO and BetBCK.
4) UI/UX
   - Presets in selector; Save/Load last; “Select All ML/Spread/Total”.
   - EV column (de‑vig books; compute BetBCK edge vs average/best).
5) Reliability & ops
   - Heartbeat/status in header (PTO WS / PLive WS / DOM fallback).
   - Auto‑restart stuck tabs; structured rotating logs; safe cadence.
6) Packaging
   - Single .exe via PyInstaller with icon/version.

## Daily test checklist
- Selector → Start: embedded window opens; header shows correct Active list.
- Change → Start: header updates within ~5s; only selected tabs remain.
- Prices flow smoothly; Spread/Total lines visible; BetBCK column populated.
- No repeated window opens; CPU stable; no deep scroll.

## Troubleshooting
- Embedded opens a browser: PyWebView missing—BAT installs it; re‑run.
- External browser fails: pick Embedded, or ensure Firefox/Chrome exists on PATH.
- PTO blank/blocked: attach to existing Chrome via remote debug using your logged‑in profile.
- Header stale after Change: wait ~5s; confirm `sports_selection.json` updated (runner hot‑reloads on mtime).

## Edit pointers
- Orchestrator: `run_live_screen.py`
- PTO DOM: `pto_live_dom_scraper.py`
- PLive DOM: `plive_dom_scraper.py`
- PTO WS: `pto_ws_client.py`
- PLive WS: `plive_ws_client.py`
- Dashboard: `dashboard.py`, `dashboard.html`
- Selector/Launcher: `sports_selector.py`, `app_launcher.py`, `start_live_screen.bat`

Note: Target architecture is WS‑first, DOM‑fallback. Keep selections minimal during tests for lowest latency.
