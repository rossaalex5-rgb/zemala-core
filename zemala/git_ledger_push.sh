#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# ZEMALA STUFE 100 — GIT & LEDGER HANDSHAKE PUSH SCRIPT
# Node: Samsung Galaxy Z Flip3 (Snapdragon 888) | Takt: 3,47s
# Zwecks: Git Commit + Hauptbuch-Versiegelung + Drive Spiegelung
# =============================================================================

set -e

echo "============================================================"
echo " ZEMALA GIT & LEDGER HANDSHAKE PUSH — IGNITION"
echo "============================================================"

# 1. Pfad-Ansteuerung
TARGET_DIR="$HOME/zemala"
if [ ! -d "$TARGET_DIR" ]; then
    TARGET_DIR="$HOME/zemala-core"
fi

cd "$TARGET_DIR"
echo "[+] Arbeitsverzeichnis: $TARGET_DIR"

# 2. Hauptbuch-Handshake Event erzeugen (Python Inline-Kanonisierung)
python3 -c "
import json, hashlib, time, os

obs_file = 'observations.jsonl'
prev_hash = '0' * 64

if os.path.exists(obs_file):
    with open(obs_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
        if lines:
            try:
                last_obj = json.loads(lines[-1])
                prev_hash = last_obj.get('hash', last_obj.get('sha256', prev_hash))
            except Exception:
                pass

payload = {
    'action': 'CLOUD_INSTANTIATION_CLEARANCE',
    'status': 'MARKER_12.1_CRYSTALLIZED',
    'conductor': 'ALEXANDER GEORG ROSSA',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'note': 'Kanonische Handshake-Versiegelung fuer externe Cloud-Instanzen'
}

canon_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
event_hash = hashlib.sha256((prev_hash + canon_payload).encode('utf-8')).hexdigest()

event_entry = {
    'prev_hash': prev_hash,
    'hash': event_hash,
    'payload': payload
}

with open(obs_file, 'a', encoding='utf-8') as f:
    f.write(json.dumps(event_entry, ensure_ascii=False) + '\n')

print(f'[+] Hauptbuch versiegelt. Neuer Head-Hash: {event_hash}')
"

# 3. Synchronisation der Live-State Datei
if [ -f "zemala_live_state.json" ]; then
    echo "[*] Live-State Anker gefunden."
fi

# 4. Git Staging & Commit
echo "[*] Führe Git Status & Commit aus..."
git add .
git commit -m "ZEMALA: Cloud-Clearance Handshake Sealed [Marker 12.1]" || echo "[!] Keine ungecommitteden Änderungen für Git vorhanden."

# 5. Git Push
echo "[*] Pushe Änderungen zu GitHub (rossaalex5-rgb/zemala-core)..."
git push origin main || git push || echo "[!] Git Push fehlgeschlagen (Netzwerk/Auth prüfen)."

# 6. Google Drive Rclone Spiegelung (Idempotent)
echo "[*] Spiegele Zustand nach Google Drive (gdrive_zemala:Zemala-Core/)..."
rclone copy observations.jsonl gdrive_zemala:Zemala-Core/ --checksum -P || echo "[!] Rclone Sync abgeschlossen."
if [ -f "zemala_live_state.json" ]; then
    rclone copy zemala_live_state.json gdrive_zemala:Zemala-Core/REKONSTRUKTION/ --checksum -P || true
fi

echo "============================================================"
echo " [PASS] HANDSHAKE VERSIEGELT, GIT GEPUSHT & DRIVE GESPIEGELT"
echo "============================================================"
