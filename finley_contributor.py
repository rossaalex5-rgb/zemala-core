import json
import os
import hashlib
from datetime import datetime, timezone

LEDGER_PATH = "core/ledger.jsonl"
PERMISSIONS_PATH = "core/permissions.json"
CADENCE = 3.47

def verify_node_permission(node_id):
    if not os.path.exists(PERMISSIONS_PATH):
        return False
    with open(PERMISSIONS_PATH, "r", encoding="utf-8") as f:
        perms = json.load(f)
    nodes = perms.get("nodes", {})
    return node_id in nodes and "WRITE_PAYLOAD" in nodes[node_id].get("permissions", [])

def get_last_hash():
    if not os.path.exists(LEDGER_PATH):
        return "0" * 64
    last_hash = "0" * 64
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    block = json.loads(line)
                    last_hash = block.get("sha256_seal", last_hash)
                except json.JSONDecodeError:
                    pass
    return last_hash

def get_next_sequence():
    if not os.path.exists(LEDGER_PATH):
        return 1
    count = 0
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count + 1

def commit_finley_payload(payload_text):
    node_id = "finley_node"
    if not verify_node_permission(node_id):
        print(f"[ACCESS DENIED] Node {node_id} has no write permissions in permissions.json!")
        return

    prev_hash = get_last_hash()
    seq = get_next_sequence()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    block_data = {
        "node_id": node_id,
        "block_sequence": seq,
        "cadence": f"{CADENCE}s",
        "event_type": "FINLEY_CONTRIBUTION_BLOCK",
        "payload": {"message": payload_text},
        "prev_hash": prev_hash,
        "status": "PASS",
        "timestamp": timestamp
    }
    
    block_string = json.dumps(block_data, sort_keys=True)
    seal = hashlib.sha256(block_string.encode("utf-8")).hexdigest()
    block_data["sha256_seal"] = seal
    
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(block_data) + "\n")
    print(f"[FINLEY NODE] Contributor Block #{seq} successfully sealed! Seal: {seal[:16]}...")

if __name__ == "__main__":
    commit_finley_payload("Grüße vom Finley Node - Multi-Node Kette aktiv!")
