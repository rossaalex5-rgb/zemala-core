import hashlib
import json
from datetime import datetime, timezone

class Ledger:
    def __init__(self, filename="clean_ledger.jsonl"):
        self.filename = filename
        self.previous_hash = "0" * 64
        self.index = 0
        
    def add_entry(self, payload):
        timestamp = datetime.now(timezone.utc).isoformat()
        block_data = {
            "index": self.index,
            "timestamp": timestamp,
            "previous_hash": self.previous_hash,
            "payload": payload
        }
        block_string = json.dumps(block_data, sort_keys=True)
        current_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
        
        complete_block = {
            **block_data,
            "hash": current_hash
        }
        
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(complete_block) + "\n")
            
        self.previous_hash = current_hash
        self.index += 1
        return complete_block

if __name__ == "__main__":
    ledger = Ledger("clean_ledger.jsonl")
    ledger.add_entry({"event": "genesis", "status": "initialized"})
    ledger.add_entry({"event": "clean_run", "message": "Sauberer Durchlauf erfolgreich initialisiert."})
    print("Ledger successfully created and populated.")
