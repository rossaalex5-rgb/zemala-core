import os, json, urllib.request

PRIMARY_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
SECONDARY_WEBHOOK = "https://discord.com/api/webhooks/1463079162029019210/jHmfToQSAfWRzPDTwd78QiMHkchjcznk76Z1qfX1XcHpmQhsC5XcWiyX-RdRxb3SvJW9"

def send_discord_notification(title, message, status="SUCCESS", channel="primary"):
    webhook_url = SECONDARY_WEBHOOK if channel == "secondary" else PRIMARY_WEBHOOK
    if not webhook_url:
        print("[-] Kein Webhook für den gewählten Kanal gesetzt.")
        return
    color = 0x00FF00 if status == "SUCCESS" else 0xFF0000
    payload = {
        "embeds": [{
            "title": f"[ZEMALA CHAT KERNEL] {title}",
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
            print(f"[*] Chat-Nachricht an Discord gesendet: {response.status}")
    except Exception as e:
        print(f"[-] Fehler beim Senden an Discord: {e}")

if __name__ == "__main__":
    send_discord_notification(
        "Chat-Brücke Aktiviert", 
        "Der direkte Befehlskanal aus dem System ist nun scharf geschaltet.",
        channel="secondary"
    )
