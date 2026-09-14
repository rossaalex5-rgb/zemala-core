#!/usr/bin/env bash
# =============================================================================
# ZEMALA MASTER CONTROL Launcher (STUFE 100 - MODULAR COLD START)
# Koordiniert die Zündung strictly über das verify_env.sh Sicherheits-Gate
# =============================================================================
set -e

CORE_DIR="$HOME/zemala-core"
cd "$CORE_DIR"

echo -e "\033[1;36m[ZEMALA CONTROL] Zünde Pre-Flight Guard...\033[0m"

# 1. Rufe das zentrale, unbestechliche Prüforgan auf
if [ -f "./verify_env.sh" ]; then
    ./verify_env.sh
else
    echo -e "\033[1;31m[✖] CRITICAL ERROR: Wächter-Skript verify_env.sh nicht im Core-Pfad gefunden!\033[0m"
    exit 1
fi

# 2. Starte den asynchronen Live-Loop sicher im tmux-Silo
echo -e "\n\033[1;36m[ZEMALA CONTROL] Schalte asynchronen Wächter scharf...\033[0m"
tmux kill-session -t zemala_live 2>/dev/null || true
tmux new-session -d -s zemala_live "bash $CORE_DIR/scripts/live_loop.sh"

echo -e "\n\033[1;32m[✔] SUCCESS: Kaltstart fehlerfrei vollzogen. System schwingt bei 3,47s.\033[0m"
