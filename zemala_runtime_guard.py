import os
import json
import hashlib
from datetime import datetime

LOCK_FILE = "zemala-core.lock"
PENDING_FILE = "pending_intent.json"
LEDGER_FILE = "ledger.jsonl"
RESTART_FILE = "restart_state.json"

def log_evidence(invariant, result, reason=""):
    event = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "CONSTITUTIONAL_GUARD",
        "invariant": invariant,
        "result": result,
        "reason": reason
    }
    entry_str = json.dumps(event, sort_keys=True)
    event["hash"] = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def check_singleton():
    """C-PROC-01: Atomarer Singleton-Lock."""
    if os.path.exists(LOCK_FILE):
        log_evidence("C-PROC-01", "BLOCKED", "Duplicate instance lock exists")
        return False
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    log_evidence("C-PROC-01", "PASS")
    return True

def check_ingress(intent_data):
    """C-INGRESS-01: Pending Collison / Single Queue."""
    if os.path.exists(PENDING_FILE):
        log_evidence("C-INGRESS-01", "BLOCKED", "Unconsumed pending_intent exists")
        return False
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(intent_data, f)
    log_evidence("C-INGRESS-01", "PASS")
    return True

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

if __name__ == "__main__":
    print("[*] Teste Constitutional Runtime Guard...")
    if check_singleton():
        print("[+] C-PROC-01: PASS")
        if check_ingress({"intent": "Test Intent"}):
            print("[+] C-INGRESS-01: PASS")
        release_lock()
    else:
        print("[-] C-PROC-01: BLOCKED (Duplicate)")
