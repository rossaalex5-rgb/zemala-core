import http.server
import socketserver
import json
import os

DIRECTORY = "."

# --- MASTER MANIFEST BINDING ---
import json
import socket
import sys

MANIFEST_FILE = "master_manifest.json"

try:
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        _manifest = json.load(f)

    _ingress = _manifest["ingress"]
    HOST = _ingress["host"]
    PORT = int(_ingress["port"])

    if _manifest.get("port_policy", {}).get("bind_localhost_only") is True:
        if HOST != "127.0.0.1":
            print("[ZEMALA] BLOCKED: NON-LOCALHOST BIND")
            sys.exit(1)

except Exception as e:
    print(f"[ZEMALA] BLOCKED: INVALID MANIFEST: {e}")
    sys.exit(1)


def port_preflight(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


if not port_preflight(HOST, PORT):
    print(f"[ZEMALA] BLOCKED: PORT_OCCUPIED {HOST}:{PORT}")
    sys.exit(1)

print(f"[ZEMALA] MANIFEST BIND: {HOST}:{PORT}")
print("[ZEMALA] PORT PREFLIGHT: PASS")
# --- END MASTER MANIFEST BINDING ---

class ZemalaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status_data = {"system": "ZEMALA CORE", "status": "ONLINE", "stufe": 100}
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
        else:
            super().do_GET()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), ZemalaHandler) as httpd:
        print(f"[ZEMALA] Lokaler Status-Server läuft auf Port {PORT}...")
        httpd.serve_forever()
