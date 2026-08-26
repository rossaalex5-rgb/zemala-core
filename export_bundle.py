import json, os, hashlib
from datetime import datetime
l, b = "ledger.jsonl", "MASTER_BUNDLE.md"
if os.path.exists(l):
    e, v = [], True
    with open(l, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    d = json.loads(line.strip())
                    sh = d.pop("hash", None)
                    if sh and hashlib.sha256(json.dumps(d, sort_keys=True).encode('utf-8')).hexdigest() != sh: v = False
                    if sh: d["hash"] = sh
                    e.append(d)
                except: pass
    le = e[-1] if e else {}
    txt = f"# ZEMALA MASTER BUNDLE // ANCHOR\n* Zeit: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n* Einträge: {len(e)}\n* Status: {'VERIFIZIERT' if v else 'FEHLER'}\n* Takt: 3,47s\n\n## Letzter Block\n```json\n{json.dumps(le, indent=2, ensure_ascii=False)}\n```"
    with open(b, "w", encoding="utf-8") as bf: bf.write(txt)
    print(f"[+] Bundle generiert. Status: {'VERIFIZIERT' if v else 'FEHLER'}")
else: print("[-] Kein Ledger.")
