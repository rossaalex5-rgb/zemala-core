import os
import json
import urllib.request

def send_discord_notification(commit_hash, commit_msg):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        print("[ZEMALA DISCORD] Kein Webhook konfiguriert. Logge lokal.")
        return

    payload = {
        "content": f"🚀 **[ZEMALA CORE] Stufe 100 verifiziert!**\n> Commit: `{commit_hash}` - {commit_msg}\n> System-Status: **Aktiv & Resonant**"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Zemala-Agent"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[ZEMALA DISCORD] Status-Post erfolgreich abgesetzt. Code: {response.getcode()}")
    except Exception as e:
        print(f"[ZEMALA DISCORD] Fehler beim Senden: {e}")

if __name__ == "__main__":
    send_discord_notification("209839b3df40", "Zemala Interoperability Protocol & Audit sync [Stufe 100]")
