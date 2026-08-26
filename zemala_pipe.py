import os
import hashlib
import sys
from discord_notifier import send_discord_notification

def process_and_dispatch(raw_message):
    normalized = raw_message.strip().lower()
    h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    
    payload_msg = f"Normalisiert & Gehasht:\nHash: {h[:12]}...\nInhalt: {normalized}"
    
    send_discord_notification(
        title="Krypto-Pipeline Verifizierung",
        message=payload_msg,
        status="SUCCESS",
        channel="secondary"
    )
    print(f"[*] Pipeline-Zyklus abgeschlossen. Hash: {h}")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Zemala Default State Initialized"
    process_and_dispatch(msg)
