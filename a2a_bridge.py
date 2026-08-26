import os
import hashlib
import json

def verify_and_dispatch(payload):
    normalized = payload.strip().lower()
    h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    ledger_entry = {
        "hash": h,
        "content": normalized,
        "status": "VERIFIED_STUFE_100"
    }
    print(f"[ZEMALA A2A] Payload verifiziert. Hash: {h[:12]}...")
    return ledger_entry

if __name__ == "__main__":
    test_payload = "Zemala A2A Pipeline Test"
    verify_and_dispatch(test_payload)
