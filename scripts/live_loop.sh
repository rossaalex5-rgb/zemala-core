#!/usr/bin/env bash
set -euo pipefail

LOGDIR="$HOME/zemala-core/logs"
FILE=$(ls -t "$LOGDIR"/*.jsonl 2>/dev/null | head -n 1 || true)

if [ -z "$FILE" ]; then
  echo "NO LOGS"
  exit 1
fi

echo "LIVE LOOP ACTIVE"
echo "WATCHING: $FILE"
echo ""

tail -n 0 -F "$FILE" | while read -r line; do

  echo "$line" | node -e "
    const e = JSON.parse(fs.readFileSync(0,'utf8'));

    console.log('--- LIVE EVENT ---');
    console.log('ID:', e.id);
    console.log('ACTION:', e.payload.action);
    console.log('TYPE:', e.type);
    console.log('TIME:', e.timestamp);

    if (e.payload.action === 'start') {
      console.log('[LIVE ROUTE] START');
    } else if (e.payload.action === 'stop') {
      console.log('[LIVE ROUTE] STOP');
    } else {
      console.log('[LIVE ROUTE] UNKNOWN');
    }
  "

done
