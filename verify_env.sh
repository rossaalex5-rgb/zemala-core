#!/usr/bin/env bash
# =============================================================================
# ZEMALA PORT & SSOT GUARD (STUFE 100 - IDENT_LOCKED)
# =============================================================================

CORE_DIR="$HOME/zemala-core"
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

verify_ports
verify_ssot
echo "[ZEMALA GUARD] Prüfung abgeschlossen. Leitstand im sicheren Standby."
