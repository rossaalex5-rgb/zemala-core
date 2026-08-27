#!/usr/bin/env python3
# ZEMALA v1.0.115 - M2 IDEMPOTENZ-GUARD (EXACTLY-ONCE PROTECTION)
# [STUFE 100 SYSTEMHYGIENE - STRICT REQUEST_ID BOUNDARY]

import sys
import os
import json
import hashlib
import time

SEEN_IDS_FILE = "seen_ids.txt"
BLOCKED_LOG = "ledger_blocked.log"

def calculate_canonical_hash(obj):
    serialized = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def log_blocked(reason, request_id, cmd, payload):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reason": reason,
        "request_id": request_id,
        "command": cmd,
        "payload_hash": calculate_canonical_hash(payload)
    }
    with open(BLOCKED_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print("[-] FAIL: No input received via STDIN.")
            sys.exit(2)
        event = json.loads(input_data)
    except json.JSONDecodeError:
        print("[-] FAIL: Input is not valid JSON (Syntax Error).")
        sys.exit(3)
    except Exception as e:
        print(f"[-] FAIL: Unexpected error parsing input: {e}")
        sys.exit(4)

    request_id = event.get("request_id")
    cmd = event.get("command")
    payload = event.get("payload")

    if not request_id or not cmd or payload is None:
        print("[-] FAIL: Missing mandatory root fields (request_id, command, payload).")
        sys.exit(5)

    for f in [SEEN_IDS_FILE, BLOCKED_LOG]:
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as temp:
                pass

    with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
        seen_ids = set(line.strip() for line in f if line.strip())

    if request_id in seen_ids:
        log_blocked("REPLAY_ATTEMPT", request_id, cmd, payload)
        print(f"== [ZEMALA GUARD] T2 DETECTED: REPLAY BLOCKADE (ID: {request_id}) ==")
        print("STATUS: IGNORED")
        print("EXECUTION=0")
        sys.exit(0)

    with open(SEEN_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(request_id + "\n")

    print(f"== [ZEMALA GUARD] INGEST SUCCESS (ID: {request_id}) ==")
    print("STATUS: PASS")
    print("EXECUTION=1")
    
    if cmd == "vibrate":
        print("[+] ACTIVATE_HARDWARE: VIBRATE_BURST_OK")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
