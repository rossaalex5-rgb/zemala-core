#!/usr/bin/env bash
# =============================================================================
# ZEMALA SABOTAGE TESTER (STUFE 100 - FAILURE INJECTION REFERENCE)
# Simuliert eine gezielte Ledger-Manipulation für das Live-Audit.
# =============================================================================
set -euo pipefail

Z_ROOT="$HOME/zemala-core"
LEDGER_FILE="$Z_ROOT/ledger/observations.jsonl"
VERIFY_SCRIPT="$Z_ROOT/scripts/verify_env.sh"

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}=============================================================${NC}"
echo -e "${CYAN}     ZEMALA SABOTAGE SIMULATION — INITIALISIERE...           ${NC}"
echo -e "${CYAN}=============================================================${NC}"

if [ ! -f "$LEDGER_FILE" ]; then
    echo -e "${RED}[✖] ERROR: Kein aktiver Ledger unter $LEDGER_FILE gefunden!${NC}"
    exit 1
fi

echo -e "${YELLOW}[INFO] Erstelle temporäres Backup des unbestechlichen Ledgers...${NC}"
BACKUP_FILE="${LEDGER_FILE}.bak"
cp "$LEDGER_FILE" "$BACKUP_FILE"
echo -e "${GREEN}[✔] Backup gesichert unter ${BACKUP_FILE}${NC}"

cleanup() {
    echo -e "\n${YELLOW}[CLEANUP] Bereinige Test-Injektion und stelle Originalzustand wieder her...${NC}"
    if [ -f "$BACKUP_FILE" ]; then
        mv "$BACKUP_FILE" "$LEDGER_FILE"
        echo -e "${GREEN}[✔] Original-Ledger erfolgreich wiederhergestellt.${NC}"
    fi
}
trap cleanup EXIT INT TERM

echo -e "\n${RED}[SABOTAGE] Injiziere unautorisiertes Rauschen in den Ledger...${NC}"
echo "ILLEGITIMATE_TAMPER_NOISE_VECTOR_$(date +%s)" >> "$LEDGER_FILE"
echo -e "${RED}[WARNUNG] Ledger-Integrität physisch gebrochen.${NC}"

echo -e "\n${YELLOW}[CHECK] Rufe unbestechlichen Pre-Flight Guard auf...${NC}"
if [ -f "$VERIFY_SCRIPT" ]; then
    if bash "$VERIFY_SCRIPT"; then
        echo -e "\n${RED}[✖] TEST FAILED: System hat die Manipulation NICHT erkannt!${NC}"
        exit 1
    else
        echo -e "\n${GREEN}[✔] SCHUTZ GEGRIFFEN: SYSTEM COMPROMISED: FAIL DETEKTIERT!${NC}"
        echo -e "${GREEN}[✔] Failsafe-Schild hat augenblicklich blockiert und eingefroren.${NC}"
    fi
else
    echo -e "${RED}[✖] Fehler: verify_env.sh nicht gefunden!${NC}"
    exit 1
fi

echo -e "\n${CYAN}=============================================================${NC}"
echo -e "SABOTAGE-CHECK ABGESCHLOSSEN — REVISIONS-NACHWEIS ERBRACHT."
echo -e "${CYAN}=============================================================${NC}"
