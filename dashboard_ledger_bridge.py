import json
import hashlib
import os
from datetime import datetime

LEDGER_PATH = "core/ledger.jsonl"

def canonicalize(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def get_prev_hash() -> str:
    if not os.path.exists(LEDGER_PATH):
        return "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines):
            line_str = line.strip()
            if line_str:
                try:
                    last_entry = json.loads(line_str)
                    return last_entry.get("sha256_seal", "GENESIS")
                except json.JSONDecodeError:
                    continue
        return "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"

def commit_event(payload: dict, node_id: str = "dirigent_zflip3"):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "node_id": node_id,
        "prev_hash": get_prev_hash(),
        "payload": payload
    }
    
    canonical_str = canonicalize(event)
    sha_seal = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
    
    final_record = {
        **event,
        "sha256_seal": sha_seal,
        "status": "PASS"
    }
    
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(final_record, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + "\n")
    
    print(f"[ZEMALA SSoT] LEDGER COMMITTED | SEAL: {sha_seal[:16]}... | STATUS: PASS")
    return sha_seal

if __name__ == "__main__":
    test_payload = {"loop_id": "ZSP-V3-DASHBOARD-INGRESS-TEST", "cadence": "3.47s"}
    commit_event(test_payload)
