#!/usr/bin/env python3
"""verify_changelog.py - Prüft die Changelog-Hash-Kette, lückenlos. Exit 0 = Kette geschlossen, Exit 1 = Lücke / Manipulation."""
import sys, json, hashlib, pathlib
def canon(o): return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)
p=pathlib.Path(__file__).parent / "evidence/changelog.jsonl"
if not p.exists():
    print("❌ changelog.jsonl fehlt"); sys.exit(1)
lines=[l for l in p.read_text().splitlines() if l.strip()]
prev="0"*64
for i,line in enumerate(lines):
    e=json.loads(line)
    if e["index"]!=i:
        print(f"❌ Index-Lücke: erwartet {i}, gefunden {e['index']}"); sys.exit(1)
    if e["prev_hash"]!=prev:
        print(f"❌ prev_hash mismatch bei Index {i}"); sys.exit(1)
    body={"index":e["index"],"timestamp":e["timestamp"],"type":e["type"],"data":e["data"],"prev_hash":e["prev_hash"]}
    h=hashlib.sha256(canon(body).encode("utf-8")).hexdigest()
    if h!=e["hash"]:
        print(f"❌ Hash mismatch bei Index {i}: erwartet {h[:16]}..., gefunden {e['hash'][:16]}..."); sys.exit(1)
    print(f"✅ Eintrag {i} {e['type']} {e['timestamp']} Hash {h[:16]}...")
    prev=e["hash"]
print(f"✅ CHANGELOG-KETTE GESCHLOSSEN: {len(lines)} Einträge (0..{len(lines)-1}), Head {prev}")
print(f"Head: {prev}")
sys.exit(0)
