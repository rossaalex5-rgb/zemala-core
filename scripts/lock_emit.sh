#!/usr/bin/env bash
set -euo pipefail
LOGDIR="$HOME/zemala-core/logs"
mkdir -p "$LOGDIR"

ID="evt_$(date +%s%N)"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
TYPE="${1:-SYSTEM}"
ACTION="${2:-noop}"
SOURCE="${3:-termux}"

TMP=$(mktemp)
cat > "$TMP" <<JSON
{"id":"$ID","timestamp":"$TS","type":"$TYPE","payload":{"action":"$ACTION","source":"$SOURCE"}}
JSON

# Hier war der Fehler: Wir rufen jetzt hasher.js richtig auf
HASH=$(node ~/zemala-core/core/engine/hasher.js create "$TMP")
OBJ=$(node -e "let j=JSON.parse(require('fs').readFileSync('$TMP','utf8')); j.event_hash='$HASH'; console.log(JSON.stringify(j));")

echo "$OBJ" >> "$LOGDIR/zemala_$(date +%Y-%m-%d).jsonl"
rm "$TMP"
echo "OK"
