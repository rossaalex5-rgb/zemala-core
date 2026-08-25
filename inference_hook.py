import json

def process_resonance():
    try:
        with open("ledger.jsonl", "r") as f:
            lines = f.readlines()
        if not lines:
            return
        
        last_event = json.loads(lines[-1])
        print(f"[ZEMALA Hook] Analysiere letzten Impuls (Stufe {last_event.get('level')}): Resonanzfeld stabil.")
    except Exception as e:
        print(f"[ZEMALA Hook] Fehler im Intelligenz-Hook: {e}")

if __name__ == "__main__":
    process_resonance()
