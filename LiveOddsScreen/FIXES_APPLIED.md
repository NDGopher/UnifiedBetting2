# LiveOddsScreen - Critical Fixes Applied

## Summary of Issues and Solutions

### 🔧 Major Issues Fixed

#### 1. **PLive Sports Selection Problem**
**Issue**: PLive was hardcoded to scrape MLB (sport/1) and Soccer (sport/220), ignoring user selections
**Solution**: 
- Added dynamic sports path mapping in `plive_dom_scraper.py`
- Created `PLIVE_SPORT_PATHS` dictionary mapping sports to PLive URLs:
  - MLB: `#!/sport/1`
  - WNBA/NBA: `#!/sport/2` 
  - NFL: `#!/sport/3`
  - NHL: `#!/sport/4`
  - Soccer/MLS: `#!/sport/220`
- Added `get_plive_paths_for_selections()` function to dynamically determine which sports to scrape
- Modified main loop in `run_live_screen.py` to use selected sports only

#### 2. **PTO Chrome Profile Connection Issues**
**Issue**: Chrome debug port conflicts preventing PTO driver connection
**Solution**:
- Changed debug port from 9222 to 9223 in `config.json`
- Created `start_pto_chrome.py` utility to properly launch Chrome with debugging
- Added process cleanup to kill conflicting Chrome instances
- Improved error handling in PTO driver initialization

#### 3. **Stale PLive Events**
**Issue**: PLive sometimes shows old/locked events that don't update
**Solution**:
- Added `_refresh_page_if_stale()` function to detect and refresh stale content
- Automatically refreshes when >60% of events are locked/stale
- Integrated into main scraping loop for automatic maintenance

#### 4. **Poor Team Name Matching for WNBA**
**Issue**: No team aliases for WNBA teams causing match failures
**Solution**:
- Added comprehensive WNBA team aliases to `team_matching.py`
- Includes full names, abbreviations, and common nicknames
- Added WNBA hints for better league detection in PLive

#### 5. **Inefficient Resource Management**
**Issue**: Multiple drivers running unnecessarily, slow updates
**Solution**:
- Changed from fixed drivers to dynamic driver management
- Creates/destroys drivers based on selected sports
- Improved memory usage and reduced conflicts

### 📁 New Files Created

1. **`start_pto_chrome.py`** - Utility to launch Chrome with proper debugging
2. **`start_pto_chrome.bat`** - Windows batch file for easy Chrome startup  
3. **`setup_fix.py`** - Comprehensive setup and verification script
4. **`FIXES_APPLIED.md`** - This documentation file

### ⚙️ Configuration Changes

**`config.json` Updated:**
```json
{
  "chrome_user_data_dir": "C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile",
  "chrome_profile_dir": "Profile 1", 
  "chrome_debug_port": 9223,
  "pto_headless": false,
  "plive_headless": true
}
```

### 🚀 Usage Instructions

#### Step 1: Setup Chrome for PTO
```bash
# Kill any existing Chrome processes and start with debugging
python start_pto_chrome.py
# OR
start_pto_chrome.bat
```

#### Step 2: Run LiveOddsScreen
```bash
# Use the existing launcher
python app_launcher.py
# OR  
start_live_screen.bat
```

#### Step 3: Select Sports
- Choose MLB and/or WNBA markets
- Select desired bet types (moneyline, spread, total)
- Click Start

### 🔍 Technical Details

#### PLive Sports Mapping
- **MLB**: `#!/sport/1` - Baseball umbrella (MLB/LMB)
- **WNBA**: `#!/sport/2` - Basketball (includes NBA/WNBA)
- **NFL**: `#!/sport/3` - Football
- **NHL**: `#!/sport/4` - Hockey  
- **Soccer**: `#!/sport/220` - Top Soccer leagues

#### Team Name Matching
Added WNBA team aliases including:
- "aces" → "las vegas aces"
- "liberty" → "new york liberty"  
- "mercury" → "phoenix mercury"
- "storm" → "seattle storm"
- And many more...

#### Stale Event Detection
- Monitors ratio of locked/stale events
- Refreshes page when >60% are stale
- Reduces dead data in the display

### 🎯 Expected Results

After applying these fixes:

1. **PLive will only scrape selected sports** (no more unwanted Soccer data)
2. **PTO connection should work reliably** (proper profile and debug port)
3. **WNBA events will match properly** (comprehensive team aliases)
4. **Stale events will refresh automatically** (keeps data fresh)
5. **Better performance** (dynamic resource management)

### 🛠️ Troubleshooting

If issues persist:

1. **Run setup verification:**
   ```bash
   python setup_fix.py
   ```

2. **Check Chrome processes:**
   ```bash
   tasklist | findstr chrome
   ```

3. **Verify PTO profile exists:**
   ```
   C:\Users\steph\AppData\Local\PTO_Chrome_Profile\Profile 1
   ```

4. **Check sports selection:**
   Look at `sports_selection.json` for your choices

### 📈 Performance Improvements

- Dynamic driver creation (only for selected sports)
- Automatic stale event refresh
- Reduced Chrome process conflicts
- Better error handling and recovery
- Optimized scraping loops

---

## Result: A Much More Reliable and Focused System

The LiveOddsScreen should now:
- ✅ Only scrape the sports you actually selected
- ✅ Connect to PTO properly using your logged-in profile
- ✅ Match WNBA teams correctly  
- ✅ Refresh stale data automatically
- ✅ Run faster with better resource management

**The main problem was that the system was hardcoded to certain sports instead of using your selections. Now it dynamically adapts to what you choose and should work much better for MLB and WNBA live odds comparison.**
