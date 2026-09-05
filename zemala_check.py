#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors = []

# ZEMALA integrity inputs that must remain parseable.
for name in ("ledger.jsonl", "ledger/observations.jsonl"):
    path = ROOT / name
    if not path.exists():
        continue
    try:
        for n, line in enumerate(path.read_text(errors="strict").splitlines(), 1):
            if line.strip():
                json.loads(line)
    except Exception as e:
        errors.append(f"{name}:{n}: {e}")

# Seal must remain valid JSON if present.
seal = ROOT / "ledger_seal.json"
if seal.exists():
    try:
        json.loads(seal.read_text())
    except Exception as e:
        errors.append(f"ledger_seal.json: {e}")

if errors:
    print("ZEMALA_CHECK=FAIL")
    for error in errors:
        print(error)
    sys.exit(1)

print("ZEMALA_CHECK=PASS")
sys.exit(0)
