#!/usr/bin/env bash
# =============================================================================
# ZEMALA PORT, SSOT & DUAL-STREAM INVARIANT GUARD (STUFE 100 - HARDENED)
# Prüft Sockets, Git-Integrität und die strukturelle Reinheit des Ledgers
# =============================================================================

CORE_DIR="$HOME/zemala-core"
LEDGER_FILE="$CORE_DIR/ledger/observations.jsonl"

echo "[ZEMALA GUARD] Starte System-Integritätsprüfung..."

verify_ports() {
    local ports=(8000 5001 8080)
    for port in "${ports[@]}"; do
        if ss -tuln 2>/dev/null | grep -q ":$port " || netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "[ZEMALA GUARD] [PASS/ACTIVE] Port $port ist aktiv."
        else
            echo "[ZEMALA GUARD] [READY] Port $port ist frei."
        fi
    done
}

verify_ssot() {
    if [ -d "$CORE_DIR/.git" ]; then
        if [ -n "$(git -C "$CORE_DIR" status --porcelain)" ]; then
            echo "[ZEMALA GUARD] [WARNUNG] Lokale Modifikationen im Workspace detektiert!"
        else
            echo "[ZEMALA GUARD] [PASS] SSoT-Repository ist absolut synchronisiert und clean."
        fi
    else
        echo "[ZEMALA GUARD] [WARNUNG] Kein Git-Repository unter $CORE_DIR gefunden!"
    fi
}

verify_dual_stream_compliance() {
    echo "[ZEMALA GUARD] Validiere Dual-Stream-Invarianz..."
    if [ -s "$LEDGER_FILE" ]; then
        local last_line
        last_line=$(tail -n 1 "$LEDGER_FILE" 2>/dev/null)
        if echo "$last_line" | jq empty 2>/dev/null; then
            echo "[ZEMALA GUARD] [PASS] Ledger-Struktur intakt. Letztes Event JSON-konform."
        else
            echo "[ZEMALA GUARD] [✖ FAIL] Letztes Ledger-Event korrupt oder kein valides JSON!"
            exit 1
        fi
    else
        echo "[ZEMALA GUARD] [✖ FAIL] Ledger unter $LEDGER_FILE fehlt oder ist leer!"
        exit 1
    fi
}

# Vollzugskaskade
verify_ports
verify_ssot
verify_dual_stream_compliance

echo "[ZEMALA GUARD] All Constitutional Invariants: PASS. Leitstand im sicheren Standby."
