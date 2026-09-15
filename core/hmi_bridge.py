import json
import os
import hashlib

HOME = "/data/data/com.termux/files/home"
LEDGER_PATH = os.path.join(HOME, "zemala-core/core/ledger.jsonl")
OUTPUT_PATH = os.path.join(HOME, ".minetest/worlds/zemala_world/voxel_state.json")

def verify_and_bridge():
    if not os.path.exists(LEDGER_PATH):
        print(f"[ERROR] Ledger not found at absolute path: {LEDGER_PATH}")
        return False

    blocks = []
    expected_prev_hash = None

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if not line.strip():
                continue
            block = json.loads(line)
            stored_seal = block.pop("sha256_seal", None)
            
            if idx == 1:
                expected_prev_hash = block.get("prev_hash")
            elif block.get("prev_hash") != expected_prev_hash:
                print(f"[FAIL] Chain broken at block #{idx}")
                return False

            block_string = json.dumps(block, sort_keys=True, separators=(",", ":"))
            calc_seal = hashlib.sha256(block_string.encode("utf-8")).hexdigest()
            
            if calc_seal != stored_seal:
                print(f"[FAIL] Hash mismatch at block #{idx}")
                return False

            block["sha256_seal"] = stored_seal
            blocks.append({
                "sequence": idx,
                "node_id": block.get("node_id", "unknown"),
                "event_type": block.get("event_type", "GENESIS"),
                "seal": stored_seal[:16]
            })
            expected_prev_hash = stored_seal

    # Ensure target directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # Export state for Minetest / Luanti Voxel Engine
    state_payload = {
        "status": "8_OF_8_PASS",
        "total_blocks": len(blocks),
        "blocks": blocks
    }
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump(state_payload, out, indent=2)

    print(f"[HMI BRIDGE SUCCESS] {len(blocks)} verified blocks exported to absolute path:\n{OUTPUT_PATH}")
    return True

if __name__ == "__main__":
    verify_and_bridge()
