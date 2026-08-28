#!/usr/bin/env bash
set -euo pipefail
# Auf eigenes Verzeichnis verankern, unabhängig vom Aufrufer (z.B. ifr_system)
cd "$(dirname "$0")/.."


LOGDIR="$HOME/zemala-core/logs"
mkdir -p "$LOGDIR"

TYPE="${1:-SYSTEM}"
ACTION="${2:-noop}"
SOURCE="${3:-termux}"

ID="evt_$(date +%N)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%S")"

TMP=$(mktemp)

cat > "$TMP" <<JSON
{
  "id": "$ID",
  "timestamp": "$TIMESTAMP",
  "type": "$TYPE",
  "payload": {
    "action": "$ACTION",
    "source": "$SOURCE",
    "metadata": {}
  }
}
JSON

# Korrigierter Pfad relativ zum Root-Verzeichnis ~/zemala-core
HASH=$(node -e '
const fs = require("fs");
const { hash } = require("./core/core/engine/canonical.js");
const obj = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
console.log(hash(obj));
' "$TMP")

node -e '
const fs = require("fs");
const file = process.argv[1];
const tmp = process.argv[2];
const hashVal = process.argv[3];
const obj = JSON.parse(fs.readFileSync(tmp, "utf8"));
obj.event_hash = hashVal;
fs.appendFileSync(file, JSON.stringify(obj) + "\n");
' "$LOGDIR/zemala_event_log_$(date +%Y-%m-%d).jsonl" "$TMP" "$HASH"

rm "$TMP"
echo "OK $ID"
