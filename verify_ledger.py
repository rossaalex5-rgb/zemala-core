import hashlib
import json

filename = "clean_ledger.jsonl"

entries = []
try:
    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"❌ Error decoding JSON at line {line_num}: {e}")
                    exit(1)
except FileNotFoundError:
    print(f"❌ Ledger file {filename} not found.")
    exit(1)

print(f"Verifying ledger with {len(entries)} blocks...")

expected_previous_hash = "0" * 64

for i, block in enumerate(entries):
    if block["index"] != i:
        print(f"❌ Index mismatch at block {i}: expected {i}, got {block['index']}")
        exit(1)
        
    if block["previous_hash"] != expected_previous_hash:
        print(f"❌ Previous hash mismatch at block {i}: expected {expected_previous_hash}, got {block['previous_hash']}")
        exit(1)
        
    block_data = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "previous_hash": block["previous_hash"],
        "payload": block["payload"]
    }
    block_string = json.dumps(block_data, sort_keys=True)
    computed_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    if computed_hash != block["hash"]:
        print(f"❌ Hash mismatch at block {i}: stored {block['hash']}, computed {computed_hash}")
        exit(1)
        
    print(f"✔ Block {i} verified successfully. Hash: {computed_hash[:16]}...")
    expected_previous_hash = computed_hash

print("🎉 Ledger verification PASSED: All blocks are cryptographically valid and chained correctly.")
