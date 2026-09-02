from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from zemala_core import ZemalaLedger, ZemalaMCPBridge

class ZemalaBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/mcp/latest":
            try:
                ledger = ZemalaLedger("zemala_core.jsonl")
                mcp = ZemalaMCPBridge(ledger)
                resources = mcp.get_mcp_resources()
                
                response_data = json.dumps(resources[0], sort_keys=True)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response_data.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "NOT_FOUND"}).encode("utf-8"))
            
    def log_message(self, format, *args):
        # Unterdrückt Standard-Stdout-Rauschen für saubere Systemhygiene
        return

def run_bridge(port=8000):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, ZemalaBridgeHandler)
    print(f"[ZEMALA HMI BRIDGE] Aktiv auf http://127.0.0.1:{port}/mcp/latest")
    httpd.serve_forever()

if __name__ == '__main__':
    run_bridge()
