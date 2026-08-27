#!/usr/bin/env python3

import fcntl
import json
import os
import sys
from datetime import datetime, timezone

LEDGER_FILE = "ledger.jsonl"
BLOCKED_FILE = "ledger_blocked.log"
LOCK_FILE = "ledger.lock"

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def load_ledger():
    if not os.path.exists(LEDGER_FILE):
        return []
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def log_blocked(reason, event):
    record = {
        "timestamp": now(),
        "status": "BLOCKED",
        "reason": reason,
        "request_id": event.get("request_id")
    }
    with open(BLOCKED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    try:
        event = json.load(sys.stdin)
    except Exception as e:
        print("STATUS=FAIL")
        print(f"REASON=INVALID_JSON:{e}")
        return 2

    request_id = event.get("request_id")
    if not request_id:
        print("STATUS=FAIL")
        print("REASON=MISSING_REQUEST_ID")
        return 2

    # Sicherstellen, dass das Lock-File existiert
    if not os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            pass

    with open(LOCK_FILE, "r+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        ledger = load_ledger()
        already_committed = any(
            entry.get("request_id") == request_id
            for entry in ledger
        )

        if already_committed:
            log_blocked("ALREADY_EXECUTED", event)
            print("STATUS=BLOCKED")
            print("REASON=ALREADY_EXECUTED")
            print("EXECUTION=0")
            fcntl.flock(lock, fcntl.LOCK_UN)
            return 1

        commit = {
            "timestamp": now(),
            "status": "ACTION_COMMITTED",
            "request_id": request_id,
            "intent_data": event
        }

        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(commit, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

        print("STATUS=PASS")
        print("STATUS=ACTION_COMMITTED")
        print("EXECUTION=1")

        fcntl.flock(lock, fcntl.LOCK_UN)

    return 0

if __name__ == "__main__":
    sys.exit(main())
