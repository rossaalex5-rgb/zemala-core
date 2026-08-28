import sys
import os
import subprocess

LEDGER_FILE = "ledger.jsonl"
BACKUP_FILE = "ledger_backup.bin"

def run_verify_seal():
    """Führt verify_seal.py aus und gibt den echten Exit-Code zurück."""
    if not os.path.exists("verify_seal.py"):
        print("  [ERROR] verify_seal.py nicht gefunden!")
        return -1
    result = subprocess.run([sys.executable, "verify_seal.py"], capture_output=True, text=True)
    return result.returncode

def trigger_action(allowed: bool):
    """Visualisiert die Gate-Entscheidung."""
    if allowed:
        print("  [GATE VISUALIZATION] → ACTION (Zustand intakt, Ausführung erlaubt)")
    else:
        print("  [GATE VISUALIZATION] → BLOCK (Integritätsbruch erkannt, Aktion gesperrt)")

def main():
    print("=== ZEMALA M7.4 // EXACT EXIT-CODE FORENSIC PROOF ===")

    if not os.path.exists(LEDGER_FILE):
        print(f"[FATAL] Kanonischer Ledger '{LEDGER_FILE}' nicht gefunden.")
        sys.exit(1)

    # 1. Original-Bytes im Ist-Zustand sichern (ohne vorheriges Sync/Checkout)
    with open(LEDGER_FILE, "rb") as f:
        original_bytes = f.read()
    
    with open(BACKUP_FILE, "wb") as f:
        f.write(original_bytes)

    success = False
    try:
        # --- [ PHASE 1: BASELINE ] ---
        print("\n[PHASE 1] Baseline-Prüfung (Soll: RC = 0)")
        rc_base = run_verify_seal()
        print(f"  verify_seal.py Exit Code: {rc_base}")
        
        if rc_base != 0:
            print(f"  [FAIL] Baseline fehlgeschlagen (Erwartet: 0, Erhalten: {rc_base}).")
            trigger_action(allowed=False)
            sys.exit(1)
        
        print("  [PASS] Baseline exakt verifiziert (RC=0).")
        trigger_action(allowed=True)

        # --- [ PHASE 2: CRYPTOGRAPHIC DRIFT ] ---
        print("\n[PHASE 2] Injektion von Daten-Drift (Soll: RC = 1 durch Hash-Mismatch)")
        with open(LEDGER_FILE, "r+b") as f:
            content = f.read()
            if content:
                # Mutiert das erste Byte, um die SHA256-Signatur zu brechen
                tampered = b'X' + content[1:]
                f.seek(0)
                f.write(tampered)
                f.truncate()

        rc_drift = run_verify_seal()
        print(f"  verify_seal.py Exit Code: {rc_drift}")

        if rc_drift != 1:
            print(f"  [FAIL] Unerwarteter Drift-Code (Erwartet exakt 1 für Hash-Mismatch, Erhalten: {rc_drift}).")
            trigger_action(allowed=True)
            sys.exit(1)

        print("  [PASS] Drift exakt als Hash-Mismatch erkannt (RC=1).")
        trigger_action(allowed=False)

        # --- [ PHASE 3: RESTORE ] ---
        print("\n[PHASE 3] Wiederherstellung des Originalzustands (Soll: RC = 0 & Bytes identisch)")
        with open(LEDGER_FILE, "wb") as f:
            f.write(original_bytes)

        with open(LEDGER_FILE, "rb") as f:
            restored_bytes = f.read()

        bytes_match = (original_bytes == restored_bytes)
        print(f"  Original bytes == Restored bytes: {bytes_match}")
        if not bytes_match:
            print("  [FAIL] Wiederhergestellte Bytes weichen vom Original ab.")
            sys.exit(1)

        rc_restore = run_verify_seal()
        print(f"  verify_seal.py Exit Code: {rc_restore}")

        if rc_restore != 0:
            print(f"  [FAIL] System nach Restore nicht im Ursprungszustand (Erwartet: 0, Erhalten: {rc_restore}).")
            trigger_action(allowed=False)
            sys.exit(1)

        print("  [PASS] System nach Restore vollständig intakt (RC=0).")
        trigger_action(allowed=True)

        success = True

    finally:
        if os.path.exists(BACKUP_FILE):
            if not success:
                print("\n[CLEANUP] Stelle Original-Ledger aus Backup wieder her...")
                with open(BACKUP_FILE, "rb") as src, open(LEDGER_FILE, "wb") as dst:
                    dst.write(src.read())
            os.remove(BACKUP_FILE)

    if success:
        print("\n==================================================")
        print("RESULT: M7.4 PASS (Forensischer Nachweis exakt erbracht)")
        print("==================================================")
    else:
        print("\nRESULT: M7.4 FAIL")

if __name__ == "__main__":
    main()
