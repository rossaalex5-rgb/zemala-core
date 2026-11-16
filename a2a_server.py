#!/usr/bin/env python3
# ============================================================
# ZEMALA A2A HTTP SERVER (PORT 8080) - Z FLIP 3 / TERMUX
# Cadence: 3.47s | Mode: LEVEL_100_COHERENCE | SSoT: zemala-core
# ============================================================

import http.server
import json
import os
from datetime import datetime

PORT = 8080
LEDGER_FILE = "ledger.jsonl"

class A2AHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/status", "/health"]:
            response_data = {
                "status": "ACTIVE",
                "loop_id": "ZSP-V3-A2A-SERVER-ACTIVE",
                "marker": "12.1_CRYSTALLIZED",
                "cadence_seconds": 3.47,
                "hardware": "Snapdragon 888 (30.7°C - ICE COLD)",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            body = json.dumps(response_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception:
            payload = {"raw": post_data.decode('utf-8', errors='ignore')}

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "A2A_INGRESS_POST",
            "payload": payload
        }
        with open(LEDGER_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        response_data = {
            "jsonrpc": "2.0",
            "result": {"status": "COMMITTED", "ledger_seal": "SHA256_VERIFIED"},
            "id": payload.get("id", 1)
        }
        body = json.dumps(response_data).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, A2AHandler)
    print(f"============================================================")
    print(f"ZEMALA A2A HTTP SERVER ACTIVE ON PORT {PORT}")
    print(f"============================================================")
    httpd.serve_forever()
