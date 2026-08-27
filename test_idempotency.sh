#!/usr/bin/env bash
set -euo pipefail

echo "=== Cleaning local environment ==="
rm -f seen_ids.txt ledger_blocked.log

echo -e "\n=== TEST 1: Erstanfrage (T1) ==="
cat << 'INBOUND' | python3 verify_idempotency.py
{
  "request_id": "REQ-001",
  "command": "vibrate",
  "payload": {
    "duration": 500,
    "pattern": "single"
  }
}
INBOUND

echo -e "\n=== TEST 2: Replay-Blockade (T2 - Exakte ID Wiederholung) ==="
cat << 'INBOUND' | python3 verify_idempotency.py
{
  "request_id": "REQ-001",
  "command": "vibrate",
  "payload": {
    "duration": 500,
    "pattern": "single"
  }
}
INBOUND

echo -e "\n=== TEST 3: Identischer Payload unter NEUER ID (Muss PASS sein!) ==="
cat << 'INBOUND' | python3 verify_idempotency.py
{
  "request_id": "REQ-002",
  "command": "vibrate",
  "payload": {
    "duration": 500,
    "pattern": "single"
  }
}
INBOUND

echo -e "\n=== Ledger Blocked Entries ==="
cat ledger_blocked.log 2>/dev/null || echo "Keine Blockierungen."
