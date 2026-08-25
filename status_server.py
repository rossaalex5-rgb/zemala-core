import http.server
import socketserver
import json
import os

PORT = 8080

class ZemalaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
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
        print(f"[ZEMALA Server] Status-API aktiv auf Port {PORT}...")
        httpd.serve_forever()
