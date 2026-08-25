#!/data/data/com.termux/files/usr/bin/bash
# ZEMALA Core - Lock & Emit (Stufe 100)
LEDGER="ledger.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PAYLOAD="${1:-"Default State Event"}"

if [ ! -f "$LEDGER" ]; then
    touch "$LEDGER"
    echo "[ZEMALA] Neues Ledger initialisiert."
fi

echo "{\"timestamp\": \"$TIMESTAMP\", \"level\": \"100\", \"payload\": \"$PAYLOAD\"}" >> "$LEDGER"
echo "[ZEMALA] Event verriegelt: $PAYLOAD ($TIMESTAMP)"
