import json, hashlib, time, urllib.request, urllib.error
PORT = 8080
TARGET_URL = f"http://127.0.0.1:{PORT}"
def canonicalize(obj):
    if obj is None or isinstance(obj, (int, float, str, bool)): return obj
    if isinstance(obj, list): return [canonicalize(x) for x in obj]
    if isinstance(obj, dict): return {k: canonicalize(obj[k]) for k in sorted(obj.keys())}
    return str(obj)
def compute_hash(payload):
    raw = json.dumps(canonicalize(payload), sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()
payload_data = {"action": "A2A_HELLO_HANDSHAKE", "sender": "OpenClaw_Armada_Node_01", "target": "ZEMALA_CORE_SNAPDRAGON_888", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "capabilities": ["MCP_RESOURCE_READ", "STATE_VERIFY"], "nonce": "ZE-8080-INIT-001"}
payload_hash = compute_hash(payload_data)
event = {"protocol": "A2A_V1", "type": "HANDSHAKE_REQUEST", "payload": payload_data, "payload_hash": payload_hash}
print(f"[+] Computed Canonical SHA-256: {payload_hash}")
req = urllib.request.Request(TARGET_URL, data=json.dumps(event).encode('utf-8'), headers={"Content-Type": "application/json", "Authorization": "Bearer ZEMALA_A2A_KEY_8080"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(f"[✔] RESPONSE ({resp.status}): {resp.read().decode('utf-8')}")
except Exception as e:
    print(f"[!] Error: {e}")
