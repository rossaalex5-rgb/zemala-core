#!/usr/bin/env bash
set -euo pipefail
LOGDIR="$HOME/zemala-core/logs"
FILE=$(ls -t "$LOGDIR"/*.jsonl 2>/dev/null | head -n 1 || true)

if [ -z "$FILE" ]; then
    echo "Fehler: Kein log gefunden."
    exit 1
fi

# Exakter realer Pfad aus dem Test-Pass
node ~/zemala-core/core/core/engine/hasher.js verify "$FILE"
