import http.server, json, os, io, hashlib
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
PORT = 5000
LEDGER_PATH = "core/ledger.jsonl"
BAD = ["error", "contradiction", "widerspruch", "fail", "invalid", "mismatch"]
def _has(b, names):
    return any(n in b and b[n] not in [None, ""] for n in names)
def evaluate_aevo_contract(blocks):
    if not blocks:
        return False, "Ledger ist leer"
    latest = blocks[-1]
    for f in ["index", "timestamp", "prev_hash", "hash"]:
        if f not in latest or latest[f] in [None, ""]:
            return False, "Unvollstaendig: Feld " + f + " fehlt in Block " + str(latest.get("index", "?"))
    if not _has(latest, ["author", "Autor", "source", "sensor", "message", "msg", "data", "signal", "note", "telemetry", "battery", "payload"]):
        return False, "Unvollstaendig: Kein Inhalt in Block " + str(latest.get("index", "?"))
    if str(latest.get("contract_state", "")).lower() == "contradiction":
        return False, str(latest.get("note", "Widerspruch im Block")) + " [Block " + str(latest.get("index")) + "]"
    check = str(latest.get("message", "")) + " " + str(latest.get("note", "")) + " " + str(latest.get("msg", ""))
    check = check.lower()
    for term in BAD:
        if term in check:
            return False, "Widerspruch erkannt: " + term + " in Block " + str(latest.get("index"))
    tel = latest.get("telemetry", {})
    if isinstance(tel, dict) and "percentage" in tel:
        try:
            pct = float(tel["percentage"])
            if pct < 10:
                return False, "Widerspruch: Kritischer Hardware-Zustand (Akku " + str(pct) + "%) - bitte laden [Block " + str(latest.get("index")) + "]"
        except:
            pass
    if len(blocks) >= 2:
        prev = blocks[-2]
        expect = hashlib.sha256(json.dumps(prev, sort_keys=True).encode()).hexdigest()
        if latest.get("prev_hash") != expect:
            return False, "AEVO-Abweichung: Verkettung stimmt nicht"
    return True, "Contract eingehalten - Block ist vollstaendig, verkettet, ohne Widerspruch"
def render_sigil(seed_text, contract_verified=False):
    hash_hex = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    ext = bytearray()
    c = 0
    while len(ext) < 121:
        ext.extend(hashlib.sha256(hash_hex.encode() + c.to_bytes(4, "big")).digest())
        c += 1
    ext = ext[:121]
    voxels = np.zeros((11, 11, 5), dtype=bool)
    colors = np.empty((11, 11, 5), dtype=object)
    rel = {0: "#E03131", 1: "#2EB85C", 2: "#2F6FEB", 3: "#F3C81E"}
    gold = "#FFD700"
    for idx in range(121):
        x = idx % 11
        y = idx // 11
        b = ext[idx]
        height = (b % 4) + 1
        base = rel[(b >> 2) % 4]
        voxels[x, y, :height] = True
        for h in range(height):
            is_top = (h == height - 1)
            colors[x, y, h] = gold if (is_top and contract_verified) else base
    fig = plt.figure(figsize=(8, 6.5), facecolor="#0D1117")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#0D1117")
    ax.voxels(voxels, facecolors=colors, edgecolor="#161B22", linewidth=0.6)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    ax.set_zlim(0, 5)
    ax.set_axis_off()
    ax.view_init(elev=35, azim=45)
    status = "CONTRACT VERIFIZIERT - ZUSTAND: GOLD (4 Farben + Gold-Decke)" if contract_verified else "11x11 SIGIL - AUSGANGSZUSTAND (UNGEPRUEFT)"
    plt.suptitle("ZEMALA Core V2.3 - " + status, color="white", fontsize=11, fontweight="bold")
    plt.title("SHA-256: " + hash_hex[:16] + "...", color="#8B949E", fontsize=9, family="monospace")
    legend = "Unten: Relation (4 Farben) - Oben: GOLD = Zustand funktioniert" if contract_verified else "Rot=Herkunft  Gruen=Widerspruch  Blau=Bestaetigung  Gelb=Kausalitaet"
    fig.text(0.5, 0.05, legend, ha="center", color="#C9D1D9", fontsize=9)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor="#0D1117")
    plt.close(fig)
    return buf.getvalue()
def get_blocks():
    blocks = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        blocks.append(json.loads(line))
                    except:
                        pass
    return blocks
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        blocks = get_blocks()
        latest = blocks[-1] if blocks else {"init": "ZEMALA_SSOT_V3_EMPTY"}
        is_gold, reason = evaluate_aevo_contract(blocks)
        seed = json.dumps(latest, sort_keys=True)
        if self.path in ["/status", "/"]:
            body = json.dumps({"cadence": "3.47s", "status": "GOLD" if is_gold else "UNVERIFIED", "contract_verified": is_gold, "aevo_reason": reason, "total_blocks": len(blocks), "latest_block": latest}, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/sigil.png"):
            img = render_sigil(seed, contract_verified=is_gold)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(img)))
            self.end_headers()
            self.wfile.write(img)
        elif self.path.startswith("/sigil_raw.png"):
            img = render_sigil(seed, contract_verified=False)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(img)))
            self.end_headers()
            self.wfile.write(img)
        elif self.path == "/cockpit":
            badge = "GOLD" if is_gold else "UNGEPRUEFT / WIDERSPRUCH"
            html = "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>ZEMALA Auto-Cockpit</title><style>body{background:#0D1117;color:#C9D1D9;font-family:monospace;text-align:center;padding:15px} .badge{background:#FFD700;color:black;padding:4px 10px;border-radius:12px;font-weight:bold} input{width:90%;max-width:600px;padding:12px;margin:6px;border-radius:8px;border:1px solid #30363D;background:#161B22;color:white} button{background:#FFD700;color:black;border:none;padding:12px 20px;border-radius:8px;font-weight:bold;cursor:pointer;margin:6px} .box{background:#161B22;border:1px solid #30363D;padding:12px;border-radius:12px;max-width:600px;margin:10px auto;text-align:left}</style></head><body><h2>ZEMALA_SSOT_V3 AUTO-COCKPIT</h2><div>Contract: <span class=\"badge\">" + badge + "</span> | Bloecke: <b id=\"bcount\">" + str(len(blocks)) + "</b></div><p id=\"reason\">" + reason + "</p><div><button onclick=\"forceView()\">Auto-Modus (Live AEVO)</button><button onclick=\"forceRaw()\">Roh-Hash ansehen (4 Farben)</button></div><img id=\"sigil\" src=\"/sigil.png\" style=\"width:100%;max-width:600px\"><div class=\"box\"><h3>Live-Teilnahme: Sag es deinem Smartphone</h3><p>Beispiel: <i>Mach das Licht an</i> - wird zum Block, verkettet, Sigil schaltet um.</p><input id=\"name\" placeholder=\"Dein Name\"><input id=\"msg\" placeholder=\"Nachricht oder Smart-Home-Signal, z.B. Mach das Licht an\"><br><button onclick=\"submitBlock()\">Block ins Ledger schreiben</button><p id=\"result\"></p></div><script>let last=\"\";function forceView(){document.getElementById('sigil').src='/sigil.png?'+Date.now()}function forceRaw(){document.getElementById('sigil').src='/sigil_raw.png?'+Date.now()}async function submitBlock(){const name=document.getElementById('name').value||'Gast';const msg=document.getElementById('msg').value;if(!msg){alert('Bitte Nachricht eingeben');return}const res=await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,message:msg})});const data=await res.json();document.getElementById('result').innerText='Block #'+data.index+' geschrieben. Hash: '+data.hash.slice(0,16)+'... Status: '+data.contract_state+' - '+data.aevo_reason;forceView()}setInterval(async()=>{try{const res=await fetch('/status');const data=await res.json();document.getElementById('bcount').innerText=data.total_blocks;document.getElementById('reason').innerText=data.aevo_reason;document.getElementById('badge').innerText=data.contract_verified?'GOLD':'UNGEPRUEFT / WIDERSPRUCH';document.getElementById('sigil').src='/sigil.png?'+Date.now()}catch(e){}},3470)</script></body></html>"
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode() or "{}")
            blocks = get_blocks()
            prev_hash = hashlib.sha256(json.dumps(blocks[-1], sort_keys=True).encode()).hexdigest() if blocks else "GENESIS"
            entry = {"index": len(blocks) + 1, "timestamp": datetime.now(timezone.utc).isoformat(), "author": data.get("name", "Gast"), "message": data.get("message", ""), "prev_hash": prev_hash, "type": "USER_SUBMIT"}
            entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
            os.makedirs("core", exist_ok=True)
            with open(LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            is_gold, reason = evaluate_aevo_contract(blocks + [entry])
            out = {"index": entry["index"], "hash": entry["hash"], "contract_state": "GOLD" if is_gold else "CONTRADICTION", "aevo_reason": reason, "sigil_url": "/sigil.png"}
            body = json.dumps(out).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        return
if __name__ == "__main__":
    http.server.HTTPServer(("0.0.0.0", PORT), H).serve_forever()
