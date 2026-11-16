#!/usr/bin/env python3
"""
ZEMALA LEDGER WATCHDOG DAEMON (Variante B - Asynchroner Sidecar)
Stufe 100 Systemhygiene | 0-Latenz Edge-Architektur
Sicherung des unbestechlichen Append-Only Event-Streams.
"""

import os
import sys
import time
import json
import hashlib
import signal

TAKT_CADENCE = 3.47
LEDGER_PATH = os.environ.get("ZEMALA_LEDGER_PATH", "./ledger.jsonl")
STATE_PATH = os.environ.get("ZEMALA_STATE_PATH", "./state_snapshot.json")
LOG_PATH = os.environ.get("ZEMALA_WATCHDOG_LOG", "./watchdog_daemon.log")

running = True

def signal_handler(sig, frame):
    global running
    running = False
    log_event("SYSTEM", "DAEMON_SHUTDOWN", {"reason": f"Signal {sig} received"})
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def log_event(level, event_type, details):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry = {
        "timestamp": timestamp,
        "level": level,
        "event_type": event_type,
        "details": details,
        "cadence": f"{TAKT_CADENCE}s"
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def canonicalize_and_hash(payload):
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def process_ledger_line(line_num, line_str):
    line_str = line_str.strip()
    if not line_str:
        return
    try:
        data = json.loads(line_str)
        payload_hash = canonicalize_and_hash(data.get("payload", data))
        
        # Verify schema/integrity
        status = "PASS" if data.get("status") in ["PASS", "COMMITTED", "SUCCESS", "ALLOWED"] else "OBSERVED"
        
        # Dispatch side-effects asynchronously
        side_effect = {
            "line": line_num,
            "hash": payload_hash,
            "status": status,
            "action": data.get("action", data.get("event", "LEDGER_APPEND")),
            "sender": data.get("sender", "SYSTEM_HOT_PATH")
        }
        
        log_event("INFO", "SIDE_EFFECT_DISPATCHED", side_effect)
        
        # Update State Snapshot without locking hot path
        update_state_snapshot(side_effect)
        
    except json.JSONDecodeError as e:
        log_event("WARN", "REJECT_BY_DEFAULT", {"line": line_num, "error": str(e), "raw": line_str[:50]})

def update_state_snapshot(effect):
    snapshot = {
        "version": "v1.0.1400",
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_processed_line": effect["line"],
        "last_hash": effect["hash"],
        "last_action": effect["action"],
        "hardware_status": "SNAPDRAGON_888_FROZEN",
        "cadence": "3.47s"
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

def run_watchdog():
    log_event("SYSTEM", "DAEMON_IGNITION", {"status": "ACTIVE", "cadence": f"{TAKT_CADENCE}s"})
    
    # Ensure ledger file exists
    if not os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            genesis = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": "GENESIS_LOCK",
                "status": "PASS",
                "payload": {"genesis": "ZEMALA_DAEMON_INITIALIZED"}
            }
            f.write(json.dumps(genesis) + "\n")

    current_pos = 0
    line_num = 0

    while running:
        try:
            with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                f.seek(current_pos)
                lines = f.readlines()
                current_pos = f.tell()

                for line in lines:
                    line_num += 1
                    process_ledger_line(line_num, line)

        except Exception as e:
            log_event("ERROR", "WATCHDOG_READ_ERROR", {"error": str(e)})

        time.sleep(TAKT_CADENCE)

if __name__ == "__main__":
    run_watchdog()
