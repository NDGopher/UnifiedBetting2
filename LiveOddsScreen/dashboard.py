import http.server
import json
import socketserver
import threading
import queue
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
import os
import subprocess
import subprocess

from rich import print
from schema import EventOdds


_latest_payload: Dict[str, Any] = {"rows": []}
_client_queues: Set["queue.Queue[str]"] = set()
_client_lock = threading.Lock()


def build_best_table(events: List[EventOdds]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for e in events:
        best = e.best_side_with_value()
        avg = e.average_odds()
        rows.append({
            "mode": "team",
            "sport": e.sport,
            "market": e.market.upper(),
            "line": e.line,
            "team": e.home,
            "opponent": e.away,
            "side": "home",
            "best": best.get("home"),
            "avg": avg.get("home"),
            "books": e.books,
        })
        rows.append({
            "mode": "team",
            "sport": e.sport,
            "market": e.market.upper(),
            "line": e.line,
            "team": e.away,
            "opponent": e.home,
            "side": "away",
            "best": best.get("away"),
            "avg": avg.get("away"),
            "books": e.books,
        })
    def parse_american(val: str) -> Optional[int]:
        try:
            s = val.strip()
            if s.startswith("+"):
                return int(s[1:])
            return int(s)
        except Exception:
            return None
    def sort_key(r: Dict[str, Any]):
        # 1) prefer rows where betbck is best
        b = r.get("best") or ""
        is_bck_best = 1 if (isinstance(b, str) and b.lower().startswith("betbck ")) else 0
        # 2) among those, sort by how much betbck beats the average
        advantage = -999999
        try:
            avg = r.get("avg")
            betbck_price = None
            books = r.get("books") or {}
            bpair = (books.get("betbck") or {})
            side = r.get("side") or "home"
            if side in bpair and bpair[side] is not None:
                betbck_price = parse_american(str(bpair[side]))
            avg_num = float(avg) if avg is not None else None
            if betbck_price is not None and avg_num is not None:
                advantage = betbck_price - avg_num
        except Exception:
            pass
        return (is_bck_best, advantage)
    rows.sort(key=sort_key, reverse=True)
    return rows


class _SSEHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global _latest_payload
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: "queue.Queue[str]" = queue.Queue()
            with _client_lock:
                _client_queues.add(q)
            try:
                # Send the latest snapshot immediately
                first = json.dumps(_latest_payload)
                self.wfile.write(f"data: {first}\n\n".encode("utf-8"))
                self.wfile.flush()
                while True:
                    data = q.get()
                    self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with _client_lock:
                    _client_queues.discard(q)
            return
        if self.path == "/selections":
            try:
                sel_path = Path("sports_selection.json")
                payload: Dict[str, Any] = {"selections": []}
                if sel_path.exists():
                    try:
                        raw = json.loads(sel_path.read_text(encoding="utf-8"))
                        if isinstance(raw, dict):
                            payload = {"selections": raw.get("selections", [])}
                        elif isinstance(raw, list):
                            payload = {"selections": raw}
                    except Exception:
                        pass
                data = json.dumps(payload)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            except Exception:
                self.send_response(500); self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/open":
            try:
                length = int(self.headers.get('Content-Length', '0'))
                raw = self.rfile.read(length).decode('utf-8') if length else '{}'
                data = json.loads(raw or '{}')
                cmd = str(data.get('cmd') or '')
                links = data.get('links') or []
                if isinstance(links, list) and cmd:
                    for url in links:
                        try:
                            if cmd == 'chrome':
                                subprocess.Popen(["cmd", "/c", "start", "", url])
                            elif cmd == 'firefox':
                                subprocess.Popen(["cmd", "/c", "start", "firefox", url])
                            elif cmd == 'comet':
                                subprocess.Popen(["cmd", "/c", "start", "comet", url])
                        except Exception:
                            continue
                self.send_response(204)
                self.end_headers()
            except Exception:
                self.send_response(400)
                self.end_headers()
            return
        if self.path == "/select":
            # Spawn selector in a separate process; runner will hot-reload on file change
            try:
                subprocess.Popen([os.environ.get("PYTHON", "python"), "-u", "sports_selector.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
                self.send_response(204)
                self.end_headers()
            except Exception:
                self.send_response(500); self.end_headers()
            return
        return super().do_GET()


def _broadcast(payload: Dict[str, Any]):
    data = json.dumps(payload)
    with _client_lock:
        for q in list(_client_queues):
            try:
                q.put_nowait(data)
            except Exception:
                pass


def serve_dashboard(rows: List[Dict[str, Any]], port: int = 8765):
    global _latest_payload
    out = {"generated": True, "rows": rows}
    _latest_payload = out
    # Write output.json next to dashboard.html (script directory)
    script_dir = Path(__file__).parent.resolve()
    out_path = script_dir / "output.json"
    try:
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    except Exception:
        pass

    def run_server():
        class ThreadingServer(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
        os.chdir(script_dir)
        with ThreadingServer(("127.0.0.1", port), _SSEHandler) as httpd:
            print(f"Dashboard at http://127.0.0.1:{port}/dashboard.html")
            httpd.serve_forever()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    return t


def push_rows(rows: List[Dict[str, Any]]):
    global _latest_payload
    _latest_payload = {"rows": rows}
    # Write output.json for manual refresh/debug
    script_dir = Path(__file__).parent.resolve()
    out_path = script_dir / "output.json"
    try:
        out_path.write_text(json.dumps(_latest_payload, indent=2), encoding="utf-8")
    except Exception:
        pass
    _broadcast(_latest_payload)

