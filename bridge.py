from flask import Flask, request, jsonify
import os, time, json, hashlib, pathlib

API_TOKEN = os.environ.get("ZEMALA_BRIDGE_TOKEN","changeme")
OBS = pathlib.Path.home() / "zemala-core" / "observations.jsonl"
OBS.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

def write_observation(payload):
    ts = int(time.time())
    # letzter hash holen für Kette
    prev = "0"*64
    try:
        if OBS.exists():
            # letzte Zeile
            with open(OBS,"rb") as f:
                f.seek(-1024,2)
                lines=f.read().decode(errors="ignore").strip().splitlines()
                if lines:
                    last=json.loads(lines[-1])
                    prev=last.get("hash",prev)
    except: pass
    file_hash = hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    h = hashlib.sha256((prev+file_hash).encode()).hexdigest()
    obs = {"ts":ts,"prev_hash":prev,"file_hash":file_hash,"hash":h,"type":payload.get("type","chatbridge_turn"),"user":payload.get("user","alex"),"text":payload.get("text",""),"meta":payload.get("meta",{})}
    with open(OBS,"a") as out:
        out.write(json.dumps(obs,ensure_ascii=False)+"\n")
    return obs

@app.route("/observe",methods=["POST"])
def observe():
    auth=request.headers.get("Authorization","")
    if auth != f"Bearer {API_TOKEN}":
        return jsonify(error="unauthorized"),401
    data=request.get_json() or {}
    if data.get("text")=="ping":
        return jsonify(status="alive"),200
    obs=write_observation(data)
    return jsonify(status="saved",observation=obs),200

if __name__=="__main__":
    app.run(host="127.0.0.1",port=8765)
