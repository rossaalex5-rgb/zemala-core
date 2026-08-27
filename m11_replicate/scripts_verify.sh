#!/usr/bin/env bash
set -euo pipefail
LOGDIR="$HOME/zemala-core/logs"
FILE=$(ls -t "$LOGDIR"/*.jsonl 2>/dev/null | head -n 1 || true)

if [ -z "$FILE" ]; then
    echo "Fehler: Kein Log gefunden."
    exit 1
fi

# Wir nutzen jetzt den stabilen hasher.js
node ~/zemala-core/core/engine/hasher.js verify "$FILE"
