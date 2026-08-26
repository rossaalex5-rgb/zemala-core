import os, json, urllib.request

def send_discord_notification(title, message, status="SUCCESS"):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("[-] DISCORD_WEBHOOK_URL nicht gesetzt.")
        return
    color = 0x00FF00 if status == "SUCCESS" else 0xFF0000
    payload = {
        "embeds": [{
            "title": f"[ZEMALA KERNEL] {title}",
            "description": message,
            "color": color,
            "fields": [
                {"name": "Takt", "value": "3,47s", "inline": True},
                {"name": "Status", "value": status, "inline": True}
            ]
        }]
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ZemalaKernel/3.47"
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[*] Discord Notification gesendet: {response.status}")
    except Exception as e:
        print(f"[-] Fehler beim Senden an Discord: {e}")

if __name__ == "__main__":
    send_discord_notification(
        "Pipeline-Integration Aktiv", 
        "Der Discord-Notifier wurde erfolgreich in die Kern-Architektur eingebunden."
    )
