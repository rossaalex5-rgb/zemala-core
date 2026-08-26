#!/data/data/com.termux/files/usr/bin/bash
set -u

# ZEMALA MASTER EXECUTION PIPELINE (TAKT 4)
# INTENT_RECEIVED -> VERIFY -> (COMMITTED | BLOCKED_EVIDENCE)

INTENT_FILE="${1:-intent.json}"
LEDGER_FILE="ledger.jsonl"
EVIDENCE_FILE="ledger_blocked.log"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "=== {ZEMALA CORE} PIPELINE TAKT 4 ==="

# 1. Roh-Evidenz: Intent ist eingegangen
echo "[*] Phase 1: Intent received from $INTENT_FILE"
INTENT_RAW=$(cat "$INTENT_FILE")

# 2. Gate-Prüfung ausführen
./verify_intent.sh "$INTENT_FILE"
GATE_RC=$?

if [ "$GATE_RC" -ne 0 ]; then
    echo "[-] Phase 2: Intent REJECTED by Gate."
    echo "[-] Phase 3: Action BLOCKED. Writing blocked evidence..."
    
    # Protokollierung als blockierte Evidenz (Keine Aktion im Haupt-Ledger!)
    echo "{\"timestamp\": \"$TIMESTAMP\", \"status\": \"ACTION_NOT_EXECUTED\", \"reason\": \"INTENT_GATE_FAILED\", \"source_intent\": $INTENT_RAW}" >> "$EVIDENCE_FILE"
    
    echo "[-] PIPELINE HALTED. EVIDENCE COMMITTED TO BLOCKED LOG."
    exit 1
fi

echo "[+] Phase 2: Intent ADMISSIBLE."
echo "[+] Phase 3: EXECUTING ACTION..."

# 3. Tatsächliche Aktion nur bei erfolgreicher Admissibilität
echo "{\"timestamp\": \"$TIMESTAMP\", \"status\": \"ACTION_COMMITTED\", \"intent_data\": $INTENT_RAW}" >> "$LEDGER_FILE"

echo "[+] PIPELINE COMPLETE: ACTION COMMITTED TO LEDGER."
exit 0
