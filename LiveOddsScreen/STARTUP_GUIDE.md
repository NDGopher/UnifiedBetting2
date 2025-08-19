# LiveOddsScreen - Quick Startup Guide

## 🎯 **SYSTEM IS NOW FULLY WORKING!**

The encoding issues are fixed and your system is operational. Here's the correct startup sequence:

---

## 🚀 **STEP-BY-STEP STARTUP**

### **Step 1: Start PTO Chrome with Debugging** 
```bash
python start_pto_chrome.py
```

**What this does:**
- Kills any existing Chrome processes
- Starts Chrome with your PTO profile
- Enables debug port 9223
- Opens PTO odds screen
- Keeps Chrome running for the live screen to connect to

**Expected output:**
```
🚀 Starting PTO Chrome with Debug
==================================================
✅ Found Chrome at: C:\Program Files\Google\Chrome\Application\chrome.exe
🔪 Killing all Chrome processes...
✅ Killed X Chrome processes
🌐 Launching Chrome: [command details]
⏳ Waiting for Chrome debug port 9223 to be ready...
✅ Chrome debug port 9223 is ready!
✅ Chrome is ready for PTO integration!
```

**IMPORTANT:** Leave this Chrome window open! Don't close it.

### **Step 2: Launch LiveOddsScreen**
```bash
start_live_screen.bat
```

**What this does:**
- Runs system diagnostics
- Checks all configurations
- Launches the sports selector GUI
- Starts the live odds dashboard

### **Step 3: Select Your Sports**
In the GUI that opens:
- Choose whatever sports you want (MLB, WNBA, EPL, etc.)
- Select markets (moneyline, spread, total)
- Click "Start"

### **Step 4: Access Dashboard**
Open your browser to: `http://127.0.0.1:8765/dashboard.html`

---

## 📊 **WHAT YOU'LL SEE**

### **Console Output (Good Signs):**
```
[Init] Starting dashboard on port 8765...
[Config] Loading configuration files...
[Browser] Profile exists: True
[PTO] Selected PTO tabs: 6
[PTO] Opening PTO driver (headless=True, debug_port=9223)...
Dashboard at http://127.0.0.1:8765/dashboard.html
[PTO] SUCCESS: PTO driver created successfully!
[PLive-Debug] Final PLive paths to scrape: ['#!/sport/1', '#!/sport/2']
[PLive] SUCCESS: Created driver for #!/sport/1
[PLive] SUCCESS: Sport_1 events scraped: 15
[Merge] PLive events: 15
[Merge] PTO events: 12
[Merge] Successful matches: 8
```

### **Dashboard:**
- Live updating table with odds
- Multiple sportsbooks (FanDuel, DraftKings, etc.)
- Best odds highlighted
- Real-time updates

---

## 🛠️ **TROUBLESHOOTING**

### **"Can't reach this page" Error:**
1. Make sure the dashboard URL is exactly: `http://127.0.0.1:8765/dashboard.html`
2. Check console for "Dashboard at http://127.0.0.1:8765/dashboard.html"
3. Try refreshing the page after 10 seconds

### **No PTO Data:**
```
[PTO] ERROR: Failed to create PTO driver: connection refused
```
**Solution:** Make sure you started PTO Chrome first with `python start_pto_chrome.py`

### **No PLive Data:**
```
[PLive] ERROR: Failed to create driver for #!/sport/X
```
**Solution:** This is usually network/firewall related. PLive drivers should work headless.

### **No Matches:**
```
[Merge] Successful matches: 0
```
**Solution:** Check that both PLive and PTO have data for the same sports.

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Chrome started with debugging (Step 1)
- [ ] LiveOddsScreen launched successfully (Step 2)  
- [ ] Sports selected in GUI (Step 3)
- [ ] Dashboard accessible at `http://127.0.0.1:8765/dashboard.html` (Step 4)
- [ ] Console shows "Dashboard at http://127.0.0.1:8765/dashboard.html"
- [ ] Console shows PTO tabs being created
- [ ] Console shows PLive drivers being created
- [ ] Dashboard shows live odds data

---

## 🎯 **SUCCESS INDICATORS**

When everything is working correctly, you'll see:

1. **Multiple PTO tabs** being scraped for your selected sports
2. **PLive paths** corresponding to your selections  
3. **Events being matched** between the two sources
4. **Live dashboard** updating with odds from multiple books
5. **Real-time updates** as odds change

---

## 🎉 **YOU'RE READY!**

Your system is now:
- ✅ Fully dynamic (any sport selections work)
- ✅ Extensively debugged (clear logging)
- ✅ Windows compatible (encoding fixed)
- ✅ Real-time (live updates)
- ✅ Professional grade (robust error handling)

**Just follow the 4 steps above and you'll have live odds comparison working!** 🚀
