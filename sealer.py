import json
import hashlib
from datetime import datetime

def seal_ledger():
    try:
        with open("ledger.jsonl", "r") as f:
            content = f.read()
        
        # SHA-256 Signatur des gesamten Ledger-Inhalts berechnen
        ledger_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        seal_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "seal_hash": ledger_hash,
            "status": "Cryptographically Sealed",
            "level": "100"
        }
        
        with open("ledger_seal.json", "w") as f:
            json.dump(seal_record, f, indent=2)
            
        print(f"[ZEMALA Sealer] Ledger erfolgreich versiegelt. Hash: {ledger_hash[:16]}...")
    except Exception as e:
        print(f"[ZEMALA Sealer] Fehler beim Versiegeln: {e}")

if __name__ == "__main__":
    seal_ledger()
