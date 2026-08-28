#!/usr/bin/env bash
set -euo pipefail

LEDGER="$HOME/zemala-core/master_history.jsonl"
TYPE="${1:-SYSTEM}"
ACTION="${2:-SEAL_CREATED}"
SOURCE="${3:-SmallThinker-3B-Ollama}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Append-only Ledger Schreibvorgang
echo "{\"timestamp\": \"$TIMESTAMP\", \"type\": \"$TYPE\", \"action\": \"$ACTION\", \"source\": \"$SOURCE\"}" >> "$LEDGER"
echo "[+] Event '$TYPE $ACTION' erfolgreich in Ledger versiegelt."
