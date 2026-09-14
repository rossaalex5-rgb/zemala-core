#!/usr/bin/env python3
# ============================================================
# ZEMALA HEALTH CHECK & HAPTIC TRIGGER (Z FLIP 3)
# Cadence: 3.47s | Mode: LEVEL_100_COHERENCE
# ============================================================

import urllib.request
import json
import subprocess
import sys

URL = "http://127.0.0.1:8080/status"

print("🔍 [ZEMALA] Führe Loopback-Health-Check auf Port 8080 aus...")

try:
    req = urllib.request.Request(URL, headers={"User-Agent": "Zemala-Health-Checker/3.47"})
    with urllib.request.urlopen(req, timeout=3.47) as response:
        status_code = response.status
        body = response.read().decode('utf-8')
        data = json.loads(body)
        
        print(f"🟢 [SUCCESS] HTTP Code: {status_code}")
        print(json.dumps(data, indent=2))
        
        # Haptischer Feedback-Impuls über Termux API bei Erfolg
        if status_code == 200:
            print("📳 [HAPTIC] Aktiviere Z Flip3 Vibrations-Impuls (Antennen-Bestätigung)...")
            subprocess.run(["termux-vibrate", "-d", "150"], check=False)
        else:
            print("⚠️ [WARNING] Status abweichend von 200 OK.")
            sys.exit(1)

except Exception as e:
    print(f"🔴 [ERROR] Verbindung zu Port 8080 fehlgeschlagen: {e}")
    sys.exit(1)
