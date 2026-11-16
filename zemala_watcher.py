import time
import json
import os
import hashlib
from datetime import datetime, timezone

LEDGER_PATH = "core/ledger.jsonl"
WATCH_DIR = "/storage/emulated/0/Documents/ZEMALA"
ARCHIVE_DIR = os.path.join(WATCH_DIR, "archive")
CADENCE = 3.47

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

def seal_block(payload, source_name):
    os.makedirs("core", exist_ok=True)
    prev_hash = get_last_hash()
    seq = get_next_sequence()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    block_data = {
        "node_id": "dirigent_zflip3_watcher",
        "block_sequence": seq,
        "cadence": f"{CADENCE}s",
        "event_type": "ZEMALA_DOCUMENT_DROP",
        "source_file": source_name,
        "payload": payload,
        "prev_hash": prev_hash,
        "status": "PASS",
        "timestamp": timestamp
    }
    
    block_string = json.dumps(block_data, sort_keys=True)
    seal = hashlib.sha256(block_string.encode("utf-8")).hexdigest()
    block_data["sha256_seal"] = seal
    
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(block_data) + "\n")
    print(f"[ZEMALA WATCHER] Block #{seq} sealed from {source_name}. Seal: {seal[:16]}...")

def main():
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    print(f"[ZEMALA WATCHER] Active. Cadence: {CADENCE}s. Watching directory: {WATCH_DIR}")
    
    while True:
        try:
            files = [f for f in os.listdir(WATCH_DIR) if os.path.isfile(os.path.join(WATCH_DIR, f))]
            for filename in files:
                file_path = os.path.join(WATCH_DIR, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Try parsing as JSON, otherwise wrap text
                    try:
                        payload = json.loads(content)
                    except json.JSONDecodeError:
                        payload = {"raw_text": content}
                        
                    seal_block(payload, filename)
                    
                    # Move to archive
                    archive_path = os.path.join(ARCHIVE_DIR, filename)
                    os.rename(file_path, archive_path)
                    print(f"[ZEMALA WATCHER] Archived {filename} -> /archive/")
                except Exception as inner_e:
                    print(f"[ERROR processing {filename}] {inner_e}")
        except Exception as e:
            print(f"[WATCHER ERROR] {e}")
            
        time.sleep(CADENCE)

if __name__ == "__main__":
    main()
