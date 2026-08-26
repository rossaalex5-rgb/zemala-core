#!/usr/bin/env bash
# ZEMALA HUGGING FACE SINK [STUFE 100]
set -euo pipefail

echo "== [ZEMALA CORE] Initializing Hugging Face Sink Sync =="

# Pre-flight check via constitutional gates
if [ -f "verify_gates.sh" ]; then
    echo "[+] Running local gate verification before sync..."
    ./verify_gates.sh
fi

# Check for huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo "[!] huggingface-cli not found. Installing via pip..."
    pip install --upgrade huggingface_hub
fi

# Sync local repository/ledger to HF Space/Dataset
# Assumes HF_REPO environment variable is set or passed
HF_REPO_TARGET="${HF_REPO:-zemala-core-sink}"
echo "[+] Syncing verified state to Hugging Face repository: ${HF_REPO_TARGET}..."

# Upload ledger and core assets
huggingface-cli upload "${HF_REPO_TARGET}" events.jsonl --repo-type dataset || echo "[-] Upload warning: Check HF authentication (huggingface-cli login)."

echo "== [ZEMALA CORE] HF SINK SYNC COMPLETED =="
exit 0
