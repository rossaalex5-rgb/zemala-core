#!/bin/bash
# STARTEN.sh - Zemala Master Orchestrator, Einstiegspunkt.
# KEINE eigenen Checks, KEINE Env-Overrides, KEIN Demo-Modus.
# EINE Regel: JEDE ZEMALA_* = FAIL. Prod ist Default. Kein Demo.
# Delegiert zu 100% an zemala_orchestrator.sh (gleiche harte Regeln:
# Manifest zuerst, ZEMALA_*-Sperre, strikte Reihenfolge, Audit zuletzt).
# Wer STARTEN.sh direkt aufruft, bekommt exakt denselben Beweis wie
# ueber zemala_orchestrator.sh. Argumente werden vom Orchestrator abgelehnt.
# Bidirektional: STARTEN -> Orchestrator -> verify_ledger.py v3 FINAL (--anchor Pflicht, --write-anchor entfernt).
# +x-unabhaengig: exec via bash, damit ein verlorenes +x nach Git-Sync den Push nie blockiert.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$SCRIPT_DIR/zemala_orchestrator.sh" "$@"
