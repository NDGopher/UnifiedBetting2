#!/usr/bin/env python3
"""
Clean app launcher without indentation issues
"""

import sys
import time
import json
import subprocess
from pathlib import Path
import threading

PORT = 8765

def run_selector():
    """Run sports selector and return results"""
    try:
        import sports_selector
        from sports_selector import main as selector_main
        
        # Clear existing selection
        try:
            Path("sports_selection.json").unlink(missing_ok=True)
        except:
            pass
        
        # Run selector
        selector_main()
        
        # Read results
        try:
            data = json.loads(Path("sports_selection.json").read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return bool(data.get("selections")), data
            if isinstance(data, list):
                return bool(data), {"selections": data, "opts": {}}
        except:
            pass
        
        return False, {"selections": [], "opts": {}}
        
    except Exception as e:
        print(f"ERROR: Selector failed: {e}")
        return False, {"selections": [], "opts": {}}

def wait_for_dashboard(port, timeout=30):
    """Wait for dashboard to be ready"""
    import http.client
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1.5)
            conn.request("GET", "/dashboard.html")
            resp = conn.getresponse()
            ok = (200 <= resp.status < 300)
            conn.close()
            if ok:
                return True
        except:
            pass
        time.sleep(0.3)
    
    return False

def open_browser(port, mode="embedded"):
    """Open browser to dashboard"""
    url = f"http://127.0.0.1:{port}/dashboard.html"
    
    if mode == "embedded":
        try:
            import webview
            window = webview.create_window(
                "Live Odds Screen",
                url,
                width=1200,
                height=800,
                min_size=(1024, 700),
                resizable=True,
            )
            webview.start()
            return
        except:
            mode = "chrome"
    
    try:
        if mode == "chrome":
            subprocess.Popen(["cmd", "/c", "start", "", "chrome", url], shell=False)
            return
        if mode == "firefox":
            subprocess.Popen(["cmd", "/c", "start", "", "firefox", url], shell=False)
            return
    except:
        pass
    
    try:
        import webbrowser
        webbrowser.open(url)
    except:
        pass

def pipe_output(proc, prefix="[Runner]"):
    """Pipe subprocess output"""
    def stream(pipe, printer):
        try:
            for line in iter(pipe.readline, b""):
                try:
                    decoded = line.decode("utf-8", errors="replace").rstrip()
                except:
                    decoded = str(line)
                printer(f"{prefix} {decoded}")
        except:
            pass
    
    t1 = threading.Thread(target=stream, args=(proc.stdout, print), daemon=True)
    t2 = threading.Thread(target=stream, args=(proc.stderr, print), daemon=True)
    t1.start()
    t2.start()

def main():
    """Main app launcher"""
    try:
        import webview
    except:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview>=4.4"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    
    # Run selector
    has_sel, payload = run_selector()
    if not has_sel:
        print("[Selector] No selections made; exiting.")
        return
    
    # Update config with selector options
    opts = payload.get("opts") or {}
    try:
        cfg_path = Path("config.json")
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
        
        def to_bool(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return bool(v)
            s = str(v).strip().lower()
            return s in {"1", "true", "yes", "on"}
        
        if "chrome_debug_port" in opts and opts["chrome_debug_port"] not in (None, ""):
            try:
                cfg["chrome_debug_port"] = int(opts["chrome_debug_port"])
            except:
                pass
        
        if "pto_headless" in opts:
            cfg["pto_headless"] = to_bool(opts["pto_headless"])
        
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except:
        pass
    
    # Start runner
    cmd = [sys.executable, "-u", "run_live_screen.py", "--port", str(PORT)]
    print(f"[Launcher] Starting: {' '.join(cmd)}")
    runner = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pipe_output(runner)
    
    try:
        if not wait_for_dashboard(PORT, timeout=30.0):
            print(f"[Launcher] Dashboard not ready on 127.0.0.1:{PORT} after timeout.")
        
        mode = (payload.get("opts") or {}).get("open_browser") or "embedded"
        open_browser(PORT, mode)
    finally:
        try:
            runner.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
