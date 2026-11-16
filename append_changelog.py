#!/usr/bin/env python3
"""append_changelog.py - Hängt einen neuen Eintrag an die Changelog-Kette an. Nie editieren, nur anhängen."""
import argparse, json, hashlib, pathlib, datetime, sys
def canon(o): return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)
base=pathlib.Path(__file__).parent
chain=base/"evidence/changelog.jsonl"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument("--type", required=True, help="z.B. COMMIT, VALIDATION_DECISION_RUN, VALIDATION_PRECOMMIT")
ap.add_argument("--commit-sha", default=None)
ap.add_argument("--result", default="PASS")
ap.add_argument("--desc", default="")
args=ap.parse_args()
lines=[l for l in chain.read_text().splitlines() if l.strip()] if chain.exists() else []
prev=json.loads(lines[-1])["hash"] if lines else "0"*64
idx=len(lines)
ts=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
six=["STARTEN.sh","verify_ledger.py","zemala_orchestrator.sh","zemala_manifest.json","evidence/ledger.jsonl","evidence/ledger_anchor.json"]
hashes={rel: sha(base/rel) for rel in six}
audit=json.loads((base/"evidence/ledger_audit.json").read_text()) if (base/"evidence/ledger_audit.json").exists() else {}
data={"desc": args.desc or f"Angehängt via append_changelog.py, Typ {args.type}",
  "hashes_6": hashes, "audit_status": audit.get("status"), "audit_head": audit.get("head_hash"), "audit_block_count": audit.get("block_count"),
  "audit_manifest_hash": audit.get("manifest_hash"), "result": args.result,
  "commit_sha": args.commit_sha, "commit_status": "VERIFIZIERT - voller SHA im Commit" if args.commit_sha else "PENDING"}
body={"index": idx, "timestamp": ts, "type": args.type, "data": data, "prev_hash": prev}
h=hashlib.sha256(canon(body).encode("utf-8")).hexdigest()
entry=dict(body); entry["hash"]=h
with chain.open("a") as f: f.write(json.dumps(entry, sort_keys=True, separators=(",",":"))+"\n")
print(f"✅ Angehängt: Index {idx} Typ {args.type} Hash {h}")
print(f"Neuer Head (prev_hash für nächsten Eintrag): {h}")
print("Nächster Schritt: python3 verify_changelog.py, dann CHANGELOG_ZEMALA.md regenerieren (siehe append-Anleitung in CHANGELOG_ZEMALA.md), dann mitpushen.")
