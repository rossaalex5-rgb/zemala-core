#!/usr/bin/env bash
echo "=== 1. Kanonisierung (Soll-Hash) ==="
python3 ~/zemala/canonicalize_observation.py && echo "PASS"

echo "=== 2. Idempotenz-Wächter (Automatik-Test) ==="
echo '{"request_id": "t1", "command": "x", "payload": {"a": 1}}' | python3 ~/zemala/verify_idempotency.py && echo "PASS"

echo "=== 3. A2A Canonical Gate (7 Testvektoren) ==="
python3 ~/zemala/a2a_canonical_gate.py && echo "PASS (3 von 3 Pruefungen)"
