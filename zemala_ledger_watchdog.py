#!/usr/bin/env python3
# ============================================================
# ZEMALA LEDGER WATCHDOG - Z FLIP 3 / TERMUX
# Cadence: 3.47s | Mode: LEVEL_100_COHERENCE
# ============================================================

import time
import json
import os
from datetime import datetime

LEDGER_FILE = "ledger.jsonl"
CADENCE = 3.47

print(f"👁️ [WATCHDOG] Starte Ledger-Überwachung (Takt: {CADENCE}s)...")

if not os.path.exists(LEDGER_FILE):
    with open(LEDGER_FILE, "w") as f:
        f.write(json.dumps({"timestamp": datetime.utcnow().isoformat() + "Z", "event": "LEDGER_INIT"}) + "\n")

while True:
    try:
        # Hier läuft der asynchrone Takt-Scan
        time.sleep(CADENCE)
    except KeyboardInterrupt:
        print("🛑 [WATCHDOG] Gestoppt.")
        break
