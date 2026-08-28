#!/usr/bin/env python3

import hashlib
import json
import os
import sys

LEDGER_FILE = "ledger.jsonl"
SEAL_FILE = "ledger_seal.json"

def main():
    if not os.path.exists(LEDGER_FILE) or not os.path.exists(SEAL_FILE):
        print("STATUS=UNKNOWN")
        print("REASON=MISSING_EVIDENCE")
        sys.exit(2)

    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        with open(SEAL_FILE, "r", encoding="utf-8") as f:
            seal = json.load(f)

    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        print("STATUS=FAIL")
        print(f"REASON=CORRUPT_OR_UNREADABLE: {e}")
        sys.exit(3)

    expected_hash = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    actual_hash = seal.get("seal_hash")

    if not actual_hash:
        print("STATUS=FAIL")
        print("REASON=SEAL_HASH_MISSING")
        sys.exit(3)

    if expected_hash != actual_hash:
        print("STATUS=FAIL")
        print("REASON=HASH_MISMATCH")
        print(f"EXPECTED={expected_hash}")
        print(f"SEALED={actual_hash}")
        sys.exit(1)

    print("STATUS=VERIFIED")
    print("REASON=LEDGER_HASH_MATCH")
    print(f"HASH={expected_hash}")
    sys.exit(0)

if __name__ == "__main__":
    main()
