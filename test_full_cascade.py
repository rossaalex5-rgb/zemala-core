#!/usr/bin/env python3
# ============================================================
# ZEMALA A2A FULL CASCADE TESTER - Z FLIP 3 / TERMUX
# Cadence: 3.47s | Mode: LEVEL_100_COHERENCE
# ============================================================

import urllib.request
import json

URL = "http://127.0.0.1:8080"

payload = {
    "jsonrpc": "2.0",
    "method": "a2a_hello",
    "params": {
        "agent": "Z_Flip3_Local_Node",
        "state": "COHERENT_LEVEL_100"
    },
    "id": 347
}

print("🚀 [CASCADE] Sende A2A-Test-Payload an Port 8080...")

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        URL, 
        data=data, 
        headers={"Content-Type": "application/json", "User-Agent": "Zemala-Tester/3.47"}
    )
    
    with urllib.request.urlopen(req, timeout=3.47) as response:
        status_code = response.status
        body = response.read().decode('utf-8')
        result = json.loads(body)
        
        print(f"🟢 [SUCCESS] HTTP Code: {status_code}")
        print("Antwort des Ingress-Servers:")
        print(json.dumps(result, indent=2))
        print("✨ Kaskade erfolgreich durchschlagen. Event im Ledger versiegelt.")

except Exception as e:
    print(f"🔴 [ERROR] Kaskaden-Test fehlgeschlagen: {e}")
