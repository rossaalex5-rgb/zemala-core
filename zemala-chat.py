import json, hashlib, time, pathlib
OUT = pathlib.Path("observations_chats.jsonl")
def h(s): return hashlib.sha256(s.encode()).hexdigest()
prev=""
if OUT.exists() and OUT.stat().st_size>0:
    try: prev=json.loads(OUT.read_text(encoding="utf-8").splitlines()[-1])["hash"]
    except: pass
print("=== ZEMALA CHAT V2 - FERTIG ===")
print(f"Kette: {len(OUT.read_text().splitlines()) if OUT.exists() else 0} echte Sätze")
print("Logik durch Interaktion. Einfach tippen. exit = Ende\n")
while True:
    try:
        txt=input("> ").strip()
    except: break
    if not txt: continue
    if txt.lower()=="exit": break
    if txt.startswith("gespeichert") or txt.startswith("Du >"): continue
    if len(txt)<2: continue
    fh=h(txt)
    d={"ts":1791982876+int(time.time())%100000,"prev_hash":prev,"file_hash":fh,"hash":h(prev+fh+txt),"type":"chatbridge_turn","user":"alex","text":txt,"meta":{"source":"termchat","ts":int(time.time())}}
    open(OUT,"a",encoding="utf-8").write(json.dumps(d,ensure_ascii=False)+"\n")
    prev=d["hash"]
    print(f"  ok [{len(open(OUT).readlines())}]\n")
