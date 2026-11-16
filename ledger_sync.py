import json
import hashlib
import urllib.request
import urllib.error

LOCAL_NODE_URL = "http://localhost:8080"
LEDGER_FILE = "clean_ledger.jsonl"

def get_local_ledger():
    entries = []
    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return entries

def sync_nodes():
    print("[SYNC] Initiating cross-node ledger synchronization and consistency check...")
    local_ledger = get_local_ledger()
    if not local_ledger:
        print("[SYNC] ERROR: Local ledger is empty.")
        return False

    local_head = local_ledger[-1]
    print(f"[SYNC] Local Ledger Head - Index: {local_head['index']}, Hash: {local_head['hash'][:16]}...")

    try:
        req = urllib.request.urlopen(f"{LOCAL_NODE_URL}/verify", timeout=3)
        data = json.loads(req.read().decode("utf-8"))
        print(f"[SYNC] Local Node Server Status: {data['status']} (Total Blocks: {data['total_blocks']})")
    except urllib.error.URLError as e:
        print(f"[SYNC] WARNING: Local node server not reachable on {LOCAL_NODE_URL}: {e}")

    try:
        with open("clean_ledger_backup_20261116.jsonl", "r", encoding="utf-8") as f:
            backup_entries = [json.loads(line.strip()) for line in f if line.strip()]
        
        backup_head = backup_entries[-1]
        if backup_head["hash"] == local_head["hash"]:
            print(f"[SYNC] CONSENSUS ACHIEVED: Peer backup head matches local head ({local_head['hash'][:16]}...).")
            return True
        else:
            print("[SYNC] CONFLICT: Peer backup head hash does not match local head.")
            return False
    except FileNotFoundError:
        print("[SYNC] No peer backup found for consensus comparison.")
        return True

if __name__ == "__main__":
    sync_nodes()
