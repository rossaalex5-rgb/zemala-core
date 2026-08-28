import os
import requests
import json
import sys

# --- ZEMALA COCKPIT ---
API_KEY = os.environ.get("YOUTUBE_API_KEY", "DEIN_KEY")
HANDLE = "lofowelt"

def check_status():
    if API_KEY == "DEIN_KEY" or len(API_KEY) < 10:
        print("\n[!] BURDE: YOUTUBE_API_KEY Umgebungsvariable nicht gesetzt.")
        return
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&forHandle={HANDLE}&key={API_KEY}"
    try:
        r = requests.get(url).json()
        if "error" in r:
            error = r["error"]
            print(f"\n[!] BLOCKADE ERKANNT (Code {error.get('code')})")
            print(f"Meldung: {error.get('message')}")
        elif "items" in r and len(r["items"]) > 0:
            title = r["items"][0]["snippet"]["title"]
            print(f"\n[2/2] VERBUNDEN: {title}")
            print("[!] Status: Stufe 100 erreicht. Das Feld ist offen.")
        else:
            print("\n[!] Keine Kanäle gefunden.")
    except Exception as e:
        print(f"\n[!] SYSTEM-REIBUNG: {e}")

if __name__ == "__main__":
    check_status()
