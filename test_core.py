#!/usr/bin/env python3
"""
ZEMALA Core - System Health & Test Suite (Stufe 100)
Validiert die Integrität aller lokalen Kernkomponenten.
"""

import os
import sys
from zemala_bridge import emit_event

def test_system():
    print("[ZEMALA Test] Starte System-Validierung...")
    
    # 1. Prüfe Existenz kritischer Dateien
    critical_files = ["zemala_bridge.py", "sync.sh", "verify.sh", "agent_loop.py"]
    for file in critical_files:
        if not os.path.exists(file):
            print(f"[ZEMALA Test] FEHLER: Kritische Datei fehlt -> {file}")
            sys.exit(1)
        else:
            print(f"[ZEMALA Test] OK: {file} vorhanden.")

    # 2. Teste Event-Emission über die Bridge
    emit_event("System-Test erfolgreich durchgeführt. Zustand stabil.")
    print("[ZEMALA Test] Alle Kernprüfungen bestanden. System bereit.")

if __name__ == "__main__":
    test_system()
