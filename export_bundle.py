#!/usr/bin/env python3
import json
import os
from pathlib import Path

OBS_FILE = "observation.json"
BUNDLE_FILE = "MASTER_BUNDLE.md"

def main():
    # 1. Harte Prüfung auf existierenden Observation Record
    if not os.path.exists(OBS_FILE):
        print("[-] Export abgebrochen: observation.json existiert nicht (Keine verifizierte Evidenz).")
        return

    try:
        obs_data = json.loads(Path(OBS_FILE).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[-] Export abgebrochen: Fehler beim Parsen von observation.json: {e}")
        return

    # 2. Status-Zwang: Nur bei echtem VERIFIED wird exportiert
    if obs_data.get("verification_status") != "VERIFIED":
        print(f"[-] Export blockiert: Status ist nicht VERIFIED ({obs_data.get('verification_status')}).")
        return

    # 3. Bundle-Generierung rein basierend auf dem Observation Contract
    timestamp = obs_data.get("timestamp", "UNKNOWN")
    seal_hash = obs_data.get("seal_hash", "UNKNOWN")
    last_req = obs_data.get("last_request_id", "UNKNOWN")
    node = obs_data.get("node", "zemala-core")

    txt = f"""# ZEMALA MASTER BUNDLE // OBSERVATION ANCHOR
* **Node:** {node}
* **Zeitstempel:** {timestamp}
* **Integrität:** VERIFIZIERT (M₃ / M₄)
* **Seal-Hash:** `{seal_hash}`
* **Letzte Request-ID:** `{last_req}`
"""

    Path(BUNDLE_FILE).write_text(txt, encoding="utf-8")
    print(f"[+] Bundle erfolgreich aus observation.json generiert. Status: VERIFIZIERT")

if __name__ == "__main__":
    main()
