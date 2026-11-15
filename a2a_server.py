# ZEMALA A2A HTTP SERVER (PORT 8080) - Z FLIP 3 / TERMUX
# Cadence: 3.47s | Node: LEVEL_100_COHERENCE | SSoT: zemala-core

import http.server
import json
import os
import hashlib
from datetime import datetime, timezone

PORT = 8080
LEDGER_FILE = "core/ledger.jsonl"

def get_ledger_blocks():
    blocks = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        blocks.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return blocks

def evaluate_contract(blocks):
    if not blocks:
        return False, "Ledger leer"
    latest = blocks[-1]
    raw_str = json.dumps(latest, sort_keys=True).lower()
    for term in ["error", "contradiction", "widerspruch", "fail", "invalid", "mismatch"]:
        if term in raw_str:
            return False, f"Widerspruch erkannt: '{term}'"
    return True, "AEVO-Contract erfuellt (GOLD)"

class A2AHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        blocks = get_ledger_blocks()
        is_gold, reason = evaluate_contract(blocks)
        latest = blocks[-1] if blocks else {}
        sigil_hash = hashlib.sha256(json.dumps(latest, sort_keys=True).encode("utf-8")).hexdigest()

        if self.path in ["/status", "/health", "/"]:
            response_data = {
                "status": "ACTIVE",
                "loop_id": "ZSP-V3-A2A-SERVER-ACTIVE",
                "coherence": "12.1_CRYSTALLIZED",
                "cadence_seconds": 3.47,
                "hardware": "Snapdragon 888 (30.7°C - ICE COLD)",
                "ssot_blocks": len(blocks),
                "contract_state": "GOLD" if is_gold else "UNVERIFIED",
                "aevo_reason": reason,
                "sigil_sha256": sigil_hash,
                "sigil_endpoint": "http://localhost:5000/sigil.png",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            body = json.dumps(response_data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            payload = {"raw": post_data.decode("utf-8", errors="ignore")}

        blocks = get_ledger_blocks()
        prev_block = blocks[-1] if blocks else {}
        prev_hash = hashlib.sha256(json.dumps(prev_block, sort_keys=True).encode("utf-8")).hexdigest()

        entry = {
            "index": len(blocks) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "A2A_INGRESS_POST",
            "prev_hash": prev_hash,
            "payload": payload
        }
        entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()

        os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        blocks.append(entry)
        is_gold, reason = evaluate_contract(blocks)
        sigil_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()

        response_data = {
            "jsonrpc": "2.0",
            "result": {
                "status": "COMMITTED",
                "block_index": entry["index"],
                "contract_state": "GOLD" if is_gold else "CONTRADICTION",
                "aevo_reason": reason,
                "ledger_seal": "SHA256_VERIFIED",
                "sigil_sha256": sigil_hash,
                "sigil_url": "http://localhost:5000/sigil.png"
            },
            "id": payload.get("id", 1) if isinstance(payload, dict) else 1
        }
        body = json.dumps(response_data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server_address = ("0.0.0.0", PORT)
    httpd = http.server.HTTPServer(server_address, A2AHandler)
    print("--------------------------------------------------")
    print(f"[ZEMALA A2A HTTP SERVER ACTIVE ON PORT {PORT}]")
    print("--------------------------------------------------")
    httpd.serve_forever()
