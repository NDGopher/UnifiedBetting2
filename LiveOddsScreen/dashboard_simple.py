#!/usr/bin/env python3
"""
Simple dashboard server for live odds display
"""

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/dashboard.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Odds Screen</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .status { background: #27ae60; color: white; padding: 10px; margin: 10px 0; border-radius: 3px; }
        .selections { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .live-data { background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Live Odds Screen Dashboard</h1>
        <p>Real-time odds comparison between PLive and PTO</p>
    </div>
    
    <div class="status">
        ✅ Dashboard is running and ready for live odds data
    </div>
    
    <div class="selections">
        <h3>📋 Your Sports Selections</h3>
        <p>The system will pull live odds for your selected sports and markets.</p>
        <p><strong>Status:</strong> Simplified mode - dashboard framework ready</p>
    </div>
    
    <div class="live-data">
        <h3>📊 Live Odds Data</h3>
        <p>Live odds comparison will appear here once the full system is running.</p>
        <p><em>Note: This is a simplified dashboard to verify the framework works.</em></p>
    </div>
    
    <script>
        // Simple auto-refresh
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
        
        elif self.path == "/api/data":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = {
                "status": "running",
                "timestamp": time.time(),
                "message": "Dashboard framework ready"
            }
            self.wfile.write(json.dumps(data).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass

def serve_dashboard_sync(initial_data, port=8765):
    """Serve dashboard synchronously"""
    try:
        server = HTTPServer(('127.0.0.1', port), DashboardHandler)
        print(f"[Dashboard] Server started on http://127.0.0.1:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"[Dashboard] Server error: {e}")

if __name__ == "__main__":
    serve_dashboard_sync([], 8765)
