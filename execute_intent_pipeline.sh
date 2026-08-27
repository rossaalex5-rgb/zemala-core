#!/usr/bin/env bash
# ZEMALA MASTER EXECUTION PIPELINE (TAKT 4 + M2 ATOMIC COMMIT + SEAL)
set -u

INTENT_FILE="${1:-intent.json}"
LEDGER_FILE="ledger.jsonl"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "=== (ZEMALA CORE) PIPELINE TAKT 4 ==="

# 1. Roh-Evidenz einlesen
echo "[*] Phase 1: Intent received from $INTENT_FILE"
INTENT_RAW=$(cat "$INTENT_FILE")

# 2. Gate-Prüfung ausführen
./verify_intent.sh "$INTENT_FILE"
GATE_RC=$?

if [ $GATE_RC -ne 0 ]; then
    echo "[-] Phase 2: Intent REJECTED by Gate."
    exit 1
fi

echo "[+] Phase 2: Intent ADMISSIBLE."

# 3. Atomarer Commit über atomic_commit.py (M2 Invariante)
python3 atomic_commit.py < "$INTENT_FILE"
COMMIT_RC=$?

if [ $COMMIT_RC -ne 0 ]; then
    echo "[-] Phase 3: Intent BLOCKED (Replay/Duplicate detected)."
    exit 1
fi

echo "[+] Phase 3: ACTION COMMITTED TO LEDGER."

# 4. Nachgelagerter Sealing-Schritt (Nur bei erfolgreichem Commit)
python3 sealer.py
SEAL_RC=$?

if [ $SEAL_RC -ne 0 ]; then
    echo "[-] Phase 4: SEAL FAILED."
    exit 1
fi

echo "[+] PIPELINE COMPLETE: COMMIT + SEALED."
exit 0
