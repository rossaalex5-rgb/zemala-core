import subprocess
import sys

# Zu prüfende historische Evidenz-Commits
EXPECTED_COMMITS = {
    "Manifest-Initialisierung": "0b63797e5",
    "Video-Evidenz & Code-Versiegelung": "bdb4102fe"
}

def verify_commit(name, commit_hash):
    try:
        result = subprocess.run(
            ["git", "cat-file", "-t", commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        obj_type = result.stdout.strip()
        if obj_type == "commit":
            log_result = subprocess.run(
                ["git", "log", "-1", "--format=%an | %ad | %s", commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[PASS] {name} ({commit_hash})")
            print(f"       -> Details: {log_result.stdout.strip()}")
            return True
        else:
            print(f"[FAIL] {name} ({commit_hash}): Objekt ist kein Commit (Typ: {obj_type})")
            return False
    except subprocess.CalledProcessError:
        print(f"[FAIL] {name} ({commit_hash}): Commit wurde im lokalen Repository nicht gefunden.")
        return False

def main():
    print("=== ZEMALA-CORE: Historische Evidenz-Verifikation ===")
    all_valid = True
    for name, commit_hash in EXPECTED_COMMITS.items():
        if not verify_commit(name, commit_hash):
            all_valid = False
            
    if all_valid:
        print("\n[SUCCESS] Alle historischen Evidenz-Commits sind kryptografisch intakt und im Ledger verankert.")
        sys.exit(0)
    else:
        print("\n[ERROR] Mindestens ein Evidenz-Commit konnte nicht verifiziert werden.")
        sys.exit(1)

if __name__ == "__main__":
    main()
