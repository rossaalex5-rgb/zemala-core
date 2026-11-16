import http.server
import socketserver
import json
import os
import hashlib
from datetime import datetime
from urllib.parse import parse_qs, urlparse

PORT = 3000
LEDGER_FILE = "zemala_value_ledger.jsonl"
RATE = 1000

def get_data():
    records = []
    total_eur = 0.0
    total_units = 0.0
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line.strip())
                        d['eur'] = float(d.get('eur', 0))
                        d['units'] = float(d.get('units', 0))
                        records.append(d)
                        total_eur += d['eur']
                        total_units += d['units']
                    except:
                        pass
    return records, total_eur, total_units

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            recs, total_eur, total_units = get_data()
            
            rows = ""
            for r in reversed(recs):
                rows += f"<tr><td>{r.get('timestamp','')}</td><td><b>{r.get('contributor','')}</b></td><td>{r.get('eur',0):,.2f} €</td><td style='color:#d4af37;'>+{r.get('units',0):,.1f} Units</td><td><a href='/certificate?name={r.get('contributor','')}' target='_blank' style='color:#d4af37;'>Zertifikat</a></td></tr>"

            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zemala Cockpit</title>
<style>
body {{ background:#080808; color:#f5f5f5; font-family:sans-serif; padding:20px; max-width:800px; margin:0 auto; }}
h1 {{ color:#d4af37; text-align:center; }}
.card {{ background:#141414; border:1px solid #222; padding:20px; border-radius:8px; margin-bottom:20px; }}
input, button {{ width:100%; padding:12px; margin-bottom:15px; background:#1c1c1c; border:1px solid #333; color:#fff; box-sizing:border-box; border-radius:4px; }}
button {{ background:#d4af37; color:#000; font-weight:bold; cursor:pointer; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ padding:10px; border-bottom:1px solid #222; text-align:left; }}
</style>
</head>
<body>
<h1>ZEMALA COCKPIT</h1>
<div class="card">
    <h3>Gesamt: {total_eur:,.2f} € | {total_units:,.1f} Units</h3>
</div>
<div class="card">
    <h3>Neuer Tausch</h3>
    <form action="/add" method="POST">
        <input type="text" name="contributor" required placeholder="Name des Investors">
        <input type="number" step="any" name="eur" required placeholder="Betrag in Euro">
        <button type="submit">Tausch erfassen & versiegeln</button>
    </form>
</div>
<div class="card">
    <h3>Historie</h3>
    <table>
        <tr><th>Zeit</th><th>Investor</th><th>Euro</th><th>Units</th><th>Aktion</th></tr>
        {rows if rows else '<tr><td colspan="5" style="color:#666;text-align:center;">Keine Transaktionen vorhanden.</td></tr>'}
    </table>
</div>
</body>
</html>"""
            response_bytes = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
            
        elif parsed.path == "/certificate":
            name = parse_qs(parsed.query).get("name", [""])[0]
            recs, _, _ = get_data()
            match = [r for r in recs if r.get("contributor","").lower() == name.lower()]
            if not match:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Zertifikat nicht gefunden.")
                return
            r = match[-1]
            cert = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Zertifikat - {r.get('contributor','')}</title>
<style>
body {{ background:#0b0b0b; color:#f5f5f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; font-family:sans-serif; }}
.cert {{ border:2px solid #d4af37; padding:40px; width:700px; background:#141414; }}
h1 {{ color:#d4af37; text-align:center; }}
.seal {{ background:#111; font-family:monospace; padding:10px; color:#d4af37; word-break:break-all; font-size:11px; margin-top:20px; }}
</style>
</head>
<body>
<div class="cert">
    <h1>ZEMALA ZERTIFIKAT</h1>
    <p><b>Investor:</b> {r.get('contributor','')}</p>
    <p><b>Units:</b> +{r.get('units',0):,.1f}</p>
    <p><b>Datum:</b> {r.get('timestamp','')}</p>
    <div class="seal">SHA-256: {r.get('seal','')}</div>
</div>
<script>window.onload=()=>window.print();</script>
</body>
</html>"""
            response_bytes = cert.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/add":
            length = int(self.headers.get('Content-Length', 0))
            data = parse_qs(self.rfile.read(length).decode('utf-8'))
            contrib = data.get("contributor", [""])[0].strip()
            try:
                eur = float(data.get("eur", [0])[0])
            except:
                eur = 0.0
            units = eur * RATE
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            seal = hashlib.sha256(f"{contrib}|{eur}|{units}|{ts}".encode('utf-8')).hexdigest()
            
            record = {
                "timestamp": ts,
                "contributor": contrib,
                "eur": eur,
                "units": units,
                "seal": seal
            }
            with open(LEDGER_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print(f"Zemala Server läuft auf http://localhost:{PORT}")
        httpd.serve_forever()
