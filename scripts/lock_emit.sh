#!/usr/bin/env bash
set -euo pipefail

LEDGER="$HOME/zemala-core/master_history.jsonl"
TYPE="${1:-SYSTEM}"
ACTION="${2:-SEAL_CREATED}"
SOURCE="${3:-SmallThinker-3B-Ollama}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 1. Append-only Ledger Schreibvorgang
echo "{\"timestamp\": \"$TIMESTAMP\", \"type\": \"$TYPE\", \"action\": \"$ACTION\", \"source\": \"$SOURCE\"}" >> "$LEDGER"
echo "[+] Event '$TYPE $ACTION' erfolgreich in Ledger versiegelt."

# 2. Direkter Discord-Webhook Push (Millisekunden-Takt via Python-Inline)
WEBHOOK_URL="https://discord.com/api/webhooks/1463047142473072721/0Gco0d7cSqpFq8OR_XSgF91zvzxw5YRPIIErht3WBCYN58-InLQ22w9eRv-5K3ASar1t"
python3 -c "
import requests, sys
url = '$WEBHOOK_URL'
payload = {'content': f'⚡ **ZEMALA-CORE EVENT** [{sys.argv[1]}] {sys.argv[2]} via {sys.argv[3]} at {sys.argv[4]}'}
try:
    requests.post(url, json=payload, timeout=5)
except Exception:
    pass
" "$TYPE" "$ACTION" "$SOURCE" "$TIMESTAMP" > /dev/null 2>&1 &
