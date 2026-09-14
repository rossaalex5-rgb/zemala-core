#!/usr/bin/env bash
CORE_DIR="$HOME/zemala-core"
LEDGER_FILE="$CORE_DIR/ledger/observations.jsonl"

echo -e "\033[1;36m[ZEMALA AUDIT] Starte On-Demand-Integritätsprüfung...\033[0m"

if [ ! -f "$LEDGER_FILE" ]; then
    echo -e "\033[1;31m[X] FAIL: Ledger nicht gefunden unter $LEDGER_FILE\033[0m"
    exit 1
fi

CORRUPT=0
LINE_NUM=0

# Härtung: IFS= read -r || [ -n "$line" ] fängt Zeilen ohne abschließenden Newline ab
while IFS= read -r line || [ -n "$line" ]; do
    LINE_NUM=$((LINE_NUM + 1))
    
    # Härtung: Leere Zeilen rasiermesserscharf überspringen (schützt vor False FAILs)
    [ -z "$line" ] && continue
    
    if ! echo "$line" | jq empty 2>/dev/null; then
        echo -e "\033[1;31m[X] Korrupte Zeile entdeckt in Zeile $LINE_NUM\033[0m"
        CORRUPT=1
    fi
done < "$LEDGER_FILE"

if [ $CORRUPT -eq 0 ]; then
    echo -e "\033[1;32m[✔] PASS: Alle $LINE_NUM Ledger-Einträge sind zu 100% JSON-valid und integer.\033[0m"
    termux-vibrate -d 50 2>/dev/null || true
    exit 0
else
    echo -e "\033[1;31m[X] FAIL: Integritätsprüfung fehlgeschlagen. Ledger korrumpiert!\033[0m"
    exit 1
fi
