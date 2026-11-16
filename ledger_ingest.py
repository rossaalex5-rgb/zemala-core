import csv
import hmac
import hashlib
import json
from datetime import datetime, timezone

LEDGER_FILE = "clean_ledger.jsonl"
SECRET_KEY = b"zemala-secure-shared-secret"

def load_ledger():
    entries = []
    try:
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return entries

def verify_record_signature(record, signature):
    rec_copy = {k: v for k, v in record.items() if k != 'signature'}
    canonical_data = json.dumps(rec_copy, sort_keys=True)
    expected_sig = hmac.new(
        SECRET_KEY,
        canonical_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)

def ingest_csv_report(csv_filename):
    print(f"[INGEST] Reading external report from {csv_filename}...")
    records_to_ingest = []
    
    with open(csv_filename, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sig = row.pop("signature")
            try:
                row["metric_value"] = float(row["metric_value"])
            except ValueError:
                pass
            
            if verify_record_signature(row, sig):
                records_to_ingest.append(row)
                print(f"[INGEST] ✔ Valid signature for metric: {row['metric_name']} from {row['node_id']}")
            else:
                print(f"[INGEST] ❌ INVALID signature for record: {row}")

    if not records_to_ingest:
        print("[INGEST] No valid records to ingest.")
        return

    ledger = load_ledger()
    previous_hash = ledger[-1]["hash"] if ledger else "0" * 64
    index = ledger[-1]["index"] + 1 if ledger else 0

    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        for rec in records_to_ingest:
            timestamp = datetime.now(timezone.utc).isoformat()
            block_data = {
                "index": index,
                "timestamp": timestamp,
                "previous_hash": previous_hash,
                "payload": {
                    "event": "external_metric_ingest",
                    "record": rec
                }
            }
            block_string = json.dumps(block_data, sort_keys=True)
            current_hash = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
            
            complete_block = {
                **block_data,
                "hash": current_hash
            }
            
            f.write(json.dumps(complete_block) + "\n")
            previous_hash = current_hash
            index += 1

    print(f"[INGEST] Successfully ingested {len(records_to_ingest)} verified records into {LEDGER_FILE}.")

if __name__ == "__main__":
    ingest_csv_report("node_alpha_report.csv")
