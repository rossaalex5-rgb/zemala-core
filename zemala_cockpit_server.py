import http.server
import json
import os

PORT = 5000
LEDGER_PATH = "core/ledger.jsonl"

class ZemalaCockpitHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            blocks = []
            if os.path.exists(LEDGER_PATH):
                with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                blocks.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            
            response_data = {
                "system": "ZEMALA_SSOT_V3",
                "cadence": "3.47s",
                "status": "PASS",
                "total_blocks": len(blocks),
                "latest_block": blocks[-1] if blocks else None
            }
            self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), ZemalaCockpitHandler)
    print(f"[ZEMALA COCKPIT] Status server active on port {PORT}. Cadence: 3.47s.")
    server.serve_forever()
