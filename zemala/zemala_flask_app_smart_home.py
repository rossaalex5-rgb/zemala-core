from flask import Flask, jsonify
import os, glob, re
app = Flask(__name__)
BASE = os.path.expanduser("~/zemala")
@app.route("/")
def index():
    return "<h1>ZEMALA State 100 Port 5001</h1><p>Handlung Bewegung Ergebnisse - Port 5000 tausendmal benutzt deshalb 5001</p><a href='/state'>/state</a> <a href='/ledger'>/ledger</a>"
@app.route("/state")
def state():
    loops = glob.glob(os.path.join(BASE, "ZEMALA_LOOP_*.md"))
    max_loop = 0
    for p in loops:
        m=re.search(r"ZEMALA_LOOP_(\d+)\.md", p)
        if m:
            max_loop = max(max_loop, int(m.group(1)))
    return jsonify({"state":100,"max_loop":max_loop,"port":5001,"msg":"Handlung Bewegung Ergebnisse"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
