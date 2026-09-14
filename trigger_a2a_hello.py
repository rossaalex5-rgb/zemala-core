import json
import urllib.request

# Konfiguration für JSON-RPC 2.0 über HTTP
URL = "http://127.0.0.1:8080" # Anpassung falls erforderlich
payload = {
    "jsonrpc": "2.0",
    "method": "a2a_hello",
    "params": {},
    "id": 1
}

def trigger_handshake():
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        print("[ZEMALA] Sende a2a_hello Handshake...")
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            print(f"[ANTWORT]\n{json.dumps(res, indent=2)}\n")
    except Exception as e:
        print(f"[FEHLER] Handshake fehlgeschlagen: {e}")

if __name__ == "__main__":
    trigger_handshake()
