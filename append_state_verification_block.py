import hashlib
import json
from datetime import datetime, timezone

filename = "clean_ledger.jsonl"

entries = []
try:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line.strip()))
except FileNotFoundError:
    pass

if entries:
    last_entry = entries[-1]
    previous_hash = last_entry["hash"]
    index = last_entry["index"] + 1
else:
    previous_hash = "0" * 64
    index = 0

payload = {
    "event": "state_verification_governance",
    "rules": [
        "Merkle tree root hashing for hierarchical state validation",
        "Cryptographic proof verification for distributed sub-ledger nodes",
        "Continuous cryptographic auditing and tamper-evident root seals"
    ]
}

timestamp = datetime.now(timezone.utc).isoformat()
block_data = {
    "index": index,
    "timestamp": timestamp,
    "previous_hash": previous_hash,
    "payload": payload
}
block_string = json.dumps(block_data, sort_keys=True)
current_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()

complete_block = {
    **block_data,
    "hash": current_hash
}

with open(filename, "a", encoding="utf-8") as f:
    f.write(json.dumps(complete_block) + "\n")

print(f"Successfully appended block {index} with state verification and Merkle proof rules.")
