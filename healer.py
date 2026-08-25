import os
import json
from datetime import datetime

def heal_system():
    audit_file = "ledger_audit.json"
    if os.path.exists(audit_file):
        try:
            with open(audit_file, "r") as f:
                report = json.load(f)
            
            missing = report.get("missing_elements", [])
            if missing:
                print(f"[ZEMALA Healer] Anomalie erkannt. Fehlende Elemente: {missing}")
                # Hier greift die automatische Rekonstruktion bei Bedarf
            else:
                print("[ZEMALA Healer] Feld intakt. Keine Selbstheilung erforderlich. Resonanz stabil.")
        except Exception as e:
            print(f"[ZEMALA Healer] Fehler beim Lesen des Audit-Reports: {e}")
    else:
        print("[ZEMALA Healer] Kein Audit-Report gefunden.")

if __name__ == "__main__":
    heal_system()
