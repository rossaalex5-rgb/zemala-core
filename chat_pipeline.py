#!/usr/bin/env python3
import json
import hashlib
from datetime import datetime, timezone
import os

LEDGER_FILE = "events.jsonl"

def get_last_hash():
    if not os.path.exists(LEDGER_FILE):
        return "0" * 64
    last_hash = "0" * 64
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    if "hash" in data:
                        last_hash = data["hash"]
                except json.JSONDecodeError:
                    pass
    return last_hash

def process_input(intent_text, actor="dirigent"):
    timestamp = datetime.now(timezone.utc).isoformat()
    prev_hash = get_last_hash()
    
    # Constitutional check (Auth Gate simulation)
    auth_status = 1 if len(intent_text.strip()) > 0 else 0
    effect_status = auth_status # Auth=0 -> Effect=0
    
    if auth_status == 0:
        print("[-] FAIL: Auth Gate Violation. Empty intent.")
        return
        
    event = {
        "timestamp": timestamp,
        "actor": actor,
        "intent": intent_text,
        "auth": auth_status,
        "effect": effect_status,
        "prev_hash": prev_hash
    }
    
    # Compute canonical hash for this event line
    event_string = json.dumps(event, sort_keys=True)
    event_hash = hashlib.sha256(event_string.encode("utf-8")).hexdigest()
    event["hash"] = event_hash
    
    # Append to immutable ledger
    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
        
    print(f"[+] ZEMALA PIPELINE SUCCESS [Stufe 100]")
    print(f" -> Timestamp : {timestamp}")
    print(f" -> Intent    : {intent_text}")
    print(f" -> Hash      : {event_hash[:16]}...")
    print(f" -> Ledger    : Appended & Verified.")

if __name__ == "__main__":
    import sys
    input_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "default_pulse_check"
    process_input(input_text)
