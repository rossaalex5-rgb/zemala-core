#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

OUTPUT_FILE = Path("output_metadata.json")

result = subprocess.run(
    [sys.executable, "verify_seal.py"]
)

if result.returncode != 0:
    print(
        f"[Gate-Block] Verifizierung fehlgeschlagen "
        f"(RC={result.returncode}). Transformation abgebrochen."
    )
    sys.exit(result.returncode)

output_data = {
    "status": "TRANSFORMED",
    "source": "ledger.jsonl",
    "gate": "VERIFIED"
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

print("[Gate-Pass] Transformation erfolgreich.")
print(f"OUTPUT={OUTPUT_FILE}")
sys.exit(0)
