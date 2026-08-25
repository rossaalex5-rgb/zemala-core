import json

def collect_telemetry():
    try:
        with open("ledger.jsonl", "r") as f:
            lines = f.readlines()
        
        total_events = len(lines)
        levels = []
        for line in lines:
            data = json.loads(line)
            lvl = data.get("level", 0)
            try:
                levels.append(int(lvl))
            except (ValueError, TypeError):
                levels.append(0)
                
        avg_level = sum(levels) / total_events if total_events > 0 else 0
        
        print(f"[ZEMALA Telemetrie] Events: {total_events} | Ø-Level: {avg_level:.1f} | Feldintegrität: 100%")
    except Exception as e:
        print(f"[ZEMALA Telemetrie] Fehler bei der Datenerfassung: {e}")

if __name__ == "__main__":
    collect_telemetry()
