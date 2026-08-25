import json
from datetime import datetime

try:
    with open("ledger.jsonl", "r") as f:
        lines = f.readlines()
    
    total_events = len(lines)
    last_events = [json.loads(line) for line in lines[-5:]]

    status_content = f"""# ZEMALA Core - Live Status Dashboard

* **System-Zustand:** Aktiv / Stufe 100
* **Letztes Update:** {datetime.utcnow().isoformat()}Z
* **Gesamt-Impulse im Ledger:** {total_events}

## Letzte Kaskaden-Ereignisse (Herzschlag)
"""
    for ev in reversed(last_events):
        status_content += f"- **[{ev.get('timestamp')}]** (Level {ev.get('level')}): {ev.get('payload')}\n"

    with open("STATUS.md", "w") as out:
        out.write(status_content)

    print("[ZEMALA Renderer] STATUS.md erfolgreich aktualisiert.")
except Exception as e:
    print(f"[ZEMALA Renderer] Fehler beim Rendern: {e}")
