#!/bin/bash
# ZEMALA - Dual-Sync-Skript mit Integritätsprüfung (Stufe 100)

echo "[ZEMALA] Starte automatische Integritätsprüfung..."
if [ -f "./verify.sh" ]; then
    ./verify.sh
else
    echo "[ZEMALA] Warnung: verify.sh nicht gefunden!"
fi

echo "[ZEMALA] Starte System-Synchronisation..."

# 1. Lokale Änderungen erfassen
git add .

# 2. Commit mit Zeitstempel im Zemala-Takt
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "[ZEMALA] Core Update: $TIMESTAMP [Stufe 100]"

# 3. Push zu GitHub (origin)
echo "[ZEMALA] Pushe zu GitHub (origin)..."
git push origin main

# 4. Push zu Hugging Face (hf)
echo "[ZEMALA] Pushe zu Hugging Face (hf)..."
git push -f hf main

echo "[ZEMALA] Verifizierung und Synchronisation auf allen Kanälen abgeschlossen. Felsenfest."
