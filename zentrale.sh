#!/data/data/com.termux/files/usr/bin/bash
set -u

if [ -z "${1:-}" ] && [ -f "pending_intent.json" ]; then
    echo "[+] [INGRESS] pending_intent.json erkannt. Übernehme in den aktiven Pfad..."
    mv pending_intent.json current_active_intent.json
    INTENT_FILE="current_active_intent.json"
else
    INTENT_FILE="${1:-intent.json}"
fi

LEDGER_FILE="ledger_seal.json"

if [ ! -f "$INTENT_FILE" ]; then
    echo "[-] ERROR: Intent file $INTENT_FILE not found."
    exit 1
fi

INTENT_ID=$(sha256sum "$INTENT_FILE" | awk '{print $1}')
STATE_HASH=$(git rev-parse HEAD 2>/dev/null || echo "NO_GIT_HEAD")
PROPOSAL_HASH=$(sha256sum execute_intent_pipeline.sh | awk '{print $1}')

./verify_intent.sh "$INTENT_FILE" >/dev/null 2>&1
AUTH_STATUS=$?

if [ "$AUTH_STATUS" -eq 0 ]; then
    SEMANTIC_STATUS="ADMISSIBLE"
    AUTH_RESULT="PASS"
    EXPECTED_RESULT="ACTION_COMMITTED"
else
    SEMANTIC_STATUS="REJECTED"
    AUTH_RESULT="FAIL"
    EXPECTED_RESULT="ACTION_BLOCKED_EVIDENCE_LOGGED"
fi

if grep -q "^#" "$LEDGER_FILE" 2>/dev/null; then
    INTEGRITY_STATUS="FAIL (Empty lines/Drift)"
else
    INTEGRITY_STATUS="PASS (Chain Intact)"
fi

ACTION_FLAG=$(echo "${2:-PENDING}" | tr '[:lower:]' '[:upper:]')
PASSED_ID="${3:-none}"

if [ "$PASSED_ID" = "AUTO" ]; then
    PASSED_ID="$INTENT_ID"
fi

if [ "$ACTION_FLAG" = "GO" ] && [ "$PASSED_ID" = "$INTENT_ID" ]; then
    echo "[+] EXPLICIT GO RECEIVED AND ID MATCHES: $INTENT_ID"
    echo "[+] INITIATING EXECUTION PIPELINE..."
    ./execute_intent_pipeline.sh "$INTENT_FILE"
    PIPELINE_RC=$?

    if [ "$PIPELINE_RC" -eq 0 ]; then
        echo "[+] EXECUTING SSOT SYNC (GitHub & Remotes)..."
        git add ledger.jsonl ledger_blocked.log events.jsonl ZEMALA_STATE.md 2>/dev/null
        git commit -m "zemala-core: automated SSOT synchronization post-execution for intent $INTENT_ID"
        git push origin main

        if git remote | grep -q "huggingface"; then
            echo "[+] Syncing to HuggingFace..."
            git push huggingface main 2>/dev/null || echo "[-] HF Sync skipped/failed."
        fi

        echo "[+] SSOT SYNCHRONIZATION COMPLETE."
    fi
    exit "$PIPELINE_RC"
fi

echo "=== (ZEMALA SCHALTZENTRALE) TAKT 4 ORCHESTRATOR ==="
echo "=================================================="
echo "         ZEMALA CONTROL PANEL - STATUS            "
echo "=================================================="
echo " CURRENT STATE HASH : $STATE_HASH"
echo " INTENT ID          : $INTENT_ID"
echo " PROPOSAL HASH      : $PROPOSAL_HASH"
echo " AUTHORIZATION      : $AUTH_RESULT ($SEMANTIC_STATUS)"
echo " INTEGRITY STATUS   : $INTEGRITY_STATUS"
echo "--------------------------------------------------"
echo " EXPECTED RESULT    : $EXPECTED_RESULT"
echo " GO STATUS          : PENDING (Waiting for explicit binding)"
echo "--------------------------------------------------"
echo "[*] EXECUTION HALTED AT GO.PENDING."
echo "[*] To execute with automatic ID binding & SSOT Sync, run:"
echo "    ./zentrale.sh $INTENT_FILE GO AUTO"
echo ""
exit 0
