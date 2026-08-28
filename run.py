#!/usr/bin/env python3
import sys
import os
import subprocess

BASE_DIR = os.path.expanduser("~/zemala-core")
VERIFY_SCRIPT = os.path.join(BASE_DIR, "verify.sh")
GNOSIS_SCRIPT = os.path.join(BASE_DIR, "a2a_gnosis.py")

def main():
    print("==================================================")
    print("   ZEMALA-CORE AUTOMATED FAIL-CLOSED ENGINE      ")
    print("==================================================")

    # 1. Gnosis / Inferenz ausführen
    if subprocess.run(["python3", GNOSIS_SCRIPT]).returncode != 0:
        print("[-] FAIL-CLOSED: Gnosis-Etappe abgebrochen.")
        sys.exit(1)
    
    # 2. Integritätsprüfung (falls verify.sh existiert)
    if os.path.exists(VERIFY_SCRIPT):
        print("[*] Zünde Integritätsabgleich (verify.sh)...")
        if subprocess.run(["bash", VERIFY_SCRIPT]).returncode != 0:
            print("[-] FAIL-CLOSED: Integritätsprüfung fehlgeschlagen!")
            sys.exit(1)
            
    print("[+] >>> AUDIT RESULT: PASS <<<")
    subprocess.run(["termux-vibrate", "-d", "500"], capture_output=True)

if __name__ == "__main__":
    main()
