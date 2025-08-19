import json
import threading
from typing import Callable, Optional

import websocket  # type: ignore


class PLiveWebSocketClient:
    def __init__(self, on_message: Callable[[str], None], auth: Optional[dict] = None):
        self.on_message = on_message
        self.auth = auth or {}
        self._ws = None
        self._thread = None

    def start(self, url: str = "wss://plive.becoms.co/socket", headers: Optional[dict] = None):
        hdrs = []
        if headers:
            for k, v in headers.items():
                hdrs.append(f"{k}: {v}")
        if self.auth.get("gsid"):
            hdrs.append(f"Cookie: gsid={self.auth['gsid']}")

        def _run():
            def _on_open(ws):
                pass
            def _on_message(ws, msg):
                try:
                    self.on_message(msg)
                except Exception:
                    pass
            def _on_error(ws, err):
                pass
            def _on_close(ws, code, msg):
                pass
            self._ws = websocket.WebSocketApp(
                url,
                header=hdrs,
                on_open=_on_open,
                on_message=_on_message,
                on_error=_on_error,
                on_close=_on_close,
            )
            self._ws.run_forever(ping_interval=20, ping_timeout=10)
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            if self._ws:
                self._ws.close()
        except Exception:
            pass
import threading
from typing import Callable, Optional

import socketio


class PLiveWebSocketClient:
    """Socket.IO v4 client to Pandora/Ganchrow. Uses python-socketio client.
    We'll join namespaces/rooms as we discover them, and forward incoming events.
    """

    def __init__(self, base_url: str = "https://pandora.ganchrow.com", on_message: Optional[Callable[[str], None]] = None, auth: Optional[dict] = None):
        self.base_url = base_url
        self.on_message = on_message
        self.sio = socketio.Client(reconnection=True)
        self.thread: Optional[threading.Thread] = None
        self.auth = auth or {}

        @self.sio.event
        def connect():
            # Connected to base namespace
            pass

        @self.sio.on('*')
        def catch_all(event, data=None):
            if self.on_message:
                try:
                    self.on_message(str({"event": event, "data": data}))
                except Exception:
                    pass

        @self.sio.event
        def disconnect():
            pass

    def start(self):
        def run():
            try:
                self.sio.connect(self.base_url, transports=["websocket"], wait_timeout=10, auth=self.auth)
                self.sio.wait()
            except Exception:
                pass
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        try:
            self.sio.disconnect()
        except Exception:
            pass

