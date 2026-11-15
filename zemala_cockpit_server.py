import http.server
import json
import os
import io
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PORT = 5000
LEDGER_PATH = "core/ledger.jsonl"

def evaluate_aevo_contract(blocks: list):
    if not blocks:
        return False, "Ledger ist leer (Warte auf Genesis-Block)"
    
    latest = blocks[-1]
    raw_str = json.dumps(latest, sort_keys=True).lower()

    forbidden_terms = ["error", "contradiction", "widerspruch", "fail", "invalid", "mismatch"]
    for term in forbidden_terms:
        if term in raw_str:
            return False, f"Widerspruch erkannt: '{term}' im Block gefunden"

    if len(blocks) >= 2:
        prev = blocks[-2]
        prev_hash = prev.get("hash") or prev.get("block_hash") or prev.get("sha256")
        claimed_prev = latest.get("prev_hash") or latest.get("previous_hash") or latest.get("parent_hash")
        if prev_hash and claimed_prev and prev_hash != claimed_prev:
            return False, "AEVO-Abweichung: prev_hash stimmt nicht mit Vorgaenger-Block ueberein"

    if len(latest.keys()) >= 2:
        return True, "AEVO-Contract erfuellt: Verkettung intakt, kein Widerspruch (GOLD)"
    
    return False, "Unvollstaendiger Block (Zu wenige Attribute)"

def render_sigil_bytes(seed_text: str, contract_verified: bool = False) -> bytes:
    hash_hex = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
    hash_bytes = bytes.fromhex(hash_hex)
    
    extended_bytes = bytearray()
    counter = 0
    while len(extended_bytes) < 121:
        chunk = hashlib.sha256(hash_bytes + counter.to_bytes(4, 'big')).digest()
        extended_bytes.extend(chunk)
        counter += 1
    extended_bytes = extended_bytes[:121]

    grid_size = 11
    voxels = np.zeros((grid_size, grid_size, 5), dtype=bool)
    colors = np.empty(voxels.shape, dtype=object)

    relation_colors = {0: '#D9383A', 1: '#2EA043', 2: '#1F6FEB', 3: '#E3B341'}
    gold_color = '#FFD700'

    for idx in range(121):
        x = idx % grid_size
        y = idx // grid_size
        byte_val = extended_bytes[idx]

        if contract_verified:
            height = 1
            color = gold_color
        else:
            height = (byte_val % 4) + 1
            color_code = (byte_val >> 2) % 4
            color = relation_colors[color_code]

        voxels[x, y, :height] = True
        colors[x, y, :height] = color

    fig = plt.figure(figsize=(8, 6.5), facecolor='#0D1117')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0D1117')
    ax.voxels(voxels, facecolors=colors, edgecolor='#161B22', linewidth=0.6)
    ax.set_box_aspect((11, 11, 3.5))
    ax.set_zlim(0, 5)
    ax.set_axis_off()
    ax.view_init(elev=35, azim=45)

    status_text = "CONTRACT VERIFIZIERT - ZUSTAND: GOLD" if contract_verified else "11x11 SIGIL - WIDERSPRUCH / UNGEPRUEFT"
    plt.suptitle(f"ZEMALA_SSOT_V3 | {status_text}", color='#FFD700' if contract_verified else 'white', fontsize=12, fontweight='bold', y=0.94)
    plt.title(f"SHA-256: {hash_hex}", color='#8B949E', fontsize=8, family='monospace', pad=8)

    legend_text = "GOLD = Contract automatisch verifiziert (AEVO-konform)" if contract_verified else "Rot=Herkunft  Gruen=Widerspruch  Blau=Bestaetigung  Gelb=Kausalitaet"
    fig.text(0.5, 0.05, legend_text, ha='center', color='#C9D1D9', fontsize=9)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='#0D1117')
    plt.close(fig)
    buf.seek(0)
    return buf.read()

def get_latest_ledger_data():
    blocks = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        blocks.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return blocks

class ZemalaCockpitHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        try:
            blocks = get_latest_ledger_data()
            latest = blocks[-1] if blocks else {"init": "ZEMALA_SSOT_V3_EMPTY"}
            seed_str = json.dumps(latest, sort_keys=True)
            is_gold, reason = evaluate_aevo_contract(blocks)

            if self.path == "/status" or self.path == "/":
                response_data = {
                    "system": "ZEMALA_SSOT_V3",
                    "cadence": "3.47s",
                    "status": "GOLD" if is_gold else "UNVERIFIED",
                    "contract_verified": is_gold,
                    "aevo_reason": reason,
                    "total_blocks": len(blocks),
                    "latest_block": blocks[-1] if blocks else None
                }
                body = json.dumps(response_data, indent=2).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            elif self.path.startswith("/sigil.png"):
                img_bytes = render_sigil_bytes(seed_str, contract_verified=is_gold)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(img_bytes)))
                self.end_headers()
                self.wfile.write(img_bytes)

            elif self.path.startswith("/sigil_raw.png"):
                img_bytes = render_sigil_bytes(seed_str, contract_verified=False)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(img_bytes)))
                self.end_headers()
                self.wfile.write(img_bytes)

            elif self.path == "/cockpit":
                badge_color = "#B8860B" if is_gold else "#D9383A"
                badge_text = "GOLD (VERIFIZIERT)" if is_gold else "UNGEPRÜFT / WIDERSPRUCH"
                html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZEMALA Auto-Cockpit V2.3</title>
<style>
  body {{ background:#0D1117; color:#C9D1D9; font-family:monospace; text-align:center; padding:15px; }}
  img {{ max-width:100%; border:1px solid #30363D; border-radius:8px; margin-top:10px; }}
  .badge {{ background:{badge_color}; color:white; padding:4px 10px; border-radius:12px; font-weight:bold; }}
  .reason {{ background:#161B22; border:1px solid #30363D; padding:8px; border-radius:6px; margin:10px auto; max-width:600px; font-size:12px; }}
  button {{ background:#1F6FEB; color:white; border:none; padding:10px 16px; border-radius:6px; font-family:monospace; margin:6px; cursor:pointer; }}
</style></head>
<body>
  <h2>ZEMALA_SSOT_V3 AUTO-COCKPIT</h2>
  <p>Contract: <span id="badge" class="badge">{badge_text}</span> | Blöcke: <b id="bcount">{len(blocks)}</b></p>
  <div id="reason" class="reason">{reason}</div>
  <div>
    <button onclick="forceView('/sigil.png')">Auto-Modus (Live AEVO)</button>
    <button style="background:#30363D" onclick="forceView('/sigil_raw.png')">Roh-Hash ansehen (4 Farben)</button>
  </div>
  <img id="sigil" src="/sigil.png" alt="11x11 Voxel Sigil">
<script>
  let lastCount = {len(blocks)};
  let lastStatus = "{is_gold}";
  let autoMode = true;
  function forceView(endpoint) {{
    autoMode = (endpoint === '/sigil.png');
    document.getElementById('sigil').src = endpoint + '?t=' + Date.now();
  }}
  setInterval(async () => {{
    try {{
      const res = await fetch('/status');
      const data = await res.json();
      document.getElementById('bcount').innerText = data.total_blocks;
      document.getElementById('reason').innerText = data.aevo_reason;
      const badge = document.getElementById('badge');
      badge.innerText = data.contract_verified ? 'GOLD (VERIFIZIERT)' : 'UNGEPRÜFT / WIDERSPRUCH';
      badge.style.background = data.contract_verified ? '#B8860B' : '#D9383A';
      if (autoMode && (data.total_blocks !== lastCount || String(data.contract_verified) !== lastStatus)) {{
        lastCount = data.total_blocks;
        lastStatus = String(data.contract_verified);
        document.getElementById('sigil').src = '/sigil.png?t=' + Date.now();
      }}
    }} catch (e) {{}}
  }}, 3470);
</script>
</body></html>""".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)

            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            err_body = json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), ZemalaCockpitHandler)
    print(f"[ZEMALA Auto-Cockpit] Active on port {PORT} with AEVO contract verification (3.47s cadence).")
    server.serve_forever()
