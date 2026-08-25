import json

try:
    with open("ledger.jsonl", "r") as f:
        lines = f.readlines()
    
    total_events = len(lines)
    levels = {}
    for line in lines:
        event = json.loads(line)
        lvl = event.get("level", "unknown")
        levels[lvl] = levels.get(lvl, 0) + 1

    print(f"[ZEMALA Analyzer] Gesamt-Events im Ledger: {total_events}")
    print(f"[ZEMALA Analyzer] Level-Verteilung: {levels}")
except Exception as e:
    print(f"[ZEMALA Analyzer] Fehler beim Lesen des Ledgers: {e}")
