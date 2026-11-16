import csv
import hmac
import hashlib
import json
from datetime import datetime, timezone

class ExternalNodeClient:
    def __init__(self, node_id, secret_key):
        self.node_id = node_id
        self.secret_key = secret_key.encode('utf-8')

    def generate_signed_record(self, metric_name, metric_value):
        timestamp = datetime.now(timezone.utc).isoformat()
        record = {
            "timestamp": timestamp,
            "node_id": self.node_id,
            "metric_name": metric_name,
            "metric_value": metric_value
        }
        canonical_data = json.dumps(record, sort_keys=True)
        signature = hmac.new(
            self.secret_key,
            canonical_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return {
            **record,
            "signature": signature
        }

    def export_csv_report(self, filename, records):
        fieldnames = ["timestamp", "node_id", "metric_name", "metric_value", "signature"]
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
        print(f"Standardized CSV report exported to {filename} with {len(records)} signed records.")

if __name__ == "__main__":
    node = ExternalNodeClient(node_id="node-alpha-01", secret_key="zemala-secure-shared-secret")
    
    records = [
        node.generate_signed_record("cpu_utilization", 14.5),
        node.generate_signed_record("memory_free_mb", 2048.0),
        node.generate_signed_record("ledger_sync_latency_ms", 1.2)
    ]
    
    node.export_csv_report("node_alpha_report.csv", records)
