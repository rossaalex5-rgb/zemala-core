import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class ZemalaAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            try:
                with open("ledger.jsonl", "r") as f:
                    lines = f.readlines()
                total_events = len(lines)
                last_event = json.loads(lines[-1]) if lines else {}
                
                response_data = {
                    "status": "Stufe 100",
                    "total_events": total_events,
                    "last_event": last_event,
                    "field_integrity": "100%"
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found. Use /status")

def run(server_class=HTTPServer, handler_class=ZemalaAPIHandler, port=8082):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"[ZEMALA API] Lausche auf Port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
