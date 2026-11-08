import os
import json
from canonicalize_observation import canonicalize_and_hash, trigger_async_sync

def append_observation(payload: dict, ledger_path: str = os.path.expanduser("~/zemala/observations.jsonl")) -> str:
    canonical_json, digest = canonicalize_and_hash(payload)
    record = {
        "hash": digest,
        "payload": payload
    }
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    trigger_async_sync()
    return digest
