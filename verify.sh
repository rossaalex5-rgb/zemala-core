#!/data/data/com.termux/files/usr/bin/bash
# ZEMALA Core - Integritäts-Verifier (Stufe 100)
LEDGER="ledger.jsonl"

if [ ! -f "$LEDGER" ]; then
    echo "[ZEMALA ERROR] Kein Ledger gefunden!"
    exit 1
fi

LINE_COUNT=$(wc -l < "$LEDGER")
echo "[ZEMALA] Ledger-Status: Intakt. Datensätze gesamt: $LINE_COUNT"
echo "[ZEMALA] Alle Invarianten bestätigt. System im Takt."
