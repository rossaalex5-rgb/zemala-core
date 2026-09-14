import urllib.request
import urllib.error
import json
import os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY is not set.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
headers = {
    "Content-Type": "application/json"
}
body = {
    "contents": [{
        "parts": [{"text": "Diagnose Ping"}]
    }]
}

print(f"[*] Probing endpoint: {url.split('?')[0]} ...")

try:
    data_bytes = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(f"[SUCCESS] Status {resp.status}:", resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"\n[EVIDENZ CAPTURED] HTTP Error {e.code} ({e.reason}):")
    error_detail = e.read().decode("utf-8")
    print(error_detail)
except Exception as e:
    print(f"\n[ERROR] Non-HTTP Exception: {e}")
