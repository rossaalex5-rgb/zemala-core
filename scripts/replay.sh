#!/usr/bin/env bash
set -euo pipefail

LOGDIR="$HOME/zemala-core/logs"
FILE=$(ls -t "$LOGDIR"/*.jsonl 2>/dev/null | head -n 1 || true)

if [ -z "$FILE" ]; then
  echo "NO LOGS"
  exit 1
fi

echo "REPLAY:"
echo "FILE: $FILE"
echo ""

while read -r line; do
  echo "$line" | node -e "
    const fs = require('fs');
    const e = JSON.parse(fs.readFileSync(0,'utf8'));

    console.log('---');
    console.log('ID:', e.id);
    console.log('TYPE:', e.type);
    console.log('ACTION:', e.payload.action);
    console.log('SOURCE:', e.payload.source);
    console.log('HASH:', e.event_hash);
    console.log('TIME:', e.timestamp);
  "
done < "$FILE"
