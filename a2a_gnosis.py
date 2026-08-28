#!/usr/bin/env python3
import json
import os
import sys
import requests
import subprocess

Z_ROOT = os.path.expanduser("~/zemala-core")
STATE_FILE = os.path.expanduser("~/zemala_system/zemala_state.json")
LOCK_EMIT_SCRIPT = os.path.join(Z_ROOT, "scripts/lock_emit.sh")
# Direkter Treffer auf dein laufendes Ollama-Backend (Port 11434)
OLLAMA_API = "http://localhost:11434/api/generate"

def main():
    if not os.path.exists(STATE_FILE):
        print(f"[-] Error: State file not found at {STATE_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    h = state.get("system", {}).get("hurst_exponent", 0.0)
    print(f"[*] Prüfe Hurst-Exponent: {h} via Ollama (Port 11434)")

    prompt = f"Frage: Ist Hurst={h} stabil? Antwort: JA\nFrage: Bestätige die Systemresonanz.\nAntwort:"
    payload = {
        "model": "small",  # Dein lokales SmallThinker-Modell in Ollama
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 2
        }
    }

    try:
        r = requests.post(OLLAMA_API, json=payload, timeout=15)
        res_data = r.json()
        answer = res_data.get("response", "").strip().upper()
        print(f"[*] Ollama Inferenz-Antwort: '{answer}'")
        
        if "JA" in answer or len(answer) < 5:
            if os.path.exists(LOCK_EMIT_SCRIPT):
                subprocess.run(["bash", LOCK_EMIT_SCRIPT, "SYSTEM", "SEAL_CREATED", "SmallThinker-3B-Ollama"], check=True)
            print("[+] Validierung erfolgreich & im Ledger versiegelt.")
            subprocess.run(["termux-vibrate", "-d", "300"], capture_output=True)
        else:
            print("[-] Gnosis negativ: Modell verweigert Resonanz.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[-] Inferenz-Fehler bei Ollama: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
