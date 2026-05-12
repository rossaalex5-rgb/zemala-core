#!/usr/bin/env bash
# Liest das Event aus dem Stream (STDIN)
EVENT_DATA=$(cat)

# Validierung: Nur weitermachen, wenn JSON valide ist
if ! echo "$EVENT_DATA" | jq empty 2>/dev/null; then
    exit 1
fi

TYPE=$(echo "$EVENT_DATA" | jq -r '.type // "NONE"')
ACTION=$(echo "$EVENT_DATA" | jq -r '.payload.action // "NONE"')

# Reines Rule-Matching
if [[ "$TYPE" == "SYSTEM" && "$ACTION" == "wakeup" ]]; then
    ~/zemala-core/scripts/check_resources.sh
fi
