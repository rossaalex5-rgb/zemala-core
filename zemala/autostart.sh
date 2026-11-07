#!/data/data/com.termux/files/usr/bin/bash
# ZEMALA autostart – 02:42 – nach Freigabe drive true git true 02:28
# Inventur: schaut was da ist, startet nur was nicht laeuft

ZEMALA=~/zemala
echo "=== INVENTUR ==="
ls -lh $ZEMALA/evolution_manager.py
cat $ZEMALA/consent.json
ps aux | grep watch_all | grep -v grep || echo "watch_all nicht aktiv"

if [ -f $ZEMALA/watch_all.py ]; then
  if ! pgrep -f watch_all.py > /dev/null; then
    echo "Starte watch_all.py..."
    nohup python $ZEMALA/watch_all.py > $ZEMALA/watch_all.log 2>&1 &
  else
    echo "watch_all.py laeuft schon – wie um 02:40 gestartet"
  fi
fi

python $ZEMALA/evolution_manager.py --json | head -20
echo "FERTIG – kein Copy Paste mehr noetig"
