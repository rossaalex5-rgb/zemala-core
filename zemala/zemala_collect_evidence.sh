#!/data/data/com.termux/files/usr/bin/bash
set -u
OUT="$HOME/zemala/zemala_live_state.json"
LEDGER="$HOME/zemala-core/observations.jsonl"
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
epoch=$(date +%s)
watcher=$(pgrep -f watch_all || echo none)
bridge=$(pgrep -f bridge || echo none)
bstat=$(python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8765)); print('BRIDGE UP'); s.close()" 2>&1 || echo 'BRIDGE DOWN')
rclone_remotes=$(rclone listremotes 2>&1 | tr '
' ' ')
ledger_lines=$(wc -l < $LEDGER 2>/dev/null || echo 0)
ledger_size=$(stat -c%s $LEDGER 2>/dev/null || echo 0)
ledger_sha=$(sha256sum $LEDGER 2>/dev/null | awk '{print $1}')
echo "{"meta":{"timestamp":"$timestamp","epoch":$epoch,"source":"Termux echte Messung"},"watcher":{"pid":"$watcher","exit":0},"rclone":{"raw":"$rclone_remotes"},"bridge":{"raw":"$bstat","pgrep":"$bridge"},"ledger":{"size":$ledger_size,"lines":$ledger_lines,"sha256":"$ledger_sha"}}" > $OUT
cat $OUT
