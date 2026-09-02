#!/usr/bin/env python3
# =============================================================================
# ZEMALA LUANTI/MINETEST BRIDGE (STUFE 100 - DETERMINISTIC COHERENCE)
# Liest den Ledger über den Canonical Path Resolver und füttert das HMI direkt
# =============================================================================

import os
import json
import sys
from pathlib import Path

# 1. Zwinge das Skript unter das unbestechliche Pfad-Gesetz (Abstraktionsschicht)
HERE = os.path.expanduser("~")
RESOLVER_PATH = os.path.join(HERE, "zemala-core", "bin", "zemala_paths.py")

if not os.path.isfile(RESOLVER_PATH):
    print(f"[✖] REJECT-BY-DEFAULT: Path resolver nicht gefunden unter {RESOLVER_PATH}", file=sys.stderr)
    sys.exit(2)

try:
    # Lade die einzig gültige Wahrheit über deine Verzeichnisstruktur
    import subprocess
    paths = json.loads(subprocess.check_output([sys.executable, RESOLVER_PATH]))
except Exception as e:
    print(f"[✖] REJECT: Fehler beim Laden der SSoT-Pfade: {e}", file=sys.stderr)
    sys.exit(1)

# Auflösung der Targets auf Basis deines canonical Gitter-Zustands
CORE_DIR = Path(paths.get("ZEMALA_CORE", os.path.join(HERE, "zemala-core")))
LEDGER_PATH = Path(paths.get("ZEMALA_LEDGER_FILE", CORE_DIR / "ledger" / "observations.jsonl"))

# Pfad zur Android-Sandbox von Luanti (Bypass über Scoped Storage Definition)
LUANTI_MOD_DIR = Path(paths.get("ZEMALA_VISUALIZER", "/sdcard/minetest/mods/zemala_visualizer"))
OUTPUT_JSON = LUANTI_MOD_DIR / "data.json"
OUTPUT_LUA = LUANTI_MOD_DIR / "init.lua"

def read_ledger():
    if not LEDGER_PATH.exists():
        print(f"[ZEMALA BRIDGE] [WARN] Ledger nicht gefunden unter {LEDGER_PATH}")
        return []
    
    entries = []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries

def process_state():
    # Stelle sicher, dass der Luanti-Mod-Ordner physisch existiert
    LUANTI_MOD_DIR.mkdir(parents=True, exist_ok=True)

    entries = read_ledger()
    latest_entry = entries[-1] if entries else {"status": "INITIALIZED", "loop_number": 0}
    
    state_data = {
        "node": "ZEMALA-CORE",
        "status": "CRYSTAL_LOCKED",
        "total_observations": len(entries),
        "latest": latest_entry
    }

    # Schreibe data.json direkt in die Luanti-Zollstation (0-Latenz-Vollzug)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2)

    # Generiere Luanti/Minetest Lua Modul-Zustand für asynchrones Polling
    lua_content = f"""-- ZEMALA HMI STATE - AUTO GENERATED
-- Takt: 3.47s | Status: CRYSTAL_LOCKED
zemala_state = {{
    total_obs = {len(entries)},
    last_hash = "{latest_entry.get('entry_hash', 'N/A')}",
    status = "ACTIVE"
}}
print("[ZEMALA HMI] State synchronisiert. Observations: " .. zemala_state.total_obs)
"""
    with open(OUTPUT_LUA, "w", encoding="utf-8") as f:
        f.write(lua_content)

    print(f"[✔] PASS: Zustand erfolgreich gebridget. HMI-Schnittstelle unter {LUANTI_MOD_DIR} gefüttert. (Einträge: {len(entries)})")

if __name__ == "__main__":
    process_state()
