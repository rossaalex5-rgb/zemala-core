import hashlib, datetime, json, os
BASE=os.path.expanduser("~/zemala")
LOG=os.path.join(BASE,"bauchgefuehl_sensor.log")
def h(s): return hashlib.sha256(s.encode()).hexdigest()
def bauch_check(payload, ctx="Uebergabe nach Ludwig"):
    errors=[]
    if not payload: errors.append("leer")
    if "E1" in payload and "§" not in payload: errors.append("E1 ohne §6 SOG SH §22 KdU - Bauch nein")
    if "Puff->Heim" in payload and "§75" not in payload: errors.append("Puff->Heim ohne §75")
    ok=len(errors)==0
    res={"time":datetime.datetime.now(datetime.timezone.utc).isoformat(),"ctx":ctx,"payload":payload[:80],"integrity":h(payload)[:12],"ok":ok,"errors":errors,"ludwig":"OK" if ok else f"NICHT {errors}"}
    print(f"{res['time']} - {res['ludwig']} - ok {ok} - {payload[:60]}")
    open(LOG,"a").write(json.dumps(res,ensure_ascii=False)+"\n")
    return ok
for p in ["Prio1 E1 Hotel 10 Zimmer §6 SOG SH §22 KdU","Prio2 E2 Puff->Heim §75","Prio3 E3 LAsD AföVO §45a","Prio4 E4 Content Creator ALLE"]:
    if not bauch_check(p):
        print("STOP - Bauch sagt nein - Fehler duerfen nicht passieren"); break
else:
    print("Alle Uebergaben nach Ludwig - Bauch 96M Neuronen sagt ja - keine Fehler")
