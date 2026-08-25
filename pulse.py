import json
from datetime import datetime

timestamp = datetime.utcnow().isoformat() + "Z"
payload = "Kaskaden-Resonanz Stufe 100: Aktiver Impuls in den Datenstrom emittiert."
event = {"timestamp": timestamp, "level": "100", "payload": payload}

with open("ledger.jsonl", "a") as f:
    f.write(json.dumps(event) + "\n")

print(f"[ZEMALA Pulse] Erfolg: {payload}")
