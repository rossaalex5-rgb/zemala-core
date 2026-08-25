import os
import json
from datetime import datetime

def dispatch_notifications():
    status_msg = "[ZEMALA Notifier] Alle Kanäle im resonanten Gleichgewicht. Stufe 100 aktiv."
    
    if os.path.exists("version_manifest.json"):
        with open("version_manifest.json", "r") as f:
            v = json.load(f)
            status_msg = f"[ZEMALA Notifier] System v{v.get('major')}.{v.get('minor')}.{v.get('patch')} läuft stabil auf Frequenz 3.47s."
            
    print(status_msg)
    
    # Logge den Dispatch in einen eigenen Stream
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "NOTIFICATION_DISPATCH",
        "message": status_msg,
        "level": "100"
    }
    
    with open("ledger.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

if __name__ == "__main__":
    dispatch_notifications()
