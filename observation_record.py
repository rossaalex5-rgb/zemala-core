#!/usr/bin/env python3

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

LEDGER_FILE = "ledger.jsonl"
SEAL_FILE = "ledger_seal.json"
OBS_FILE = "observation.json"

def get_last_request_id():
    try:
        if not os.path.exists(LEDGER_FILE):
            return "UNKNOWN"
        lines = Path(LEDGER_FILE).read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return "EMPTY"
        last_entry = json.loads(lines[-1])
        
        if "request_id" in last_entry:
            return last_entry["request_id"]
        if "intent_data" in last_entry and isinstance(last_entry["intent_data"], dict):
            if "request_id" in last_entry["intent_data"]:
                return last_entry["intent_data"]["request_id"]
        if "payload" in last_entry and isinstance(last_entry["payload"], dict):
            if "request_id" in last_entry["payload"]:
                return last_entry["payload"]["request_id"]
                
        return "UNKNOWN"
    except Exception:
        return "PARSE_ERROR"

def main():
    res = subprocess.run([sys.executable, "verify_seal.py"], capture_output=True, text=True)
    
    if res.returncode != 0:
        print(f"[-] Observation abgebrochen: verify_seal lieferte RC={res.returncode}")
        if os.path.exists(OBS_FILE):
            os.remove(OBS_FILE)
        sys.exit(1)

    seal_hash = None
    for line in res.stdout.splitlines():
        if line.startswith("HASH="):
            seal_hash = line.split("=", 1)[1].strip()

    if not seal_hash:
        print("[-] Observation abgebrochen: RC=0, aber kein gültiger HASH in der Ausgabe gefunden.")
        if os.path.exists(OBS_FILE):
            os.remove(OBS_FILE)
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        if os.path.exists(SEAL_FILE):
            seal_data = json.loads(Path(SEAL_FILE).read_text(encoding="utf-8"))
            timestamp = seal_data.get("timestamp", timestamp)
    except Exception:
        pass

    record = {
        "schema": "ZEMALA_OBSERVATION_V1",
        "node": "zemala-core",
        "timestamp": timestamp,
        "verification_status": "VERIFIED",
        "seal_hash": seal_hash,
        "last_request_id": get_last_request_id()
    }

    tmp_file = OBS_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, OBS_FILE)
        print("[+] observation.json atomar emittiert.")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Fehler beim atomaren Schreiben: {e}")
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        sys.exit(1)

if __name__ == "__main__":
    main()
