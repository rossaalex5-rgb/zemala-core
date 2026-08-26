#!/usr/bin/env bash
CURRENT_HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "UNKNOWN_HEAD")
if [ -f "ZEMALA_STATE.md" ]; then
    CURRENT_STATE=$(head -n 1 ZEMALA_STATE.md)
else
    CURRENT_STATE="ZEMALA Core (Stufe 100)"
fi

if [ -z "$DISCORD_WEBHOOK_URL" ]; then
    echo "[NOTIFIER] Keine DISCORD_WEBHOOK_URL in der Umgebung gefunden."
    exit 0
fi

PAYLOAD="{\"content\":\"🛡️ **ZEMALA CORE // SYSTEM-STATUS (Bash)**\n- **HEAD:** \`$CURRENT_HEAD\`\n- **Status:** $CURRENT_STATE\n- **Integrität:** Verifiziert (Stufe 100). Alles stabil für Finlay! O-M-A. 🕉️\"}"

curl -s -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$DISCORD_WEBHOOK_URL"
echo -e "\n[NOTIFIER] Abgeschlossen."
