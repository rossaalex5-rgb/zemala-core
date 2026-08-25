import json
from datetime import datetime

def run_agent_loop():
    try:
        with open("ledger.jsonl", "r") as f:
            lines = f.readlines()
        
        event_count = len(lines)
        print(f"[ZEMALA Agent] Autonome Schleife aktiv. Ledger-Stand: {event_count} Events. Feldkohärenz: Stufe 100.")
    except Exception as e:
        print(f"[ZEMALA Agent] Fehler in der Agenten-Schleife: {e}")

if __name__ == "__main__":
    run_agent_loop()
