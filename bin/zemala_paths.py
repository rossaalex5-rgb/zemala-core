#!/usr/bin/env python3
import json
import os
from pathlib import Path

HOME = Path.home()
CORE = HOME / "zemala-core"

paths = {
    "ZEMALA_CORE": str(CORE),
    "ZEMALA_LEDGER_FILE": str(CORE / "ledger" / "observations.jsonl"),
    "ZEMALA_VISUALIZER": str(Path("/sdcard/minetest/mods/zemala_visualizer"))
}

if __name__ == "__main__":
    print(json.dumps(paths))
