import time, json, hashlib
from pathlib import Path

WATCH = Path.home() / "storage/shared/Download"
LEDGER = Path.home() / "zemala-core/observations.jsonl"

while True:
    for f in WATCH.glob("zemala_offline_kette*.json"):
        try:
            text = f.read_text(encoding="utf-8")
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            # anhängen
            with LEDGER.open("a", encoding="utf-8") as out:
                for entry in items:
                    out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.unlink()
            print(f"[AUTO] {f.name} -> Ledger +{len(items)}")
        except Exception as e:
            print(f"[ERR] {e}")
    time.sleep(5)
