import pathlib, json, hashlib, time
WATCH = pathlib.Path.home() / "zemala-core" / "bridge_input"
OUT = pathlib.Path.home() / "zemala-core" / "observations.jsonl"
IGNORE = ["minetest","Inventur_notes","ZELLE","AIon_snapshot","logs",".gemini","tmp","file_history","mods"]
WATCH.mkdir(exist_ok=True)
def h(s): return hashlib.sha256(s.encode()).hexdigest()
prev = ""
if OUT.exists():
    try:
        prev = json.loads(open(OUT, encoding="utf-8").readlines()[-1])["hash"]
    except:
        pass
print(f"WATCH ONLY: {WATCH}")
while True:
    for f in WATCH.rglob("*"):
        if not f.is_file():
            continue
        if any(x in str(f) for x in IGNORE):
            continue
        try:
            txt = f.read_text(errors="ignore").strip()
            if not txt:
                continue
            fh = hashlib.sha256(f.read_bytes()).hexdigest()
            d = {"ts": int(time.time()), "prev_hash": prev, "file_hash": fh, "hash": h(prev+fh+txt), "type": "chatbridge_turn", "user": "alex", "text": txt, "meta": {"source": "bridge_input"}}
            open(OUT, "a", encoding="utf-8").write(json.dumps(d, ensure_ascii=False) + "\n")
            prev = d["hash"]
            print(f"+ {f.name}")
            f.unlink()
        except Exception as e:
            print(e)
    time.sleep(2)
