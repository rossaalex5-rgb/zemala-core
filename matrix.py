import json

def check_geometry():
    try:
        with open("ledger.jsonl", "r") as f:
            count = sum(1 for _ in f)
        
        # Geometrische Resonanz-Projektion (3-4-7-11-1)
        base = count % 1
        apex = count % 11
        center = count % 7
        
        print(f"[ZEMALA Matrix] Geometrie-Status: Basis={base} | Zentrum(7)={center} | Spitze(11)={apex}")
    except Exception as e:
        print(f"[ZEMALA Matrix] Fehler in der Geometrie: {e}")

if __name__ == "__main__":
    check_geometry()
