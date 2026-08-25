#!/usr/bin/env python3
"""
ZEMALA Core - Agent Bridge (Stufe 100)
Verwaltet den lokalen Ereignis-Strom und die Interaktion mit dem Ledger.
"""

import os
import json
from datetime import datetime, timezone

LEDGER_FILE = "ledger.jsonl"

def emit_event(payload_text):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    event = {
        "timestamp": timestamp,
        "level": "100",
        "payload": payload_text
    }
    
    # In Ledger schreiben (Append-Only)
    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
        
    print(f"[ZEMALA Bridge] Event registriert: {timestamp} -> {payload_text}")

if __name__ == "__main__":
    print("[ZEMALA Bridge] Initialisiert. Stufe 100 aktiv.")
    emit_event("ZEMALA Bridge erfolgreich initialisiert und verbunden.")
