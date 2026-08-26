#!/data/data/com.termux/files/usr/bin/bash
set -u

# ZEMALA MASTER EXECUTION PIPELINE
# INTENT -> GATE -> EXECUTE -> LEDGER COMMIT

INTENT_FILE="${1:-intent.json}"
LEDGER_FILE="ledger.jsonl"

echo "=== {ZEMALA CORE} PIPELINE INITIALIZED ==="

# Schritt 1: Pre-Ledger Admissibility Gate ausführen
./verify_intent.sh "$INTENT_FILE"
GATE_RC=$?

if [ "$GATE_RC" -ne 0 ]; then
    echo "[-] PIPELINE HALTED AT GATE"
    echo "[-] REASON: Intent failed admissibility check."
    # Optional: Den Fehlversuch als blockierte Evidenz dokumentieren
    echo "{\"status\": \"BLOCKED\", \"source\": \"$INTENT_FILE\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> ledger_blocked.log
    exit 1
fi

echo "[+] GATE PASSED. PROCEEDING TO EXECUTION & COMMIT..."

# Schritt 2: Exekusion & Ledger Commit (Beispielhafter Eintrag in den Ledger)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PAYLOAD_CONTENT=$(cat "$INTENT_FILE")

# Hier greift dein regulärer Ledger-Commit (Append-Only)
echo "{\"timestamp\": \"$TIMESTAMP\", \"status\": \"COMMITTED\", \"intent_data\": $PAYLOAD_CONTENT}" >> "$LEDGER_FILE"

echo "[+] LEDGER COMMIT SUCCESSFUL."
echo "=== PIPELINE COMPLETE ==="
exit 0
