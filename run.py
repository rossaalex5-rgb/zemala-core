#!/usr/bin/env python3
import sys
import os
import subprocess

BASE_DIR = os.path.expanduser("~/zemala-core")
VERIFY_SCRIPT = os.path.join(BASE_DIR, "verify.sh")
GNOSIS_SCRIPT = os.path.join(BASE_DIR, "a2a_gnosis.py")
A2A_BRIDGE = os.path.join(BASE_DIR, "a2a_bridge.py")

def main():
    print("---------------------------------------------------------")
    print(" ZEMALA-CORE: RUNNER ACTIVATED [MCP / A2A / LEDGER]      ")
    print("---------------------------------------------------------")

    # 1. System-Integrität & Ledger-Verifikation (Verify-first)
    if os.path.exists(VERIFY_SCRIPT):
        print("[*] Prüfe Ledger & System-Integrität (verify.sh)...")
        if subprocess.run(["bash", VERIFY_SCRIPT]).returncode != 0:
            print("[-] BLOCK: Integritätsprüfung fehlgeschlagen. Abbruch.")
            sys.exit(1)

    # 2. A2A Bridge & Gnosis-Pipeline freigeben
    print("[*] Integrität verifiziert. Initialisiere A2A / Gnosis...")
    if os.path.exists(GNOSIS_SCRIPT):
        if subprocess.run(["python3", GNOSIS_SCRIPT]).returncode != 0:
            print("[-] BLOCK: Gnosis-Etappe abgebrochen.")
            sys.exit(1)

    if os.path.exists(A2A_BRIDGE):
        print("[*] Starte A2A Bridge Link...")
        subprocess.Popen(["python3", A2A_BRIDGE])

    print("[+] >>> SYSTEM RUNNING: A2A + LEDGER SECURED <<<")
    subprocess.run(["termux-vibrate", "-d", "300"], capture_output=True)

if __name__ == "__main__":
    main()
