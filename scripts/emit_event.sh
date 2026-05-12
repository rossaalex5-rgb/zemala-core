#!/usr/bin/env bash
set -euo pipefail

LOGDIR="$HOME/zemala-core/logs"
mkdir -p "$LOGDIR"

TYPE="${1:-SYSTEM}"
ACTION="${2:-noop}"
SOURCE="${3:-termux}"

ID="evt_$(date +%s%N)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

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

HASH=$(node -e "
const fs=require('fs');
const crypto=require('crypto');
const obj=JSON.parse(fs.readFileSync('$TMP','utf8'));
const canonical=JSON.stringify(obj);
console.log(crypto.createHash('sha256').update(canonical).digest('hex'));
")

obj=$(cat "$TMP")
echo "$obj" | node -e "
const fs=require('fs');
const input=fs.readFileSync(0,'utf8');
const obj=JSON.parse(input);
obj.event_hash='$HASH';
console.log(JSON.stringify(obj));
" >> "$LOGDIR/zemala_event_log_$(date +%Y-%m-%d).jsonl"

echo "OK $ID"
