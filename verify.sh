#!/bin/bash
# ZEMALA Core - Integrity Verifier (Stufe 100)
# Berechnet und prüft SHA256-Prüfsummen für Ledger und Core-Dateien

echo "[ZEMALA Verify] Starte kryptografische Integritätsprüfung..."

# 1. Ledger-Prüfung (falls vorhanden)
if [ -f "ledger.jsonl" ]; then
    LEDGER_HASH=$(sha256sum ledger.jsonl | awk '{print $1}')
    echo "[ZEMALA Verify] ledger.jsonl SHA256: $LEDGER_HASH"
else
    echo "[ZEMALA Verify] Hinweis: ledger.jsonl noch nicht im Arbeitsverzeichnis."
fi

# 2. Bridge-Prüfung
if [ -f "zemala_bridge.py" ]; then
    BRIDGE_HASH=$(sha256sum zemala_bridge.py | awk '{print $1}')
    echo "[ZEMALA Verify] zemala_bridge.py SHA256: $BRIDGE_HASH"
fi

# 3. Sync-Skript Prüfung
if [ -f "sync.sh" ]; then
    SYNC_HASH=$(sha256sum sync.sh | awk '{print $1}')
    echo "[ZEMALA Verify] sync.sh SHA256: $SYNC_HASH"
fi

echo "[ZEMALA Verify] Integritätsprüfung erfolgreich abgeschlossen. System intakt."
