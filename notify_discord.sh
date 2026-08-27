#!/usr/bin/env bash

OBS_FILE="observation.json"

# 1. Prüfen, ob ein Webhook konfiguriert ist
if [ -z "$DISCORD_WEBHOOK_URL" ]; then
    exit 0
fi

# 2. Prüfen, ob die verifizierte observation.json existiert
if [ ! -f "$OBS_FILE" ]; then
    exit 0
fi

# 3. Evidenz sicher via Python auslesen (verhindert jq-Abhängigkeiten)
EVAL_RESULT=$(python3 -c '
import json
from pathlib import Path
try:
    data = json.loads(Path("observation.json").read_text(encoding="utf-8"))
    status = data.get("verification_status", "UNKNOWN")
    seal = data.get("seal_hash", "UNKNOWN")
    req = data.get("last_request_id", "UNKNOWN")
    print(f"{status}|{seal}|{req}")
except Exception:
    print("ERROR||")
')

IFS="|" read -r STATUS SEAL_HASH LAST_REQ <<< "$EVAL_RESULT"

# 4. Harter Gatekeeper: Nur bei echtem VERIFIED senden
if [ "$STATUS" != "VERIFIED" ]; then
    exit 0
fi

# 5. Payload mit reiner, verifizierter Evidenz bauen
PAYLOAD="{\"content\":\"**ZEMALA CORE // OBSERVATION ANCHOR**\\n• Status: **VERIFIED**\\n• Seal-Hash: \`$SEAL_HASH\`\\n• Request-ID: \`$LAST_REQ\`\"}"

curl -s -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$DISCORD_WEBHOOK_URL" >/dev/null 2>&1
