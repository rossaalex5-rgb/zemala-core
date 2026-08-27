import sys
import os
import subprocess
import shutil

LEDGER_FILE = "ledger.jsonl"
BACKUP_FILE = "ledger_backup.bin"

def get_file_bytes(filepath):
    if not os.path.exists(filepath):
        return b""
    with open(filepath, "rb") as f:
        return f.read()

def run_system_verify():
    if not os.path.exists("verify.sh"):
        print("  [ERROR] verify.sh nicht gefunden!")
        return 1
    result = subprocess.run(["./verify.sh"], capture_output=True, text=True)
    return result.returncode

def trigger_action(allowed: bool):
    if allowed:
        print("→ ACTION")
    else:
        print("→ NO ACTION")

print("=== ZEMALA M7.4 // HUMAN-OBSERVABLE DRIFT DEMO ==.")

if not os.path.exists(LEDGER_FILE):
    print(f"[FATAL] {LEDGER_FILE} existiert nicht.")
    sys.exit(1)

original_bytes = get_file_bytes(LEDGER_FILE)
with open(BACKUP_FILE, "wb") as f:
    f.write(original_bytes)

# [1] BASELINE
print("\nBASELINE")
rc_base = run_system_verify()
print(f"verify.sh RC={rc_base}")
if rc_base == 0:
    print("→ VERIFIED")
    trigger_action(allowed=True)
else:
    print("→ FAIL")
    print("→ BLOCKED")
    trigger_action(allowed=False)
    print("\nRESULT: M7.4 FAIL (Baseline unexpected failure)")
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
    sys.exit(1)

# [2] SEMANTIC DRIFT
print("\nSEMANTIC DRIFT")
with open(LEDGER_FILE, "ab") as f:
    f.write(b'{"tampered": true}\n')

rc_drift = run_system_verify()
print(f"verify.sh RC={rc_drift}")
if rc_drift != 0:
    print("→ FAIL")
    print("→ BLOCKED")
    trigger_action(allowed=False)
else:
    print("→ VERIFIED [KRITISCHER FEHLER: Drift unerkannt!]")
    trigger_action(allowed=True)
    with open(LEDGER_FILE, "wb") as f:
        f.write(original_bytes)
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
    print("\nRESULT: M7.4 FAIL (Drift detection failed)")
    sys.exit(1)

# [3] RESTORE
print("\nRESTORE")
with open(LEDGER_FILE, "wb") as f:
    f.write(original_bytes)

restored_bytes = get_file_bytes(LEDGER_FILE)
bytes_match = (original_bytes == restored_bytes)
print(f"original bytes == restored bytes: {bytes_match}")

rc_restore = run_system_verify()
print(f"verify.sh RC={rc_restore}")
if rc_restore == 0 and bytes_match:
    print("→ VERIFIED")
    trigger_action(allowed=True)
else:
    print("→ FAIL")
    print("→ BLOCKED")
    trigger_action(allowed=False)
    print("\nRESULT: M7.4 FAIL (Restore failed)")
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
    sys.exit(1)

if os.path.exists(BACKUP_FILE):
    os.remove(BACKUP_FILE)

print("\nRESULT: M7.4 PASS")
