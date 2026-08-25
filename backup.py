import os
import shutil
from datetime import datetime

def backup_ledger():
    try:
        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/ledger_backup_{timestamp}.jsonl"
        
        if os.path.exists("ledger.jsonl"):
            shutil.copy("ledger.jsonl", backup_path)
            print(f"[ZEMALA Backup] Ledger erfolgreich gesichert unter {backup_path}.")
        else:
            print("[ZEMALA Backup] Kein Ledger zum Sichern gefunden.")
    except Exception as e:
        print(f"[ZEMALA Backup] Fehler beim Backup: {e}")

if __name__ == "__main__":
    backup_ledger()
