#!/usr/bin/env python3
import sys
import json
import os
import datetime
import requests

ledger = os.path.expanduser("~/zemala-core/master_history.jsonl")
event_type = sys.argv[1] if len(sys.argv) > 1 else "SYSTEM"
action = sys.argv[2] if len(sys.argv) > 2 else "SEAL_CREATED"
source = sys.argv[3] if len(sys.argv) > 3 else "SmallThinker-3B-Ollama"
timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

entry = {"timestamp": timestamp, "type": event_type, "action": action, "source": source}
os.makedirs(os.path.dirname(ledger), exist_ok=True)
with open(ledger, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")

print(f"[+] Event '{event_type} {action}' erfolgreich in Ledger versiegelt.")

webhook_url = "https://discord.com/api/webhooks/1463047142473072721/0Gco0d7cSqpFq8OR_XSgF91zvzxw5YRPIIErht3WBCYN58-InLQ22w9eRv-5K3ASar1t"
payload = {"content": f"⚡ **ZEMALA-CORE EVENT** [`{event_type}`] `{action}` via `{source}` at `{timestamp}`"}
try:
    requests.post(webhook_url, json=payload, timeout=5)
except Exception:
    pass
