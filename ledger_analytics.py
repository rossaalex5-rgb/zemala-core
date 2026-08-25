import json
from collections import Counter

def analyze_ledger():
    try:
        with open("ledger.jsonl", "r") as f:
            lines = f.readlines()
        
        levels = []
        for line in lines:
            data = json.loads(line)
            levels.append(str(data.get('level', 'unknown')))
        
        counts = Counter(levels)
        print(f"[ZEMALA Analytics] Event-Verteilung nach Level: {dict(counts)}")
    except Exception as e:
        print(f"[ZEMALA Analytics] Fehler: {e}")

if __name__ == "__main__":
    analyze_ledger()
