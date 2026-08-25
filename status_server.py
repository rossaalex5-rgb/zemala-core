import http.server
import socketserver
import json
import os

PORT = 8080

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>ZEMALA Core // Live-Telemetrie</title>
    <style>
        body { background-color: #0b0b0f; color: #00ffcc; font-family: monospace; padding: 20px; }
        h1 { border-bottom: 2px solid #00ffcc; padding-bottom: 10px; }
        .card { background: #12121a; border: 1px solid #1a1a2e; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,255,204,0.1); }
        .metric { font-size: 1.5em; color: #ffcc00; }
        .status-optimal { color: #00ff66; font-weight: bold; }
    </style>
</head>
<body>
    <h1>ZEMALA Core // Stufe 100</h1>
    <div class="card">
        <h3>System-Status</h3>
        <p>Zustand: <span id="status" class="status-optimal">Laden...</span></p>
        <p>Feldintegrität: <span id="integrity" class="metric">Laden...</span></p>
        <p>Aktives Level: <span id="level">Laden...</span></p>
    </div>
    <div class="card">
        <h3>Letztes Kryptosiegel</h3>
        <pre id="seal">Laden...</pre>
    </div>
    <script>
        async function fetchStatus() {
            try {
                let response = await fetch('/status');
                let data = await response.json();
                document.getElementById('status').innerText = data.status;
                document.getElementById('integrity').innerText = data.field_integrity;
                document.getElementById('level').innerText = data.level;
                document.getElementById('seal').innerText = JSON.stringify(data.latest_seal || {}, null, 2);
            } catch (e) {
                document.getElementById('status').innerText = "Verbindungsfehler";
            }
        }
        fetchStatus();
        setInterval(fetchStatus, 3470); // Im 3.47s Takt aktualisieren
    </script>
</body>
</html>
"""

class ZemalaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status = {
                "system": "ZEMALA Core",
                "status": "Stable",
                "level": "100",
                "field_integrity": "100%"
            }
            if os.path.exists("ledger_seal.json"):
                with open("ledger_seal.json", "r") as f:
                    status["latest_seal"] = json.load(f)
            self.wfile.write(json.dumps(status, indent=2).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ZemalaHandler) as httpd:
        print(f"[ZEMALA Server] Live-Dashboard & Status-API aktiv auf Port {PORT}...")
        httpd.serve_forever()
