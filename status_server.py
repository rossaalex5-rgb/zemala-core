import http.server
import socketserver
import json
import os

PORT = 8090
DIRECTORY = "."

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
