import os
import json
import hashlib
from datetime import datetime, timezone
from fetch_playlist import verify_and_get_uploads_id, fetch_and_normalize_playlist_items

LEDGER_PATH = "ledger/observations.jsonl"

def canonicalize_and_seal():
    print("[*] ZEMALA INGESTION: Starte Live-Abruf der Kondensationsplatten...")
    try:
        uploads_id = verify_and_get_uploads_id()
        raw_videos = fetch_and_normalize_playlist_items(uploads_id)
    except Exception as e:
        print(f"[!] FEHLER beim Abrufen der YouTube-Daten: {e}")
        return
    
    os.makedirs("ledger", exist_ok=True)
    
    events_written = 0
    previous_hash = "0" * 64
    
    # Letzten Hash aus bestehendem Ledger lesen für lückenlose Verkettung
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                try:
                    last_event = json.loads(lines[-1].strip())
                    previous_hash = last_event.get("hash", previous_hash)
                except json.JSONDecodeError:
                    pass

    with open(LEDGER_PATH, "a", encoding="utf-8") as ledger_file:
        for video in raw_videos:
            canonical_payload = {
                "source": "youtube",
                "channel_handle": "lofowelt",
                "video_id": video.get("video_id"),
                "title": video.get("title"),
                "description": video.get("description"),
                "published_at": video.get("published_at"),
                "observed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Deterministischer JSON-String (sortierte Schlüssel, ohne Whitespace-Rauschen)
            canonical_json = json.dumps(canonical_payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            
            # SHA-256 Hash mit vorherigem Hash verkettet
            hasher = hashlib.sha256()
            hasher.update((previous_hash + canonical_json).encode("utf-8"))
            current_hash = hasher.hexdigest()
            
            event = {
                "prev_hash": previous_hash,
                "hash": current_hash,
                "payload": canonical_payload
            }
            
            ledger_file.write(json.dumps(event, ensure_ascii=False) + "\n")
            previous_hash = current_hash
            events_written += 1

    print(f"[✓] LEDGER VERSIEGELT: {events_written} Beobachtungen erfolgreich in {LEDGER_PATH} geschrieben.")

if __name__ == "__main__":
    canonicalize_and_seal()
