#!/usr/bin/env python3
# ZEMALA M5 — ATOMIC OUTBOUND ACTUATOR
# VERIFIED != AUTHORIZED_TO_ACT
# Guarantees: fresh observation + explicit authorization + atomic claim
# Does not claim exactly-once semantics from a non-idempotent external API.

import json
import os
import sys
import subprocess
import fcntl
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

OBS_FILE = "observation.json"
RECEIPT_FILE = "outbound_receipts.jsonl"
LOCK_FILE = "outbound.lock"

def fail(msg, rc=1):
    print(f"[-] {msg}")
    sys.exit(rc)

def canonical_identity(observation):
    seal_hash = observation.get("seal_hash")
    request_id = observation.get("last_request_id")

    if not seal_hash or not request_id:
        fail("Observation fehlt seal_hash oder last_request_id.")

    return f"{seal_hash}:{request_id}"

def load_observation():
    try:
        with open(OBS_FILE, "r", encoding="utf-8") as f:
            obs = json.load(f)
    except Exception as e:
        fail(f"Observation nicht lesbar: {e}")

    if obs.get("verification_status") != "VERIFIED":
        fail("Outbound BLOCKED: Observation ist nicht VERIFIED.")

    return obs

def refresh_observation():
    result = subprocess.run(
        [sys.executable, "observation_record.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        fail("Fresh Observation konnte nicht erzeugt werden.")

def receipt_exists(identity):
    if not os.path.exists(RECEIPT_FILE):
        return False

    with open(RECEIPT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("identity") == identity:
                    return True
            except json.JSONDecodeError:
                continue

    return False

def append_receipt(entry):
    with open(RECEIPT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())

def main():
    # M5.1 — Just-in-Time freshness
    refresh_observation()

    observation = load_observation()

    # M5.2 — Explicit authorization
    if os.environ.get("ZEMALA_AUTHORIZED") != "1":
        fail("Outbound BLOCKED: ZEMALA_AUTHORIZED != 1.")

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        fail("Outbound BLOCKED: DISCORD_WEBHOOK_URL fehlt.")

    identity = canonical_identity(observation)
    seal_hash = observation["seal_hash"]
    request_id = observation["last_request_id"]

    # M5.3 — Atomic claim
    with open(LOCK_FILE, "a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        if receipt_exists(identity):
            print("STATUS=BLOCKED")
            print("REASON=OUTBOUND_ALREADY_CLAIMED")
            print(f"REQUEST_ID={request_id}")
            print(f"SEAL_HASH={seal_hash}")
            sys.exit(1)

        claim = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "identity": identity,
            "seal_hash": seal_hash,
            "request_id": request_id,
            "status": "CLAIMED"
        }

        append_receipt(claim)

        payload = {
            "content":
                f"ZEMALA CORE // VERIFIED OUTBOUND\n"
                f"request_id={request_id}\n"
                f"seal_hash={seal_hash}\n"
                f"verification_status=VERIFIED"
        }

        data = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(
                webhook,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                http_status = response.status

            result_status = "SUCCESS" if 200 <= http_status < 300 else "FAIL"

        except Exception as e:
            http_status = None
            result_status = "FAIL"
            error = str(e)

        receipt = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "identity": identity,
            "seal_hash": seal_hash,
            "request_id": request_id,
            "status": result_status,
            "http_status": http_status
        }

        if result_status == "FAIL":
            receipt["error"] = error

        append_receipt(receipt)

        if result_status != "SUCCESS":
            print("STATUS=FAIL")
            print("REASON=OUTBOUND_FAILED")
            sys.exit(1)

        print("STATUS=PASS")
        print("EXECUTION=1")
        print("STATUS=OUTBOUND_SUCCESS")
        print(f"REQUEST_ID={request_id}")
        print(f"SEAL_HASH={seal_hash}")

if __name__ == "__main__":
    main()
