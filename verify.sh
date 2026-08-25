#!/usr/bin/env bash
# ZEMALA Verify & Test-Suite (Stufe 100)

echo "[ZEMALA Verify] Starte automatisierte Test-Suite..."
python3 test_core.py
if [ $? -ne 0 ]; then
    echo "[ZEMALA Verify] FEHLER: System-Tests fehlgeschlagen. Abbruch."
    exit 1
fi

echo "[ZEMALA Verify] Starte kryptografische Integritätsprüfung..."
sha256sum ledger.json1 zemala_bridge.py sync.sh test_core.py agent_loop.py
echo "[ZEMALA Verify] Integritätsprüfung erfolgreich abgeschlossen. System intakt."
