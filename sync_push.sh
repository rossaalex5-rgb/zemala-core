#!/bin/bash
git add MASTER_BUNDLE.md ledger.jsonl status_server.py
git commit -m "ZEMALA STUFE 100: Automatisierter Runtime-Evidence-Sync $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main
echo "[+] Master-State erfolgreich zu GitHub gepusht."
