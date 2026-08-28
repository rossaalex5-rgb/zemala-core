#!/usr/bin/env bash
# ZEMALA Verify & Test-Suite (Stufe 100)

echo "[ZEMALA Verify] Starte automatisierte Test-Suite..."
python3 test_core.py
if [ $? -ne 0 ]; then
  echo "[ZEMALA Verify] FEHLER: System-Tests fehlgeschlagen. Abbruch."
  exit 1
fi

echo "[ZEMALA Verify] Starte kryptografische Integritätsprüfung (Core)..."
sha256sum ledger.jsonl zemala_bridge.py sync.sh test_core.py agent_loop.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[ZEMALA Verify] FEHLER: Core-Checksummenprüfung fehlgeschlagen."
  exit 1
fi

echo "[ZEMALA Verify] Prüfe observations.jsonl Hash-Kette..."
python3 -c '
import json, hashlib, sys
ledger_path = "ledger/observations.jsonl"
try:
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        sys.exit(0)
    prev = "0" * 64
    for idx, line in enumerate(lines):
        item = json.loads(line)
        if item["prev_hash"] != prev:
            print(f"[!] FAIL: observations.jsonl Zeile {idx+1} - prev_hash Bruch.")
            sys.exit(1)
        canonical_json = json.dumps(item["payload"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        hasher = hashlib.sha256()
        hasher.update((prev + canonical_json).encode("utf-8"))
        if hasher.hexdigest() != item["hash"]:
            print(f"[!] FAIL: observations.jsonl Zeile {idx+1} - Hash-Signatur ungültig.")
            sys.exit(1)
        prev = item["hash"]
    print("[✓] observations.jsonl Kette intakt.")
except Exception as e:
    print(f"[!] FAIL: observations.jsonl Prüfung fehlgeschlagen: {e}")
    sys.exit(1)
'
if [ $? -ne 0 ]; then
  echo "[ZEMALA Verify] FEHLER: Observations-Ledger Integrität verletzt. STOP."
  exit 1
fi

echo "[ZEMALA Verify] Integritätsprüfung erfolgreich abgeschlossen. System intakt."
exit 0
