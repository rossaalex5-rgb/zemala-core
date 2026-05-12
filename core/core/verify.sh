#!/usr/bin/env bash
set -euo pipefail

LOGDIR="$HOME/zemala-core/logs"
CONTRACT="$HOME/zemala-core/core/contracts/event.json"

echo "=== ZEMALA VERIFY ENGINE ==="

FILE=$(ls -t "$LOGDIR"/*.jsonl 2>/dev/null | head -n 1 || true)

if [ -z "$FILE" ]; then
  echo "❌ Keine Logs gefunden"
  exit 1
fi

SUCCESS=0
FAIL=0

while IFS= read -r line || [ -n "$line" ]; do

RESULT=$(node - <<NODE "$line"
const crypto = require('crypto');

const event = JSON.parse(process.argv[1]);

function canonicalize(obj){
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(canonicalize);
  return Object.keys(obj).sort().reduce((r,k)=>{
    r[k]=canonicalize(obj[k]); return r;
  },{});
}

const copy = JSON.parse(JSON.stringify(event));
const expected = copy.event_hash;
delete copy.event_hash;

const canonical = JSON.stringify(canonicalize(copy));
const computed = crypto.createHash('sha256').update(canonical).digest('hex');

console.log(computed === expected ? "OK" : "FAIL");
NODE
)

  if [ "$RESULT" = "OK" ]; then
    echo "[OK]"
    ((SUCCESS++))
  else
    echo "[FAIL]"
    ((FAIL++))
  fi

done < "$FILE"

echo "OK: $SUCCESS FAIL: $FAIL"
