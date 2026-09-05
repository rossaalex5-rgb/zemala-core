#!/usr/bin/env python3
import os
import json
import hashlib
import glob
from datetime import datetime, timezone

ZCORE = "/storage/emulated/0/_zcore"
OUTBOX = os.path.join(ZCORE, "outbox")
PROCESSED = os.path.join(ZCORE, "processed")
REJECTED = os.path.join(ZCORE, "rejected")
LEDGER_DIR = os.path.join(ZCORE, "ledger")
LEDGER = os.path.join(LEDGER_DIR, "observations.jsonl")

TOXIC_PATTERNS = ["rm -rf", "mkfs", ":(){ :|:& };:", "dd if="]

os.makedirs(OUTBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)
os.makedirs(REJECTED, exist_ok=True)
os.makedirs(LEDGER_DIR, exist_ok=True)

def get_last_hash():
    if not os.path.exists(LEDGER):
        return "GENESIS_ROOT_HASH"
    last_line = None
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if not last_line:
        return "GENESIS_ROOT_HASH"
    try:
        data = json.loads(last_line)
        return data.get("current_hash", "GENESIS_ROOT_HASH")
    except Exception:
        return "CORRUPTED_LEDGER_TIP"

def compute_hash(prev_hash, payload_str):
    hasher = hashlib.sha256()
    hasher.update((prev_hash + payload_str).encode("utf-8"))
    return hasher.hexdigest()

def process_outbox():
    print("=== ZEMALA BRIDGE: AIRLOCK SCAN ===")
    proposals = glob.glob(os.path.join(OUTBOX, "*.json"))
    
    if not proposals:
        print("[*] Outbox ist leer. Keine Proposals an der Schleuse.")
        return

    for prop_path in proposals:
        print(f"[*] Prüfe Proposal: {os.path.basename(prop_path)}")
        try:
            with open(prop_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
                proposal_data = json.loads(raw_content)
        except Exception as e:
            print(f"[!] FEHLER: Ungültiges JSON in {prop_path}: {e}")
            os.rename(prop_path, os.path.join(REJECTED, os.path.basename(prop_path)))
            continue

        proposal_str = json.dumps(proposal_data, ensure_ascii=False)
        is_toxic = any(pattern in proposal_str for pattern in TOXIC_PATTERNS)
        
        if is_toxic:
            print(f"[!] SICHERHEITSSTOPP: Toxisches Muster im Proposal erkannt! Abweisung.")
            target = os.path.join(REJECTED, os.path.basename(prop_path))
            os.rename(prop_path, target)
            continue

        prev_hash = get_last_hash()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        block = {
            "timestamp": timestamp,
            "prev_hash": prev_hash,
            "source": "OUTBOX_AIRLOCK",
            "payload": proposal_data
        }
        
        block_str = json.dumps(block, sort_keys=True, ensure_ascii=False)
        current_hash = compute_hash(prev_hash, block_str)
        block["current_hash"] = current_hash

        with open(LEDGER, "a", encoding="utf-8") as ledger_file:
            ledger_file.write(json.dumps(block, ensure_ascii=False) + "\n")

        print(f"[+] VERGOLDET: Proposal erfolgreich verifiziert und ins Ledger geschrieben.")
        print(f"    Hash: {current_hash[:16]}...")

        target = os.path.join(PROCESSED, os.path.basename(prop_path))
        os.rename(prop_path, target)

if __name__ == "__main__":
    process_outbox()
