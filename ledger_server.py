import http.server
import json
import hashlib
import socketserver

PORT = 8080
LEDGER_FILE = "clean_ledger.jsonl"

def load_ledger():
    entries = []
    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return entries

class LedgerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        ledger = load_ledger()
        if self.path == "/blocks":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(ledger, indent=2).encode("utf-8"))
        elif self.path == "/verify":
            valid = True
            expected_prev = "0" * 64
            for i, block in enumerate(ledger):
                if block["index"] != i or block["previous_hash"] != expected_prev:
                    valid = False
                    break
                block_data = {
                    "index": block["index"],
                    "timestamp": block["timestamp"],
                    "previous_hash": block["previous_hash"],
                    "payload": block["payload"]
                }
                computed = hashlib.sha256(json.dumps(block_data, sort_keys=True).encode("utf-8")).hexdigest()
                if computed != block["hash"]:
                    valid = False
                    break
                expected_prev = computed
            
            response = {"status": "VALID" if valid else "INVALID", "total_blocks": len(ledger)}
            self.send_response(200 if valid else 500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found. Use /blocks or /verify"}).encode("utf-8"))

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    print(f"Starting Read-only Ledger Node Interface on port {PORT}...")
    with socketserver.TCPServer(("", PORT), LedgerHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
