import time
import hashlib
import json
from datetime import datetime, timezone

LEDGER_FILE = "clean_ledger.jsonl"
CHECK_INTERVAL = 10  # seconds

def verify_ledger_once():
    entries = []
    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    except FileNotFoundError:
        return False, "Ledger file missing."

    expected_previous_hash = "0" * 64
    for i, block in enumerate(entries):
        if block["index"] != i or block["previous_hash"] != expected_previous_hash:
            return False, f"Chain break at index {i}"
        
        block_data = {
            "index": block["index"],
            "timestamp": block["timestamp"],
            "previous_hash": block["previous_hash"],
            "payload": block["payload"]
        }
        computed = hashlib.sha256(json.dumps(block_data, sort_keys=True).encode("utf-8")).hexdigest()
        if computed != block["hash"]:
            return False, f"Hash mismatch at index {i}"
        expected_previous_hash = computed

    return True, f"All {len(entries)} blocks verified successfully."

if __name__ == "__main__":
    print(f"Ledger Integrity Monitor initialized. Monitoring '{LEDGER_FILE}'...")
    is_valid, msg = verify_ledger_once()
    timestamp = datetime.now(timezone.utc).isoformat()
    if is_valid:
        print(f"[{timestamp}] [MONITOR] INITIAL HEALTH CHECK PASSED: {msg}")
    else:
        print(f"[{timestamp}] [MONITOR] INITIAL HEALTH CHECK FAILED: {msg}")
