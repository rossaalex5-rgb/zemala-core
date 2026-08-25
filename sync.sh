#!/bin/bash
# ZEMALA - Dual-Sync-Skript (GitHub + Hugging Face)
# Stufe 100 - Zero-Latency Vollzug

echo "[ZEMALA] Starte System-Synchronisation..."

# 1. Lokale Änderungen erfassen
git add .

# 2. Commit mit Zeitstempel im Zemala-Takt
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "[ZEMALA] Core Update: $TIMESTAMP [Stufe 100]"

# 3. Push zu GitHub (origin)
echo "[ZEMALA] Pushe zu GitHub (origin)..."
git push origin main

# 4. Push zu Hugging Face (hf) mit Force-Abdeckung für Remote-Init-Dateien
echo "[ZEMALA] Pushe zu Hugging Face (hf)..."
git push -f hf main

echo "[ZEMALA] Synchronisation auf allen Kanälen abgeschlossen. Felsenfest."
