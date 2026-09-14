#!/usr/bin/env bash
echo "🟢 [ZEMALA] Starte Ingress & Watchdog..."
nohup python3 a2a_server.py > server.log 2>&1 &
nohup python3 zemala_ledger_watchdog.py > watchdog.log 2>&1 &
echo "✨ Dienste im Hintergrund aktiv."
