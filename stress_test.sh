#!/usr/bin/env bash
# ZEMALA STRESS & DRIFT TESTER [STUFE 100]
set -euo pipefail

echo "== [ZEMALA CORE] Starting Stress & Tamper Simulation =="

# Backup current ledger if exists
if [ -f "events.jsonl" ]; then
    cp events.jsonl events.jsonl.bak
fi

# Inject a malicious/unauthorized event (violating Auth Gate)
echo '{"malicious_tamper": true}' >> events.jsonl

echo "[?] Testing gate reaction to unauthorized injection..."
if ./verify_gates.sh; then
    echo "[-] CRITICAL FAIL: Gates did not block unauthorized event!"
    # Restore ledger
    [ -f "events.jsonl.bak" ] && mv events.jsonl.bak events.jsonl
    exit 1
else
    echo "[+] SUCCESS: Gates successfully intercepted and blocked the tamper attempt!"
    # Restore clean ledger
    [ -f "events.jsonl.bak" ] && mv events.jsonl.bak events.jsonl
    echo "== [ZEMALA CORE] STRESS TEST PASSED =="
    exit 0
fi
