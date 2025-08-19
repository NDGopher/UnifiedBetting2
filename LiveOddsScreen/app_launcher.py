import sys
import time
import json
import subprocess
from pathlib import Path
import threading

PORT = 8765


def run_selector() -> tuple[bool, dict]:
    try:
        import sports_selector  # noqa: F401
        from sports_selector import main as selector_main
        try:
            Path("sports_selection.json").unlink(missing_ok=True)
        except Exception:
            pass
        selector_main()
    except Exception:
        pass
    try:
        data = json.loads(Path("sports_selection.json").read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return bool(data.get("selections")), data
        if isinstance(data, list):
            return bool(data), {"selections": data, "opts": {}}
    except Exception:
        return False, {"selections": [], "opts": {}}


def wait_for_dashboard(port: int, timeout_s: float = 30.0) -> bool:
    start = time.time()
    import http.client
    path = "/dashboard.html"
    while time.time() - start < timeout_s:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1.5)
            conn.request("GET", path)
            resp = conn.getresponse()
            ok = (200 <= resp.status < 300)
            conn.close()
            if ok:
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False


def open_window(port: int, mode: str):
    url = f"http://127.0.0.1:{port}/dashboard.html"
    if mode == "embedded":
        try:
            import webview  # type: ignore
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
        except Exception:
            mode = "chrome"
    try:
        if mode == "firefox":
            subprocess.Popen(["cmd", "/c", "start", "", "firefox", url], shell=False)
            return
        if mode == "chrome":
            subprocess.Popen(["cmd", "/c", "start", "", "chrome", url], shell=False)
            return
        if mode == "comet":
            subprocess.Popen(["cmd", "/c", "start", "", "comet", url], shell=False)
            return
    except Exception:
        pass
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


def _pipe_output(proc: subprocess.Popen, prefix: str = "[Runner]"):
    def _stream(pipe, printer):
        try:
            for line in iter(pipe.readline, b""):
                try:
                    decoded = line.decode("utf-8", errors="replace").rstrip()
                except Exception:
                    decoded = str(line)
                printer(f"{prefix} {decoded}")
        except Exception:
            pass
    t1 = threading.Thread(target=_stream, args=(proc.stdout, print), daemon=True)
    t2 = threading.Thread(target=_stream, args=(proc.stderr, print), daemon=True)
    t1.start(); t2.start()


def main():
    try:
        import webview  # type: ignore
    except Exception:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview>=4.4"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    has_sel, payload = run_selector()
    if not has_sel:
        print("[Selector] No selections made; exiting.")
        return
    opts = payload.get("opts") or {}
    try:
        cfg_path = Path("config.json")
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
        # Normalize types from selector opts (strings → proper types)
        def _to_bool(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return bool(v)
            s = str(v).strip().lower()
            return s in {"1", "true", "yes", "on"}
        if "chrome_debug_port" in opts and opts["chrome_debug_port"] not in (None, ""):
            try:
                cfg["chrome_debug_port"] = int(opts["chrome_debug_port"])
            except Exception:
                pass
        if "pto_headless" in opts:
            cfg["pto_headless"] = _to_bool(opts["pto_headless"])
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass

    # Start runner in same console and stream logs
    cmd = [sys.executable, "-u", "run_live_screen.py", "--port", str(PORT)]
    print(f"[Launcher] Starting: {' '.join(cmd)}")
    runner = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _pipe_output(runner)

    try:
        if not wait_for_dashboard(PORT, timeout_s=30.0):
            print(f"[Launcher] Dashboard not ready on 127.0.0.1:{PORT} after timeout.")
        mode = (payload.get("opts") or {}).get("open_browser") or "embedded"
        open_window(PORT, mode)
    finally:
        try:
            runner.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()


